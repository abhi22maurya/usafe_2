import React from 'react';
import './App.css';
import Map from './components/Map';
import Dashboard from './components/Dashboard';
import ThreeD from './components/ThreeD';

function App() {
  return (
    <div className="App">
      <h1>UttarakhandSafe</h1>
      <Map />
      <ThreeD />
      <Dashboard />
      <iframe
        src="http://YOUR_GRADIO_URL"
        title="AI Predictor"
        style={{ width: '100%', height: '400px' }}
      ></iframe>
    </div>
  );
}

export default App;