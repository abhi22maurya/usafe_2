import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
from config import DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.graph_objects as go
import plotly.express as px
import logging
import traceback

class AnalyticsService:
    def __init__(self):
        self.db_config = DB_CONFIG
        logging.basicConfig(
            filename='logs/analytics.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.accuracy_metrics = {
            'incident_prediction': {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0},
            'resource_allocation': {'accuracy': 0.0, 'count': 0}
        }

    def _get_db_connection(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}\n{traceback.format_exc()}")
            raise

    def get_incident_analytics(self, time_range: str = '7d') -> Dict:
        """Get analytics for incidents with enhanced accuracy"""
        conn = None
        try:
            conn = self._get_db_connection()
            self.logger.info("Connected to database for incident analytics")
            
            # Validate time range
            valid_ranges = ['7d', '30d']
            if time_range not in valid_ranges:
                raise ValueError(f"Invalid time range. Must be one of: {valid_ranges}")
            
            # Calculate time range
            end_date = datetime.now()
            if time_range == '7d':
                start_date = end_date - timedelta(days=7)
            else:  # 30d
                start_date = end_date - timedelta(days=30)
            
            # Get incident data with validation
            df = pd.read_sql("""
                SELECT 
                    type,
                    severity,
                    EXTRACT(DOW FROM created_at) as day_of_week,
                    EXTRACT(HOUR FROM created_at) as hour_of_day,
                    COUNT(*) as count
                FROM incidents
                WHERE created_at BETWEEN %s AND %s
                GROUP BY type, severity, day_of_week, hour_of_day
            """, conn, params=(start_date, end_date))
            
            if df.empty:
                raise ValueError("No incident data found for the specified time range")
            
            # Validate data types
            if not all(df['count'].apply(lambda x: isinstance(x, (int, float)))):
                raise ValueError("Invalid count values in incident data")
            
            self.logger.info(f"Retrieved {len(df)} incident records")
            
            # Generate analytics with accuracy metrics
            analytics = {
                'total_incidents': int(df['count'].sum()),
                'by_type': self._get_incidents_by_type(df),
                'by_severity': self._get_incidents_by_severity(df),
                'by_time': self._get_incidents_by_time(df),
                'trends': self._get_incident_trends(df),
                'accuracy_metrics': self._calculate_incident_accuracy(df)
            }
            
            # Update accuracy metrics
            self._update_accuracy_metrics('incident_prediction', analytics)
            
            return analytics
        except Exception as e:
            self.logger.error(f"Error in get_incident_analytics: {str(e)}\n{traceback.format_exc()}")
            raise
        finally:
            if conn:
                conn.close()
                self.logger.info("Closed database connection")

    def _calculate_incident_accuracy(self, df):
        """Calculate accuracy metrics for incident predictions"""
        # Calculate prediction accuracy
        total = len(df)
        if total == 0:
            return {'accuracy': 0.0, 'count': 0}
            
        # Calculate accuracy based on historical patterns
        accuracy = (df.groupby(['type', 'severity'])['count'].sum() / total).mean()
        
        return {
            'accuracy': float(accuracy),
            'count': int(total),
            'confidence_interval': self._calculate_confidence_interval(accuracy, total)
        }

    def _calculate_confidence_interval(self, accuracy, n, confidence=0.95):
        """Calculate confidence interval for accuracy"""
        import scipy.stats
        z = scipy.stats.norm.ppf((1 + confidence) / 2)
        std_error = np.sqrt((accuracy * (1 - accuracy)) / n)
        margin_of_error = z * std_error
        return {
            'lower': float(accuracy - margin_of_error),
            'upper': float(accuracy + margin_of_error)
        }

    def _update_accuracy_metrics(self, metric_type, analytics):
        """Update accuracy metrics based on analytics"""
        if metric_type == 'incident_prediction':
            accuracy = analytics['accuracy_metrics']['accuracy']
            self.accuracy_metrics[metric_type]['accuracy'] = accuracy
            self.accuracy_metrics[metric_type]['count'] += 1
        
        self.logger.info(f"Updated accuracy metrics: {json.dumps(self.accuracy_metrics)}")

    def get_resource_analytics(self) -> Dict:
        """Get analytics for resources"""
        conn = None
        try:
            conn = self._get_db_connection()
            logging.info("Connected to database for resource analytics")
            
            # Get resource data
            df = pd.read_sql("""
                SELECT 
                    r.category,
                    r.quantity,
                    COUNT(ra.id) as allocation_count,
                    SUM(ra.quantity) as allocated_quantity
                FROM resources r
                LEFT JOIN resource_allocations ra ON r.id = ra.resource_id
                GROUP BY r.category, r.quantity
            """, conn)
            
            logging.info(f"Retrieved {len(df)} resource records")
            
            # Generate analytics
            analytics = {
                'total_resources': int(df['quantity'].sum()),
                'by_category': self._get_resources_by_category(df),
                'utilization': self._get_resource_utilization(df),
                'allocation_trends': self._get_allocation_trends(conn)
            }
            
            return analytics
        except Exception as e:
            logging.error(f"Error in get_resource_analytics: {str(e)}\n{traceback.format_exc()}")
            raise
        finally:
            if conn:
                conn.close()
                logging.info("Closed database connection")

    def get_response_analytics(self) -> Dict:
        """Get analytics for response teams"""
        conn = None
        try:
            conn = self._get_db_connection()
            logging.info("Connected to database for response analytics")
            
            # Get response team data
            df = pd.read_sql("""
                SELECT 
                    t.team_type,
                    COUNT(DISTINCT tm.id) as member_count,
                    COUNT(DISTINCT ta.id) as assignment_count,
                    AVG(EXTRACT(EPOCH FROM (ta.completed_at - ta.assigned_at))/60) as avg_response_time
                FROM response_teams t
                LEFT JOIN team_members tm ON t.id = tm.team_id
                LEFT JOIN team_assignments ta ON t.id = ta.team_id
                GROUP BY t.team_type
            """, conn)
            
            logging.info(f"Retrieved {len(df)} response team records")
            
            # Generate analytics
            analytics = {
                'total_teams': len(df),
                'by_type': self._get_teams_by_type(df),
                'response_times': self._get_response_times(df),
                'team_utilization': self._get_team_utilization(conn)
            }
            
            return analytics
        except Exception as e:
            logging.error(f"Error in get_response_analytics: {str(e)}\n{traceback.format_exc()}")
            raise
        finally:
            if conn:
                conn.close()
                logging.info("Closed database connection")

    def get_weather_analytics(self) -> Dict:
        """Get analytics for weather data"""
        conn = psycopg2.connect(**self.db_config)
        
        # Get weather data
        df = pd.read_sql("""
            SELECT 
                weather_condition,
                temperature,
                wind_speed,
                COUNT(*) as count
            FROM weather_data
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY weather_condition, temperature, wind_speed
        """, conn)
        
        # Generate analytics
        analytics = {
            'weather_patterns': self._get_weather_patterns(df),
            'temperature_trends': self._get_temperature_trends(df),
            'wind_patterns': self._get_wind_patterns(df)
        }
        
        conn.close()
        return analytics

    def _get_incidents_by_type(self, df: pd.DataFrame) -> Dict:
        """Get incident distribution by type"""
        type_counts = df.groupby('type')['count'].sum().to_dict()
        return {
            'data': type_counts,
            'chart': self._create_pie_chart(type_counts, 'Incidents by Type')
        }

    def _get_incidents_by_severity(self, df: pd.DataFrame) -> Dict:
        """Get incident distribution by severity"""
        severity_counts = df.groupby('severity')['count'].sum().to_dict()
        return {
            'data': severity_counts,
            'chart': self._create_bar_chart(severity_counts, 'Incidents by Severity')
        }

    def _get_incidents_by_time(self, df: pd.DataFrame) -> Dict:
        """Get incident distribution by time"""
        hourly_counts = df.groupby('hour_of_day')['count'].sum().to_dict()
        return {
            'data': hourly_counts,
            'chart': self._create_line_chart(hourly_counts, 'Incidents by Hour')
        }

    def _get_incident_trends(self, df: pd.DataFrame) -> Dict:
        """Get incident trends over time"""
        daily_counts = df.groupby('day_of_week')['count'].sum().to_dict()
        return {
            'data': daily_counts,
            'chart': self._create_line_chart(daily_counts, 'Daily Incident Trends')
        }

    def _get_resources_by_category(self, df: pd.DataFrame) -> Dict:
        """Get resource distribution by category"""
        category_data = df.groupby('category').agg({
            'quantity': 'sum',
            'allocation_count': 'sum',
            'allocated_quantity': 'sum'
        }).to_dict('index')
        return {
            'data': category_data,
            'chart': self._create_bar_chart(
                {k: v['quantity'] for k, v in category_data.items()},
                'Resources by Category'
            )
        }

    def _get_resource_utilization(self, df: pd.DataFrame) -> Dict:
        """Get resource utilization metrics"""
        utilization = df.groupby('category').apply(
            lambda x: (x['allocated_quantity'].sum() / x['quantity'].sum()) * 100
        ).to_dict()
        return {
            'data': utilization,
            'chart': self._create_bar_chart(utilization, 'Resource Utilization (%)')
        }

    def _get_allocation_trends(self, conn) -> Dict:
        """Get resource allocation trends"""
        df = pd.read_sql("""
            SELECT 
                DATE_TRUNC('day', allocated_at) as date,
                COUNT(*) as count
            FROM resource_allocations
            GROUP BY date
            ORDER BY date
        """, conn)
        return {
            'data': df.to_dict('records'),
            'chart': self._create_line_chart(
                dict(zip(df['date'], df['count'])),
                'Resource Allocation Trends'
            )
        }

    def _get_teams_by_type(self, df: pd.DataFrame) -> Dict:
        """Get team distribution by type"""
        team_data = df.to_dict('records')
        return {
            'data': team_data,
            'chart': self._create_bar_chart(
                {row['team_type']: row['member_count'] for row in team_data},
                'Team Members by Type'
            )
        }

    def _get_response_times(self, df: pd.DataFrame) -> Dict:
        """Get response time metrics"""
        response_times = df.groupby('team_type')['avg_response_time'].mean().to_dict()
        return {
            'data': response_times,
            'chart': self._create_bar_chart(response_times, 'Average Response Time (minutes)')
        }

    def _get_team_utilization(self, conn) -> Dict:
        """Get team utilization metrics"""
        df = pd.read_sql("""
            SELECT 
                team_type,
                COUNT(*) as total_assignments,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_assignments
            FROM team_assignments ta
            JOIN response_teams t ON ta.team_id = t.id
            GROUP BY team_type
        """, conn)
        utilization = df.apply(
            lambda x: (x['completed_assignments'] / x['total_assignments']) * 100,
            axis=1
        ).to_dict()
        return {
            'data': utilization,
            'chart': self._create_bar_chart(utilization, 'Team Utilization (%)')
        }

    def _get_weather_patterns(self, df: pd.DataFrame) -> Dict:
        """Get weather pattern analysis"""
        patterns = df.groupby('weather_condition')['count'].sum().to_dict()
        return {
            'data': patterns,
            'chart': self._create_pie_chart(patterns, 'Weather Patterns')
        }

    def _get_temperature_trends(self, df: pd.DataFrame) -> Dict:
        """Get temperature trend analysis"""
        temp_stats = df.groupby('temperature')['count'].sum().to_dict()
        return {
            'data': temp_stats,
            'chart': self._create_line_chart(temp_stats, 'Temperature Distribution')
        }

    def _get_wind_patterns(self, df: pd.DataFrame) -> Dict:
        """Get wind pattern analysis"""
        wind_stats = df.groupby('wind_speed')['count'].sum().to_dict()
        return {
            'data': wind_stats,
            'chart': self._create_line_chart(wind_stats, 'Wind Speed Distribution')
        }

    def _create_pie_chart(self, data: Dict, title: str) -> str:
        """Create a pie chart"""
        fig = go.Figure(data=[go.Pie(
            labels=list(data.keys()),
            values=list(data.values()),
            hole=.3
        )])
        fig.update_layout(title_text=title)
        return fig.to_html(full_html=False)

    def _create_bar_chart(self, data: Dict, title: str) -> str:
        """Create a bar chart"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values())
        )])
        fig.update_layout(title_text=title)
        return fig.to_html(full_html=False)

    def _create_line_chart(self, data: Dict, title: str) -> str:
        """Create a line chart"""
        fig = go.Figure(data=[go.Scatter(
            x=list(data.keys()),
            y=list(data.values()),
            mode='lines+markers'
        )])
        fig.update_layout(title_text=title)
        return fig.to_html(full_html=False) 