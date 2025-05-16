const express = require('express');
const twilio = require('twilio');
const app = express();

const client = twilio('YOUR_ACCOUNT_SID', 'YOUR_AUTH_TOKEN');

app.use(express.json());

app.post('/api/alert', async (req, res) => {
  const { phone, message } = req.body;
  try {
    await client.messages.create({
      body: message,
      from: '+1234567890', // Your Twilio number
      to: phone,
    });
    res.status(200).send('Alert sent');
  } catch (error) {
    res.status(500).send('Error sending alert');
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));