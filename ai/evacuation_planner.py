from typing import Dict, List, Optional
import json
import os
from config import DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor
import networkx as nx
import numpy as np
from geopy.distance import geodesic

class EvacuationPlanner:
    def __init__(self):
        self.db_config = DB_CONFIG
        self._init_database()
        self.road_network = nx.Graph()

    def _init_database(self):
        """Initialize database tables for evacuation planning"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        # Create shelters table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shelters (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                capacity INTEGER NOT NULL,
                current_occupancy INTEGER DEFAULT 0,
                facilities TEXT[],
                status VARCHAR(20) DEFAULT 'available'
            )
        """)
        
        # Create evacuation zones table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evacuation_zones (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                polygon_coordinates JSONB NOT NULL,
                population INTEGER NOT NULL,
                risk_level VARCHAR(20) NOT NULL
            )
        """)
        
        # Create evacuation routes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evacuation_routes (
                id SERIAL PRIMARY KEY,
                zone_id INTEGER REFERENCES evacuation_zones(id),
                shelter_id INTEGER REFERENCES shelters(id),
                route_coordinates JSONB NOT NULL,
                distance FLOAT NOT NULL,
                estimated_time INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()

    def add_shelter(self, name: str, latitude: float, longitude: float, 
                   capacity: int, facilities: List[str]) -> Dict:
        """Add a new evacuation shelter"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO shelters (name, latitude, longitude, capacity, facilities)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (name, latitude, longitude, capacity, facilities))
        
        shelter = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(shelter)

    def add_evacuation_zone(self, name: str, polygon_coordinates: List[Dict], 
                          population: int, risk_level: str) -> Dict:
        """Add a new evacuation zone"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO evacuation_zones (name, polygon_coordinates, population, risk_level)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (name, json.dumps(polygon_coordinates), population, risk_level))
        
        zone = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(zone)

    def plan_evacuation_route(self, zone_id: int, shelter_id: int) -> Dict:
        """Plan evacuation route from zone to shelter"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get zone and shelter coordinates
        cur.execute("""
            SELECT z.polygon_coordinates, s.latitude, s.longitude
            FROM evacuation_zones z, shelters s
            WHERE z.id = %s AND s.id = %s
        """, (zone_id, shelter_id))
        
        result = cur.fetchone()
        if not result:
            return {"error": "Zone or shelter not found"}
        
        zone_coords = json.loads(result['polygon_coordinates'])
        shelter_coords = (result['latitude'], result['longitude'])
        
        # Calculate route (simplified version - in reality would use road network)
        route_coords = self._calculate_route(zone_coords, shelter_coords)
        distance = self._calculate_distance(route_coords)
        estimated_time = self._estimate_evacuation_time(distance, zone_id)
        
        # Save route
        cur.execute("""
            INSERT INTO evacuation_routes (zone_id, shelter_id, route_coordinates, 
                                        distance, estimated_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (zone_id, shelter_id, json.dumps(route_coords), distance, estimated_time))
        
        route = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(route)

    def get_available_shelters(self, capacity_needed: int) -> List[Dict]:
        """Get available shelters with sufficient capacity"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM shelters
            WHERE status = 'available'
            AND (capacity - current_occupancy) >= %s
        """, (capacity_needed,))
        
        shelters = cur.fetchall()
        
        cur.close()
        conn.close()
        return [dict(shelter) for shelter in shelters]

    def update_shelter_occupancy(self, shelter_id: int, occupancy_change: int) -> Dict:
        """Update shelter occupancy"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            UPDATE shelters
            SET current_occupancy = current_occupancy + %s
            WHERE id = %s
            RETURNING *
        """, (occupancy_change, shelter_id))
        
        shelter = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(shelter)

    def get_evacuation_plan(self, zone_id: int) -> Dict:
        """Get complete evacuation plan for a zone"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get zone details
        cur.execute("""
            SELECT * FROM evacuation_zones
            WHERE id = %s
        """, (zone_id,))
        
        zone = cur.fetchone()
        
        # Get assigned routes
        cur.execute("""
            SELECT r.*, s.name as shelter_name, s.capacity, s.current_occupancy
            FROM evacuation_routes r
            JOIN shelters s ON r.shelter_id = s.id
            WHERE r.zone_id = %s AND r.status = 'active'
        """, (zone_id,))
        
        routes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        result = dict(zone)
        result['routes'] = [dict(route) for route in routes]
        return result

    def _calculate_route(self, zone_coords: List[Dict], shelter_coords: tuple) -> List[Dict]:
        """Calculate evacuation route (simplified version)"""
        # In reality, this would use a proper routing algorithm with road network
        # This is a simplified version that creates a direct route
        route = []
        for coord in zone_coords:
            route.append({
                'latitude': coord['latitude'],
                'longitude': coord['longitude']
            })
        route.append({
            'latitude': shelter_coords[0],
            'longitude': shelter_coords[1]
        })
        return route

    def _calculate_distance(self, route_coords: List[Dict]) -> float:
        """Calculate total route distance"""
        total_distance = 0
        for i in range(len(route_coords) - 1):
            point1 = (route_coords[i]['latitude'], route_coords[i]['longitude'])
            point2 = (route_coords[i+1]['latitude'], route_coords[i+1]['longitude'])
            total_distance += geodesic(point1, point2).kilometers
        return total_distance

    def _estimate_evacuation_time(self, distance: float, zone_id: int) -> int:
        """Estimate evacuation time based on distance and population"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT population FROM evacuation_zones
            WHERE id = %s
        """, (zone_id,))
        
        population = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        # Simplified estimation (in minutes)
        # Base time + time per kilometer + time per person
        base_time = 30  # minutes
        time_per_km = 2  # minutes
        time_per_person = 0.1  # minutes
        
        return int(base_time + (distance * time_per_km) + (population * time_per_person)) 