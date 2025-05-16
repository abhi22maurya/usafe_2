from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    # Simulated predictions for Uttarakhand
    predictions = [
        {
            'id': 1,
            'disasterType': 'Floods',
            'date': '2025-07-01',
            'probability': 35.0,
            'impactLevel': 'Moderate',
            'lastUpdated': '2025-05-02T12:00:00',
            'lat': 30.2456,
            'lng': 79.1234,
            'riskLevel': 'Moderate'
        },
        {
            'id': 2,
            'disasterType': 'Landslides',
            'date': '2025-07-01',
            'probability': 25.0,
            'impactLevel': 'Moderate',
            'lastUpdated': '2025-05-02T12:00:00',
            'lat': 30.3789,
            'lng': 79.2345,
            'riskLevel': 'Moderate'
        },
        {
            'id': 3,
            'disasterType': 'Earthquakes',
            'date': '2025-07-01',
            'probability': 15.0,
            'impactLevel': 'High',
            'lastUpdated': '2025-05-02T12:00:00',
            'lat': 30.1234,
            'lng': 79.3456,
            'riskLevel': 'High'
        },
        # Historical data
        {'id': 4, 'disasterType': 'Floods', 'date': '2020-07-01', 'probability': 28.0, 'impactLevel': 'Moderate', 'lastUpdated': '2020-07-01T12:00:00', 'lat': 30.2111, 'lng': 79.1567, 'riskLevel': 'Moderate'},
        {'id': 5, 'disasterType': 'Landslides', 'date': '2020-07-01', 'probability': 22.0, 'impactLevel': 'Low', 'lastUpdated': '2020-07-01T12:00:00', 'lat': 30.3222, 'lng': 79.2678, 'riskLevel': 'Low'},
        {'id': 6, 'disasterType': 'Earthquakes', 'date': '2020-07-01', 'probability': 12.0, 'impactLevel': 'Moderate', 'lastUpdated': '2020-07-01T12:00:00', 'lat': 30.1333, 'lng': 79.3789, 'riskLevel': 'Moderate'},
        
        {'id': 7, 'disasterType': 'Floods', 'date': '2021-07-01', 'probability': 30.0, 'impactLevel': 'Moderate', 'lastUpdated': '2021-07-01T12:00:00', 'lat': 30.2444, 'lng': 79.1890, 'riskLevel': 'Moderate'},
        {'id': 8, 'disasterType': 'Landslides', 'date': '2021-07-01', 'probability': 23.0, 'impactLevel': 'Moderate', 'lastUpdated': '2021-07-01T12:00:00', 'lat': 30.3555, 'lng': 79.2901, 'riskLevel': 'Moderate'},
        {'id': 9, 'disasterType': 'Earthquakes', 'date': '2021-07-01', 'probability': 13.0, 'impactLevel': 'Moderate', 'lastUpdated': '2021-07-01T12:00:00', 'lat': 30.1666, 'lng': 79.3012, 'riskLevel': 'Moderate'},
    ]
    return jsonify(predictions)

@app.route('/api/realtime-data', methods=['GET'])
def get_realtime_data():
    # Simulate real-time data
    data = {
        'weather': {
            'temperature': random.uniform(20, 30),
            'humidity': random.uniform(40, 90),
            'rainfall': random.uniform(0, 50)
        },
        'seismic': [
            {
                'time': '2025-05-02T10:30:00',
                'magnitude': random.uniform(1.0, 3.0),
                'depth': random.uniform(5, 15),
                'location': 'Uttarakhand'
            }
        ]
    }
    return jsonify(data)

@app.route('/api/community/partnerships', methods=['GET'])
def get_community_partnerships():
    # Dummy data for community partnerships
    partnerships = [
        {
            'id': 1,
            'name': 'Local NGO Alliance',
            'type': 'Community',
            'description': 'Collaboration with local NGOs for disaster preparedness workshops.',
            'contact': 'contact@localngo.org',
            'active': True
        },
        {
            'id': 2,
            'name': 'Uttarakhand Disaster Management Authority',
            'type': 'Authority',
            'description': 'Official partnership for real-time alert dissemination and resource coordination.',
            'contact': 'info@udma.gov.in',
            'active': True
        },
        {
            'id': 3,
            'name': 'Community Volunteer Network',
            'type': 'Community',
            'description': 'Network of trained volunteers for immediate disaster response.',
            'contact': 'volunteer@cvn.org',
            'active': True
        }
    ]
    return jsonify(partnerships)

