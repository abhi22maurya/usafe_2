from datetime import datetime
import json
import os
from typing import Dict, List, Optional
from config import DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

class ResourceManager:
    def __init__(self):
        self.db_config = DB_CONFIG
        self._init_database()

    def _init_database(self):
        """Initialize database tables for resource management"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        # Create resources table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL,
                location VARCHAR(100) NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create resource requests table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resource_requests (
                id SERIAL PRIMARY KEY,
                resource_id INTEGER REFERENCES resources(id),
                requester VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                priority VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fulfilled_at TIMESTAMP
            )
        """)
        
        # Create resource allocations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resource_allocations (
                id SERIAL PRIMARY KEY,
                request_id INTEGER REFERENCES resource_requests(id),
                resource_id INTEGER REFERENCES resources(id),
                quantity INTEGER NOT NULL,
                allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()

    def add_resource(self, name: str, category: str, quantity: int, location: str) -> Dict:
        """Add a new resource to the inventory"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO resources (name, category, quantity, location)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (name, category, quantity, location))
        
        resource = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(resource)

    def update_resource(self, resource_id: int, quantity: int) -> Dict:
        """Update resource quantity"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            UPDATE resources
            SET quantity = %s, last_updated = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, (quantity, resource_id))
        
        resource = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(resource)

    def request_resources(self, resource_id: int, requester: str, quantity: int, priority: str) -> Dict:
        """Create a new resource request"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO resource_requests (resource_id, requester, quantity, priority)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (resource_id, requester, quantity, priority))
        
        request = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(request)

    def allocate_resources(self, request_id: int) -> Dict:
        """Allocate resources for a request"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get request details
        cur.execute("""
            SELECT r.*, res.quantity as available_quantity
            FROM resource_requests r
            JOIN resources res ON r.resource_id = res.id
            WHERE r.id = %s
        """, (request_id,))
        
        request = cur.fetchone()
        
        if not request:
            return {"error": "Request not found"}
        
        if request['quantity'] > request['available_quantity']:
            return {"error": "Insufficient resources available"}
        
        # Create allocation
        cur.execute("""
            INSERT INTO resource_allocations (request_id, resource_id, quantity)
            VALUES (%s, %s, %s)
            RETURNING *
        """, (request_id, request['resource_id'], request['quantity']))
        
        allocation = cur.fetchone()
        
        # Update resource quantity
        cur.execute("""
            UPDATE resources
            SET quantity = quantity - %s
            WHERE id = %s
        """, (request['quantity'], request['resource_id']))
        
        # Update request status
        cur.execute("""
            UPDATE resource_requests
            SET status = 'fulfilled', fulfilled_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (request_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        return dict(allocation)

    def get_resource_inventory(self) -> List[Dict]:
        """Get current resource inventory"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM resources")
        resources = cur.fetchall()
        
        cur.close()
        conn.close()
        return [dict(resource) for resource in resources]

    def get_pending_requests(self) -> List[Dict]:
        """Get all pending resource requests"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT r.*, res.name as resource_name
            FROM resource_requests r
            JOIN resources res ON r.resource_id = res.id
            WHERE r.status = 'pending'
        """)
        
        requests = cur.fetchall()
        
        cur.close()
        conn.close()
        return [dict(request) for request in requests]

    def get_resource_utilization(self) -> Dict:
        """Get resource utilization statistics"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                category,
                SUM(quantity) as total_quantity,
                COUNT(*) as resource_count
            FROM resources
            GROUP BY category
        """)
        
        utilization = cur.fetchall()
        
        cur.close()
        conn.close()
        return {
            'by_category': [dict(stat) for stat in utilization],
            'total_resources': sum(stat['total_quantity'] for stat in utilization)
        } 