# Uttarakhand Safe

A comprehensive disaster management platform designed for the Uttarakhand region to enhance preparedness, response, and recovery during natural disasters.

## Overview

Uttarakhand Safe is a web-based platform aimed at providing real-time disaster alerts, community engagement features, AI-driven risk assessments, and recovery support to residents and authorities in Uttarakhand. The platform integrates various technologies to ensure accessibility, multilingual support, and efficient resource management.

## Features

### Latest Additions (2025)
- **Assistance Chatbot**: 24/7 Groq-powered AI chatbot for disaster queries and guidance.
- **Resource Management Dashboard**: Map and analytics for tracking relief resources (food, water, shelter, medical) across locations.
- **Recovery Support Dashboard**: Aid schemes, help requests, mental health, and analytics in a modern, accessible UI.
- **UI Modernization**: Glassmorphism, icons, accessibility, and mobile responsiveness across all dashboards.
- **API & AI Integrations**: Groq for chatbot and analysis, OpenRouteService for SafeRoute, extensible for real-time data APIs.


### 1. Disaster Alert System
- **Real-Time Alerts**: Immediate notifications for floods, landslides, and earthquakes
- **Push Notifications**: Automatic alerts to keep users informed
- **Accessibility**: ARIA labels and keyboard navigation support

### 2. Risk Assessment
- **Personalized Analysis**: Location-based risk assessment
- **Safety Recommendations**: Tailored safety measures during disasters
- **AI-Powered**: Automated risk analysis and suggestions

### 3. Community Engagement
- **Disaster Reports**: Share and view disaster experiences
- **AI Analysis**: Automated alerts to response teams
- **Gamification System**: Earn points and badges for participation
- **Location Tracking**: Post with specific locations
- **Disaster Types**: Categorize reports by disaster type

### 4. Emergency Resources
- **Emergency Contacts**: Quick access to critical numbers
- **Resource Tracking**: Manage disaster relief resources
- **Volunteer System**: Register and coordinate volunteers

### 5. Navigation and Safety

---

## Running the Application

You need two terminals: one for the backend (FastAPI) and one for the frontend (React).

### Backend (FastAPI)
From the project root:
```sh
source myenv/bin/activate
python backend/app.py
```
The backend will run at: http://localhost:8050

### Frontend (React)
In a new terminal:
```sh
cd frontend
npm start
```
The frontend will run at: http://localhost:3000

Make sure both are running for full functionality.

- **SafeRoute System**: AI-powered evacuation routes
- **Travel Options**: Multiple modes of evacuation (car, walk, bike)
- **Real-Time Updates**: Traffic and hazard information
- **Safe Zones**: Platform-recommended evacuation areas

### 6. Recovery Support
- **Post-Disaster Resources**: Information for rebuilding
- **Government Schemes**: Access to aid and support programs
- **Rehabilitation Guide**: Step-by-step recovery assistance

### 7. Analytics and Visualization
- **Data Visualization**: Interactive charts for disaster trends
- **Historical Analysis**: 2020-2025 disaster data
- **Regional Maps**: Risk assessment by location
- **Prediction Models**: AI-driven disaster predictions

### 8. User Interface
- **Multilingual Support**: English and Hindi options
- **Responsive Design**: Works on all devices
- **Accessibility Features**: Keyboard navigation and screen reader support

### 9. Authority Tools
- **Dashboard Analytics**: Comprehensive disaster data
- **Community Insights**: Track community reports and trends
- **Resource Management**: Monitor and allocate resources
- **Response Coordination**: Real-time team monitoring

### 10. Assistance System
- **24/7 Chatbot**: Instant disaster-related queries
- **Evacuation Guidance**: Safety protocols and procedures
- **Emergency Support**: Immediate assistance for crises

## Tech Stack

### Frontend
- **React.js**: For building a dynamic and responsive user interface.
- **Material-UI**: For pre-built components and styling.
- **Recharts**: For data visualization in dashboards.
- **React-Leaflet**: For interactive maps in visualization.
- **Framer Motion**: For animations and transitions.

### Backend
- **Flask (Python)**: Lightweight framework for API endpoints and server-side logic.
- **WebSocket/Firebase**: Planned integration for real-time notifications.

### APIs and Integrations
- **Geolocation API**: For detecting user location.
- **Weather and Seismic APIs**: Planned for real-time disaster data.

## File Structure

```
uttarakhand-safe/
│
├── frontend/                    # React.js frontend codebase
│   ├── public/                  # Static assets and index.html
│   │   ├── index.html          # Main HTML file
│   │   └── favicon.ico         # Favicon
│   │
│   └── src/                     # Source code
│       ├── components/          # Reusable UI components
│       │   ├── AlertForm.js              # Form for users to report alerts
│       │   ├── AlertNotifications.js     # Real-time disaster alerts
│       │   ├── AssistanceChatbot.js      # Chatbot for immediate assistance
│       │   ├── AuthorityDashboard.js     # Analytics dashboard for authorities
│       │   ├── CommunityPage.js          # Community engagement with gamification
│       │   ├── EmergencyContacts.js      # Critical contact numbers
│       │   ├── PersonalizedRiskAssessment.js  # AI-driven risk analysis
│       │   ├── RecoverySupport.js        # Post-disaster recovery resources
│       │   ├── ResourceManagement.js     # Disaster relief resource tracking
│       │   ├── SafeRoute.js              # AI-powered evacuation navigation
│       │   ├── VisualizationDashboard.js # Disaster prediction visualization
│       │   └── VolunteerRegistration.js  # Volunteer registration form
│       │
│       ├── context/             # React contexts for state management
│       │   └── LanguageContext.js  # Multilingual support context
│       │
│       ├── App.js               # Main app component with routing
│       ├── Layout.js            # Layout component for consistent UI
│       ├── theme.js             # Material-UI theme configuration
│       └── index.js             # Entry point for React app
│
├── app.py                       # Flask backend application
├── requirements.txt             # Python dependencies for backend
└── README.md                    # Project documentation
```

## Installation and Setup

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- npm (comes with Node.js)
- pip (comes with Python)

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
4. The application will be available at `http://localhost:3000`

### Backend Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   python backend/app.py
   ```
3. The API will be available at `http://localhost:8000`

### Running the Application
1. Ensure both frontend and backend servers are running
2. Access the application at `http://localhost:3000`
3. The application will automatically connect to the backend API

### Development Notes
- The frontend uses React with Material-UI for the UI components
- The backend uses FastAPI for RESTful API endpoints
- CORS is enabled for cross-origin requests
- The application is designed to be responsive and accessible

## Future Enhancements
- Integration with real-time weather and seismic APIs for accurate predictions.
- Mobile application development for wider accessibility.
- Advanced AI models for more precise risk assessments.
- Expansion to cover more regions beyond Uttarakhand.

## Contributing
We welcome contributions from the community. Please feel free to submit pull requests or open issues for bugs and feature requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
