const API_BASE_URL = 'http://localhost:5001/api';

export const sendSMS = async (to, message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/send-sms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ to, message }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending SMS:', error);
    return { success: false, error: error.message };
  }
};

export const sendEmergencyAlert = async (phoneNumbers, location, message = 'Emergency Alert') => {
  try {
    const response = await fetch(`${API_BASE_URL}/send-emergency-alert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phoneNumbers, location, message }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending emergency alerts:', error);
    return { success: false, error: error.message };
  }
}; 