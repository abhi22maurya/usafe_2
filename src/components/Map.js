import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import firebase from 'firebase/app';
import 'firebase/database';

mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';

const Map = () => {
  const mapContainer = useRef(null);

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [79.5, 30.5], // Uttarakhand center
      zoom: 7,
      pitch: 45, // 3D view
      bearing: -17.6,
    });

    map.on('load', () => {
      map.addSource('disasters', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      map.addLayer({
        id: 'disaster-heatmap',
        type: 'heatmap',
        source: 'disasters',
        maxzoom: 15,
        paint: {
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(0, 0, 255, 0)',
            0.5, 'yellow',
            1, 'red',
          ],
        },
      });

      // Load real-time reports
      firebase.database().ref('reports').on('value', (snapshot) => {
        const features = [];
        snapshot.forEach((child) => {
          const { coordinates, type } = child.val();
          features.push({
            type: 'Feature',
            geometry: { type: 'Point', coordinates },
            properties: { type },
          });
        });
        map.getSource('disasters').setData({
          type: 'FeatureCollection',
          features,
        });
      });

      // Add 3D terrain
      map.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.terrain-rgb',
      });
      map.addLayer({
        id: 'terrain-data',
        type: 'hillshade',
        source: 'mapbox-dem',
      });

      // Add click to report disaster
      map.on('click', (e) => {
        firebase.database().ref('reports').push({
          type: 'landslide',
          coordinates: [e.lngLat.lng, e.lngLat.lat],
          timestamp: Date.now(),
        });
      });
    });

    return () => map.remove();
  }, []);

  return <div ref={mapContainer} id="map" />;
};

export default Map;