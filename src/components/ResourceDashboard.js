import React, { useState, useEffect } from 'react';
import { collection, getDocs, updateDoc, doc } from 'firebase/firestore';
import { db } from '../config/firebase';
import twilio from 'twilio';

const ResourceDashboard = () => {
  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState(null);
  const [alertMessage, setAlertMessage] = useState('');
  const [phoneNumbers, setPhoneNumbers] = useState([]);

  // Initialize Twilio client
  const twilioClient = twilio(
    process.env.REACT_APP_TWILIO_ACCOUNT_SID,
    process.env.REACT_APP_TWILIO_AUTH_TOKEN
  );

  useEffect(() => {
    fetchResources();
    fetchPhoneNumbers();
  }, []);

  const fetchResources = async () => {
    try {
      const resourcesRef = collection(db, 'resources');
      const snapshot = await getDocs(resourcesRef);
      const resourcesData = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setResources(resourcesData);
    } catch (error) {
      console.error('Error fetching resources:', error);
    }
  };

  const fetchPhoneNumbers = async () => {
    try {
      const numbersRef = collection(db, 'alert_contacts');
      const snapshot = await getDocs(numbersRef);
      const numbers = snapshot.docs.map(doc => doc.data().phoneNumber);
      setPhoneNumbers(numbers);
    } catch (error) {
      console.error('Error fetching phone numbers:', error);
    }
  };

  const updateResourceQuantity = async (resourceId, newQuantity) => {
    try {
      const resourceRef = doc(db, 'resources', resourceId);
      await updateDoc(resourceRef, { quantity: newQuantity });
      
      // Check if quantity is below threshold
      const resource = resources.find(r => r.id === resourceId);
      if (newQuantity <= resource.threshold) {
        sendLowStockAlert(resource);
      }
      
      fetchResources(); // Refresh the list
    } catch (error) {
      console.error('Error updating resource:', error);
    }
  };

  const sendLowStockAlert = async (resource) => {
    const message = `ALERT: ${resource.name} is running low! Current quantity: ${resource.quantity}. Please restock soon.`;
    
    try {
      // Send SMS to all registered numbers
      for (const phoneNumber of phoneNumbers) {
        await twilioClient.messages.create({
          body: message,
          from: process.env.REACT_APP_TWILIO_PHONE_NUMBER,
          to: phoneNumber
        });
      }
      
      // Add alert to Firestore
      await addDoc(collection(db, 'alerts'), {
        resourceId: resource.id,
        resourceName: resource.name,
        message,
        timestamp: new Date(),
        status: 'pending'
      });
    } catch (error) {
      console.error('Error sending SMS alert:', error);
    }
  };

  const sendCustomAlert = async () => {
    if (!selectedResource || !alertMessage) return;

    try {
      // Send SMS to all registered numbers
      for (const phoneNumber of phoneNumbers) {
        await twilioClient.messages.create({
          body: `ALERT: ${selectedResource.name} - ${alertMessage}`,
          from: process.env.REACT_APP_TWILIO_PHONE_NUMBER,
          to: phoneNumber
        });
      }
      
      // Add alert to Firestore
      await addDoc(collection(db, 'alerts'), {
        resourceId: selectedResource.id,
        resourceName: selectedResource.name,
        message: alertMessage,
        timestamp: new Date(),
        status: 'pending'
      });
      
      setAlertMessage('');
    } catch (error) {
      console.error('Error sending custom alert:', error);
    }
  };

  return (
    <div className="resource-dashboard">
      <h2>Resource Inventory Dashboard</h2>
      
      <div className="resource-list">
        <h3>Available Resources</h3>
        <table>
          <thead>
            <tr>
              <th>Resource</th>
              <th>Category</th>
              <th>Quantity</th>
              <th>Threshold</th>
              <th>Location</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {resources.map(resource => (
              <tr key={resource.id}>
                <td>{resource.name}</td>
                <td>{resource.category}</td>
                <td>{resource.quantity}</td>
                <td>{resource.threshold}</td>
                <td>{resource.location}</td>
                <td>
                  <button onClick={() => setSelectedResource(resource)}>
                    Update
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedResource && (
        <div className="resource-update">
          <h3>Update {selectedResource.name}</h3>
          <div className="update-form">
            <label>
              New Quantity:
              <input
                type="number"
                value={selectedResource.quantity}
                onChange={(e) => updateResourceQuantity(selectedResource.id, parseInt(e.target.value))}
              />
            </label>
            <div className="alert-section">
              <h4>Send Custom Alert</h4>
              <textarea
                value={alertMessage}
                onChange={(e) => setAlertMessage(e.target.value)}
                placeholder="Enter alert message..."
              />
              <button onClick={sendCustomAlert}>Send Alert</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResourceDashboard; 