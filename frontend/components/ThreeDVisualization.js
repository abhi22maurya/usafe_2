import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Html, useProgress, Line, Stats } from '@react-three/drei';
import * as THREE from 'three';
import './ThreeDVisualization.css';
import LoadingIndicator from './LoadingIndicator';

// AI-powered building data with enhanced features
const buildings = [
  { 
    position: [-6, 0, -6], 
    height: 3.5, 
    color: '#2E7D32', 
    name: 'Hospital', 
    info: '24/7 Emergency Services',
    riskScore: 0.2,
    capacity: 0.8,
    resources: {
      medical: 0.9,
      staff: 0.7,
      equipment: 0.8
    },
    recommendations: ['High capacity', 'Emergency ready', 'Medical supplies stocked'],
    connections: [1, 3, 4],
    alerts: ['High patient load', 'Staff rotation needed']
  },
  { 
    position: [0, 0, -6], 
    height: 4.5, 
    color: '#1565C0', 
    name: 'Police Station', 
    info: 'Law Enforcement HQ',
    riskScore: 0.1,
    recommendations: ['Patrol routes optimized', 'Emergency response ready', 'Communication systems active'],
    connections: [0, 2, 4]
  },
  { position: [6, 0, -6], height: 3, color: '#F57F17', name: 'Fire Station', info: 'Fire & Rescue Services' },
  { position: [-6, 0, 0], height: 4, color: '#6A1B9A', name: 'Emergency Center', info: 'Disaster Response HQ' },
  { position: [0, 0, 0], height: 3, color: '#C62828', name: 'Shelter', info: 'Emergency Housing' },
  { position: [6, 0, 0], height: 3.5, color: '#00838F', name: 'Medical Center', info: 'Healthcare Services' },
  { position: [-6, 0, 6], height: 2.5, color: '#EF6C00', name: 'Relief Center', info: 'Aid Distribution' },
  { position: [0, 0, 6], height: 4, color: '#558B2F', name: 'Command Center', info: 'Operations Control' },
  { position: [6, 0, 6], height: 3, color: '#AD1457', name: 'Resource Center', info: 'Supply Management' }
];

// Loading component for 3D scene
function LoadingScreen() {
  const { progress } = useProgress();
  return <LoadingIndicator message={`Loading 3D Scene... ${Math.round(progress)}%`} />;
}

// Responsive camera setup with touch gestures
const ResponsiveCamera = () => {
  const { camera, size, gl } = useThree();
  const touchStartRef = useRef({ x: 0, y: 0 });
  const lastPinchDistanceRef = useRef(0);
  
  useEffect(() => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
      camera.position.set(25, 25, 25);
      camera.fov = 50;
    } else {
      camera.position.set(20, 20, 20);
      camera.fov = 40;
    }
    camera.updateProjectionMatrix();

    const handleTouchStart = (e) => {
      if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        lastPinchDistanceRef.current = Math.sqrt(dx * dx + dy * dy);
      } else if (e.touches.length === 1) {
        touchStartRef.current = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      }
    };

    const handleTouchMove = (e) => {
      if (e.touches.length === 2) {
        // Pinch to zoom
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const delta = distance - lastPinchDistanceRef.current;
        
        if (Math.abs(delta) > 1) {
          camera.position.z += delta * 0.1;
          camera.position.z = Math.max(10, Math.min(40, camera.position.z));
          lastPinchDistanceRef.current = distance;
        }
      }
    };

    const canvas = gl.domElement;
    canvas.addEventListener('touchstart', handleTouchStart);
    canvas.addEventListener('touchmove', handleTouchMove);

    return () => {
      canvas.removeEventListener('touchstart', handleTouchStart);
      canvas.removeEventListener('touchmove', handleTouchMove);
    };
  }, [camera, size, gl]);

  return null;
};

