from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from config import DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

class ResponseTeamManager:
    def __init__(self):
        self.db_config = DB_CONFIG
        self._init_database()

    def _init_database(self):
        """Initialize database tables for response team management"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        
        # Create teams table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS response_teams (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                team_type VARCHAR(50) NOT NULL,
                location VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'available',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create team members table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES response_teams(id),
                name VARCHAR(100) NOT NULL,
                role VARCHAR(50) NOT NULL,
                contact VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'available'
            )
        """)
        
        # Create team assignments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_assignments (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES response_teams(id),
                incident_id VARCHAR(50) NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                completed_at TIMESTAMP
            )
        """)
        
        # Create team locations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_locations (
                id SERIAL PRIMARY KEY,
                team_id INTEGER REFERENCES response_teams(id),
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()

    def create_team(self, name: str, team_type: str, location: str) -> Dict:
        """Create a new response team"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO response_teams (name, team_type, location)
            VALUES (%s, %s, %s)
            RETURNING *
        """, (name, team_type, location))
        
        team = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(team)

    def add_team_member(self, team_id: int, name: str, role: str, contact: str) -> Dict:
        """Add a member to a response team"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO team_members (team_id, name, role, contact)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (team_id, name, role, contact))
        
        member = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(member)

    def assign_team(self, team_id: int, incident_id: str) -> Dict:
        """Assign a team to an incident"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Update team status
        cur.execute("""
            UPDATE response_teams
            SET status = 'assigned'
            WHERE id = %s
        """, (team_id,))
        
        # Create assignment
        cur.execute("""
            INSERT INTO team_assignments (team_id, incident_id)
            VALUES (%s, %s)
            RETURNING *
        """, (team_id, incident_id))
        
        assignment = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(assignment)

    def update_team_location(self, team_id: int, latitude: float, longitude: float) -> Dict:
        """Update team's current location"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO team_locations (team_id, latitude, longitude)
            VALUES (%s, %s, %s)
            RETURNING *
        """, (team_id, latitude, longitude))
        
        location = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(location)

    def get_team_status(self, team_id: int) -> Dict:
        """Get current status of a team"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get team details
        cur.execute("""
            SELECT t.*, 
                   COUNT(tm.id) as member_count,
                   tl.latitude, tl.longitude
            FROM response_teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN team_locations tl ON t.id = tl.team_id
            WHERE t.id = %s
            GROUP BY t.id, tl.latitude, tl.longitude
        """, (team_id,))
        
        team = cur.fetchone()
        
        # Get team members
        cur.execute("""
            SELECT * FROM team_members
            WHERE team_id = %s
        """, (team_id,))
        
        members = cur.fetchall()
        
        cur.close()
        conn.close()
        
        result = dict(team)
        result['members'] = [dict(member) for member in members]
        return result

    def get_available_teams(self) -> List[Dict]:
        """Get all available response teams"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT t.*, 
                   COUNT(tm.id) as member_count,
                   tl.latitude, tl.longitude
            FROM response_teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN team_locations tl ON t.id = tl.team_id
            WHERE t.status = 'available'
            GROUP BY t.id, tl.latitude, tl.longitude
        """)
        
        teams = cur.fetchall()
        
        cur.close()
        conn.close()
        return [dict(team) for team in teams]

    def complete_assignment(self, assignment_id: int) -> Dict:
        """Mark a team assignment as completed"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get assignment details
        cur.execute("""
            SELECT * FROM team_assignments
            WHERE id = %s
        """, (assignment_id,))
        
        assignment = cur.fetchone()
        
        if not assignment:
            return {"error": "Assignment not found"}
        
        # Update assignment status
        cur.execute("""
            UPDATE team_assignments
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """, (assignment_id,))
        
        updated_assignment = cur.fetchone()
        
        # Update team status
        cur.execute("""
            UPDATE response_teams
            SET status = 'available'
            WHERE id = %s
        """, (assignment['team_id'],))
        
        conn.commit()
        cur.close()
        conn.close()
        return dict(updated_assignment) 