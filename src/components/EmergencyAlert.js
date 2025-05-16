import React, { useState } from 'react';
import { sendEmergencyAlert } from '../services/twilioService';
import Map from './Map';

const EmergencyAlert = () => {
  const [phoneNumbers, setPhoneNumbers] = useState('');
  const [location, setLocation] = useState('');
  const [coordinates, setCoordinates] = useState(null);
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus('');

    try {
      const numbers = phoneNumbers.split(',').map(num => num.trim());
      const result = await sendEmergencyAlert(numbers, location, message);
      
      if (result.success) {
        setStatus('Emergency alerts sent successfully!');
      } else {
        setStatus(`Error: ${result.error}`);
      }
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (coords, address) => {
    setCoordinates(coords);
    setLocation(address);
  };

  return (
    <div className="emergency-alert">
      <h2>Send Emergency Alert</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Phone Numbers (comma-separated):</label>
          <input
            type="text"
            value={phoneNumbers}
            onChange={(e) => setPhoneNumbers(e.target.value)}
            placeholder="+1234567890, +0987654321"
            required
          />
        </div>
        
        <div className="form-group">
          <label>Location:</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter location or click on map"
            required
          />
        </div>

        <div className="form-group">
          <label>Select Location on Map:</label>
          <Map 
            onLocationSelect={handleLocationSelect}
            initialLocation={coordinates}
          />
        </div>
        
        <div className="form-group">
          <label>Message:</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter emergency message"
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Alert'}
        </button>
      </form>
      
      {status && <div className="status">{status}</div>}
    </div>
  );
};

export default EmergencyAlert; 