// AI Visualization component
const AIVisualization = ({ buildings }) => {
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [showConnections, setShowConnections] = useState(false);
  const [showRisk, setShowRisk] = useState(false);

  // Calculate risk visualization
  const getRiskColor = (riskScore) => {
    const hue = (1 - riskScore) * 120; // Green (0) to Red (1)
    return `hsl(${hue}, 100%, 50%)`;
  };

  // Draw connections between buildings
  const renderConnections = () => {
    if (!selectedBuilding || !showConnections) return null;

    return selectedBuilding.connections.map((targetIndex) => {
      const target = buildings[targetIndex];
      const start = new THREE.Vector3(...selectedBuilding.position);
      const end = new THREE.Vector3(...target.position);
      
      return (
        <Line
          key={`${selectedBuilding.name}-${target.name}`}
          points={[start, end]}
          color="#00ff00"
          lineWidth={2}
          dashed={true}
        />
      );
    });
  };

  return (
    <group>
      {buildings.map((building, index) => (
        <group key={index}>
          <mesh
            position={building.position}
            onClick={() => {
              setSelectedBuilding(building);
              setShowConnections(true);
            }}
          >
            <boxGeometry args={[1, building.height, 1]} />
            <meshStandardMaterial 
              color={showRisk ? getRiskColor(building.riskScore) : building.color}
              metalness={0.5}
              roughness={0.2}
            />
          </mesh>
          {selectedBuilding === building && (
            <Html position={[0, building.height + 1, 0]}>
              <div className="ai-info">
                <h3>{building.name}</h3>
                <p>Risk Score: {(building.riskScore * 100).toFixed(1)}%</p>
                <ul>
                  {building.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            </Html>
          )}
        </group>
      ))}
      {renderConnections()}
    </group>
  );
};

// AI Analytics component
const AIAnalytics = ({ buildings }) => {
  const [selectedMetric, setSelectedMetric] = useState('risk');
  const [timeRange, setTimeRange] = useState('24h');
  const [predictionMode, setPredictionMode] = useState(false);

  const getMetricColor = (value, metric) => {
    switch (metric) {
      case 'risk':
        return `hsl(${(1 - value) * 120}, 100%, 50%)`;
      case 'capacity':
        return `hsl(${value * 120}, 100%, 50%)`;
      case 'resources':
        return `hsl(${value * 120}, 100%, 50%)`;
      default:
        return '#ffffff';
    }
  };

  return (
    <div className="ai-analytics">
      <div className="analytics-controls">
        <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
          <option value="risk">Risk Score</option>
          <option value="capacity">Capacity</option>
          <option value="resources">Resources</option>
        </select>
        <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
          <option value="1h">Last Hour</option>
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
        </select>
        <button 
          className={predictionMode ? 'active' : ''}
          onClick={() => setPredictionMode(!predictionMode)}
        >
          {predictionMode ? 'Hide Predictions' : 'Show Predictions'}
        </button>
      </div>
      <div className="analytics-chart">
        {/* Add chart visualization here */}
      </div>
    </div>
  );
};

// Enhanced Building component with real-time updates
const Building = ({ position, height, color, name, info, riskScore, capacity, resources, recommendations, connections, alerts }) => {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);
  const [scale, setScale] = useState(1);
  const [currentRisk, setCurrentRisk] = useState(riskScore);
  const { size } = useThree();
  const isMobile = size.width <= 768;
  const touchTimeout = useRef(null);

  // Simulate real-time risk updates
  useEffect(() => {
    const interval = setInterval(() => {
      const randomChange = (Math.random() - 0.5) * 0.1;
      setCurrentRisk(prev => Math.max(0, Math.min(1, prev + randomChange)));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Enhanced AI-powered animation
  useFrame(() => {
    if (hovered && !isMobile) {
      meshRef.current.rotation.y += 0.01;
      setScale(1.1);
    } else {
      const riskPulse = Math.sin(Date.now() * 0.001) * 0.05 * currentRisk;
      const capacityPulse = Math.sin(Date.now() * 0.002) * 0.03 * capacity;
      setScale(1 + riskPulse + capacityPulse);
    }
  });

  const getResourceColor = (value) => {
    return `hsl(${value * 120}, 100%, 50%)`;
  };

  const handlePointerDown = (e) => {
    e.stopPropagation();
    if (isMobile) {
      if (touchTimeout.current) clearTimeout(touchTimeout.current);
      setHovered(true);
      touchTimeout.current = setTimeout(() => {
        setHovered(false);
        setClicked(!clicked);
      }, 200);
    } else {
      setClicked(!clicked);
    }
  };

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onPointerOver={() => !isMobile && setHovered(true)}
        onPointerOut={() => !isMobile && setHovered(false)}
        onPointerDown={handlePointerDown}
        scale={scale}
      >
        <boxGeometry args={[1, height, 1]} />
        <meshStandardMaterial 
          color={hovered ? 'hotpink' : color} 
          metalness={0.5}
          roughness={0.2}
          transparent
          opacity={clicked ? 0.9 : 1}
        />
      </mesh>
      <Text
        position={[0, height / 2 + 0.5, 0]}
        fontSize={isMobile ? 0.15 : 0.2}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {name}
      </Text>
      {clicked && (
        <Html position={[0, height / 2 + 1, 0]}>
          <div className="building-info">
            <h3>{name}</h3>
            <p>{info}</p>
            <div className="metrics">
              <div className="metric">
                <span>Risk Level</span>
                <div className="progress-bar">
                  <div 
                    className="progress" 
                    style={{ 
                      width: `${currentRisk * 100}%`,
                      background: `linear-gradient(90deg, #4CAF50, #FFC107, #F44336)`
                    }}
                  />
                </div>
                <span>{(currentRisk * 100).toFixed(1)}%</span>
              </div>
              <div className="metric">
                <span>Capacity</span>
                <div className="progress-bar">
                  <div 
                    className="progress" 
                    style={{ 
                      width: `${capacity * 100}%`,
                      background: getResourceColor(capacity)
                    }}
                  />
                </div>
                <span>{(capacity * 100).toFixed(1)}%</span>
              </div>
              <div className="resources">
                <h4>Resources</h4>
                {Object.entries(resources).map(([key, value]) => (
                  <div key={key} className="resource">
                    <span>{key}</span>
                    <div className="progress-bar">
                      <div 
                        className="progress" 
                        style={{ 
                          width: `${value * 100}%`,
                          background: getResourceColor(value)
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            {alerts.length > 0 && (
              <div className="alerts">
                <h4>Active Alerts</h4>
                <ul>
                  {alerts.map((alert, i) => (
                    <li key={i} className="alert">{alert}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="recommendations">
              <h4>Recommendations</h4>
              <ul>
                {recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

// Main component with enhanced features
const ThreeDVisualization = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showRisk, setShowRisk] = useState(false);
  const [showConnections, setShowConnections] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showStats, setShowStats] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div className="three-container">
      {!isOnline && (
        <div className="offline-indicator">
          <span>⚠️ Offline Mode</span>
        </div>
      )}
      <div className="ai-controls">
        <button onClick={() => setShowRisk(!showRisk)}>
          {showRisk ? 'Hide Risk' : 'Show Risk'}
        </button>
        <button onClick={() => setShowConnections(!showConnections)}>
          {showConnections ? 'Hide Connections' : 'Show Connections'}
        </button>
        <button onClick={() => setShowAnalytics(!showAnalytics)}>
          {showAnalytics ? 'Hide Analytics' : 'Show Analytics'}
        </button>
        <button onClick={() => setShowStats(!showStats)}>
          {showStats ? 'Hide Stats' : 'Show Stats'}
        </button>
      </div>
      {showAnalytics && <AIAnalytics buildings={buildings} />}
      <Canvas dpr={[1, 2]}>
        <Suspense fallback={<LoadingScreen />}>
          {showStats && <Stats />}
          <ResponsiveCamera />
          <ambientLight intensity={0.2} />
          <pointLight position={[10, 15, 10]} intensity={1.2} />
          <pointLight position={[-10, 15, -10]} intensity={0.8} />
          <spotLight
            position={[0, 20, 0]}
            angle={0.3}
            penumbra={1}
            intensity={0.5}
            castShadow
          />
          <OrbitControls 
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={10}
            maxDistance={40}
            minPolarAngle={Math.PI / 6}
            maxPolarAngle={Math.PI / 2}
            enableDamping={true}
            dampingFactor={0.05}
            rotateSpeed={0.5}
            zoomSpeed={0.8}
            touchRotate={true}
            touchZoom={true}
            touches={{
              ONE: THREE.TOUCH.ROTATE,
              TWO: THREE.TOUCH.DOLLY_PAN
            }}
          />
          <gridHelper args={[25, 25]} />
          {buildings.map((building, index) => (
            <Building
              key={index}
              {...building}
            />
          ))}
          <AIVisualization buildings={buildings} />
        </Suspense>
      </Canvas>
    </div>
  );
};

export default ThreeDVisualization; 