@app.route('/api/community/challenges', methods=['GET'])
def get_community_challenges():
    # Dummy data for community challenges
    challenges = [
        {
            'id': 1,
            'title': 'Disaster Preparedness Quiz',
            'description': 'Test your knowledge on disaster preparedness and earn points.',
            'start_date': '2025-05-01',
            'end_date': '2025-05-15',
            'reward': 'Certificate of Preparedness',
            'participants': 143
        },
        {
            'id': 2,
            'title': 'Emergency Kit Assembly Challenge',
            'description': 'Assemble an emergency kit and share a photo to earn points.',
            'start_date': '2025-05-10',
            'end_date': '2025-05-24',
            'reward': 'Recognition from Local Authorities',
            'participants': 87
        },
        {
            'id': 3,
            'title': 'Community Drill Participation',
            'description': 'Participate in a local disaster drill to prepare for emergencies.',
            'start_date': '2025-05-20',
            'end_date': '2025-05-27',
            'reward': 'Community Hero Badge',
            'participants': 54
        }
    ]
    return jsonify(challenges)

@app.route('/api/gamification/leaderboard', methods=['GET'])
def get_leaderboard():
    # Dummy data for leaderboard
    leaderboard = [
        {'id': 1, 'username': 'SafetyStar', 'points': 1250, 'rank': 1, 'badges': ['Preparedness Pro', 'Community Hero']},
        {'id': 2, 'username': 'DisasterDefender', 'points': 980, 'rank': 2, 'badges': ['Quick Responder', 'Safety Advocate']},
        {'id': 3, 'username': 'AlertAce', 'points': 750, 'rank': 3, 'badges': ['Preparedness Pro']},
        {'id': 4, 'username': 'RescueRanger', 'points': 620, 'rank': 4, 'badges': ['Community Hero']},
        {'id': 5, 'username': 'EmergencyExpert', 'points': 510, 'rank': 5, 'badges': ['Safety Advocate']}
    ]
    return jsonify(leaderboard)

@app.route('/api/gamification/user/<int:user_id>', methods=['GET'])
def get_user_gamification(user_id):
    # Dummy data for user gamification stats
    user_data = {
        'id': user_id,
        'username': 'User' + str(user_id),
        'points': 320,
        'rank': 12,
        'badges': ['Preparedness Pro', 'Quick Responder'],
        'challenges_completed': 3,
        'rewards': ['Certificate of Participation'],
        'next_badge_progress': {'name': 'Community Hero', 'progress': 64}
    }
    return jsonify(user_data)

@app.route('/api/gamification/badges', methods=['GET'])
def get_available_badges():
    # Dummy data for available badges
    badges = [
        {'id': 1, 'name': 'Preparedness Pro', 'description': 'Completed basic disaster preparedness training.', 'icon': 'preparedness-icon', 'criteria': 'Complete 2 preparedness challenges'},
        {'id': 2, 'name': 'Quick Responder', 'description': 'Responded to an alert or incident within 10 minutes.', 'icon': 'responder-icon', 'criteria': 'Respond to 3 alerts quickly'},
        {'id': 3, 'name': 'Community Hero', 'description': 'Participated in community disaster drills or real incidents.', 'icon': 'hero-icon', 'criteria': 'Participate in 2 community events'},
        {'id': 4, 'name': 'Safety Advocate', 'description': 'Shared safety information with others in the community.', 'icon': 'advocate-icon', 'criteria': 'Share 5 safety tips or alerts'}
    ]
    return jsonify(badges)

if __name__ == '__main__':
    print("Starting simple Flask app on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=True)
