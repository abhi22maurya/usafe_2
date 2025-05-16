import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, onSnapshot } from 'firebase/firestore';
import { config } from '../config/firebase';

// Initialize Firebase
const app = initializeApp(config);
const db = getFirestore(app);

const Map3D = () => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [reports, setReports] = useState([]);
  const [riskData, setRiskData] = useState([]);

  useEffect(() => {
    if (!map.current) {
      mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;
      
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/satellite-v9',
        center: [79.0193, 30.0668], // Uttarakhand coordinates
        zoom: 7,
        pitch: 45,
        bearing: -30
      });

      // Add 3D terrain
      map.current.on('load', () => {
        map.current.addSource('mapbox-dem', {
          type: 'raster-dem',
          url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
          tileSize: 512,
          maxzoom: 14
        });

        map.current.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });
        
        // Add sky layer
        map.current.addLayer({
          id: 'sky',
          type: 'sky',
          paint: {
            'sky-type': 'atmosphere',
            'sky-atmosphere-sun': [0.0, 0.0],
            'sky-atmosphere-sun-intensity': 15
          }
        });
      });

      // Listen for reports from Firebase
      const reportsRef = collection(db, 'reports');
      const unsubscribe = onSnapshot(reportsRef, (snapshot) => {
        const newReports = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        setReports(newReports);
        updateRiskHeatmap(newReports);
      });

      return () => {
        unsubscribe();
        if (map.current) {
          map.current.remove();
        }
      };
    }
  }, []);

  const updateRiskHeatmap = (reports) => {
    // Calculate risk scores based on report density and severity
    const riskPoints = reports.map(report => ({
      type: 'Feature',
      properties: {
        risk: calculateRiskScore(report)
      },
      geometry: {
        type: 'Point',
        coordinates: [report.longitude, report.latitude]
      }
    }));

    setRiskData(riskPoints);

    if (map.current) {
      // Update heatmap layer
      if (map.current.getSource('risk-heatmap')) {
        map.current.getSource('risk-heatmap').setData({
          type: 'FeatureCollection',
          features: riskPoints
        });
      } else {
        map.current.addSource('risk-heatmap', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: riskPoints
          }
        });

        map.current.addLayer({
          id: 'risk-heatmap',
          type: 'heatmap',
          source: 'risk-heatmap',
          paint: {
            'heatmap-weight': ['get', 'risk'],
            'heatmap-intensity': 1,
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0, 0, 255, 0)',
              0.2, 'rgba(0, 0, 255, 0.5)',
              0.4, 'rgba(0, 255, 0, 0.5)',
              0.6, 'rgba(255, 255, 0, 0.5)',
              0.8, 'rgba(255, 126, 0, 0.5)',
              1, 'rgba(255, 0, 0, 0.5)'
            ],
            'heatmap-radius': 30,
            'heatmap-opacity': 0.8
          }
        });
      }
    }
  };

  const calculateRiskScore = (report) => {
    // Simple risk calculation based on report type and timestamp
    const severityWeights = {
      'Medical Emergency': 1.0,
      'Natural Disaster': 0.8,
      'Accident': 0.6,
      'Other': 0.4
    };

    const timeDecay = Math.max(0, 1 - (Date.now() - report.timestamp) / (24 * 60 * 60 * 1000));
    return severityWeights[report.type] * timeDecay;
  };

  return (
    <div className="map-container">
      <div ref={mapContainer} className="map" />
      <div className="map-overlay">
        <h3>Disaster Reports</h3>
        <div className="reports-list">
          {reports.map(report => (
            <div key={report.id} className="report-item">
              <h4>{report.type}</h4>
              <p>{report.description}</p>
              <small>{new Date(report.timestamp).toLocaleString()}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Map3D; 