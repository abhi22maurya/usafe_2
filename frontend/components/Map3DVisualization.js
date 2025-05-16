import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const Map3DVisualization = () => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const scene = useRef(null);
  const camera = useRef(null);
  const renderer = useRef(null);
  const buildings = useRef([]);

  useEffect(() => {
    if (!map.current) {
      mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;
      
      // Initialize Mapbox map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/satellite-v9',
        center: [79.0193, 30.0668], // Uttarakhand coordinates
        zoom: 15,
        pitch: 60,
        bearing: -30
      });

      // Initialize Three.js scene
      scene.current = new THREE.Scene();
      camera.current = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      renderer.current = new THREE.WebGLRenderer({ alpha: true });
      renderer.current.setSize(window.innerWidth, window.innerHeight);
      document.getElementById('three-container').appendChild(renderer.current.domElement);

      // Add ambient light
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      scene.current.add(ambientLight);

      // Add directional light
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(1, 1, 1);
      scene.current.add(directionalLight);

      // Load terrain data
      loadTerrain();

      // Load building models
      loadBuildings();

      // Handle window resize
      window.addEventListener('resize', handleResize);

      // Start animation loop
      animate();

      return () => {
        window.removeEventListener('resize', handleResize);
        if (map.current) {
          map.current.remove();
        }
        if (renderer.current) {
          renderer.current.dispose();
        }
      };
    }
  }, []);

  const loadTerrain = async () => {
    try {
      // Fetch elevation data from Mapbox
      const response = await fetch(
        `https://api.mapbox.com/v4/mapbox.terrain-rgb/tilequery/${map.current.getCenter().lng},${map.current.getCenter().lat}.json?access_token=${mapboxgl.accessToken}`
      );
      const data = await response.json();

      // Create terrain geometry
      const geometry = new THREE.PlaneGeometry(1000, 1000, 100, 100);
      const material = new THREE.MeshStandardMaterial({
        color: 0x3a5f0b,
        wireframe: false,
        flatShading: true
      });

      // Apply elevation data to vertices
      const vertices = geometry.attributes.position.array;
      for (let i = 0; i < vertices.length; i += 3) {
        const x = vertices[i];
        const z = vertices[i + 2];
        const elevation = getElevation(x, z, data);
        vertices[i + 1] = elevation * 10; // Scale elevation for better visibility
      }

      geometry.computeVertexNormals();
      const terrain = new THREE.Mesh(geometry, material);
      terrain.rotation.x = -Math.PI / 2;
      scene.current.add(terrain);
    } catch (error) {
      console.error('Error loading terrain:', error);
    }
  };

  const loadBuildings = async () => {
    try {
      const loader = new GLTFLoader();
      
      // Load building models
      const buildingModels = [
        { url: '/models/emergency_center.glb', position: [0, 0, 0] },
        { url: '/models/hospital.glb', position: [50, 0, 50] },
        { url: '/models/shelter.glb', position: [-50, 0, -50] }
      ];

      for (const model of buildingModels) {
        loader.load(
          model.url,
          (gltf) => {
            const building = gltf.scene;
            building.position.set(...model.position);
            building.scale.set(0.1, 0.1, 0.1);
            scene.current.add(building);
            buildings.current.push(building);
          },
          undefined,
          (error) => {
            console.error('Error loading building model:', error);
          }
        );
      }
    } catch (error) {
      console.error('Error loading buildings:', error);
    }
  };

  const getElevation = (x, z, elevationData) => {
    // Simple elevation calculation based on distance from center
    const distance = Math.sqrt(x * x + z * z);
    return Math.sin(distance * 0.01) * 10;
  };

  const handleResize = () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    camera.current.aspect = width / height;
    camera.current.updateProjectionMatrix();
    renderer.current.setSize(width, height);
  };

  const animate = () => {
    requestAnimationFrame(animate);

    // Update camera position based on map
    const center = map.current.getCenter();
    const zoom = map.current.getZoom();
    const pitch = map.current.getPitch();
    const bearing = map.current.getBearing();

    camera.current.position.set(
      center.lng * 100,
      zoom * 10,
      center.lat * 100
    );
    camera.current.lookAt(0, 0, 0);

    // Rotate buildings slightly for visual interest
    buildings.current.forEach(building => {
      building.rotation.y += 0.001;
    });

    renderer.current.render(scene.current, camera.current);
  };

  return (
    <div className="map-container">
      <div ref={mapContainer} className="map" />
      <div id="three-container" className="three-container" />
    </div>
  );
};

export default Map3DVisualization; 