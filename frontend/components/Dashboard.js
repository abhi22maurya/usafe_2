import React, { useState, useEffect } from 'react';
import firebase from 'firebase/app';
import 'firebase/database';
import axios from 'axios';

const Dashboard = () => {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    firebase.database().ref('resources').on('value', (snapshot) => {
      const resourceList = [];
      snapshot.forEach((child) => {
        resourceList.push({ id: child.key, ...child.val() });
      });
      setResources(resourceList);
    });

    // Seed initial data
    firebase.database().ref('resources').set([
      { item: 'Food Kits', quantity: 100, location: 'Dehradun' },
      { item: 'Medical Supplies', quantity: 50, location: 'Uttarkashi' },
    ]);
  }, []);

  const sendAlert = async () => {
    try {
      await axios.post('/api/alert', {
        phone: '+91XXXXXXXXXX', // Replace with test number
        message: 'High landslide risk in your area! Evacuate to nearest shelter.',
      });
      alert('Alert sent!');
    } catch (error) {
      alert('Error sending alert');
    }
  };

  return (
    <div>
      <h2>Resource Inventory</h2>
      <table>
        <thead>
          <tr>
            <th>Item</th>
            <th>Quantity</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          {resources.map((r) => (
            <tr key={r.id}>
              <td>{r.item}</td>
              <td>{r.quantity}</td>
              <td>{r.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={sendAlert}>Send Alert</button>
    </div>
  );
};

export default Dashboard;