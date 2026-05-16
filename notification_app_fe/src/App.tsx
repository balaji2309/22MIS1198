import React, { useState } from 'react';
import { RemoteLogger } from '../../logging_middleware/src/index';

// Pass identical token down to intercept UI analytics directly to test server
const AUTH_BEARER_TOKEN = "YOUR_JWT_ACCESS_TOKEN_HERE";
const uiLogger = new RemoteLogger(AUTH_BEARER_TOKEN);

export default function App() {
  const [channel, setChannel] = useState('email');
  const [recipient, setRecipient] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState<string | null>(null);

  const handleDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Dispatching event stream...");
    
    await uiLogger.log('frontend', 'info', 'component', `Submission initialization triggered for channel: ${channel}`);

    try {
      const response = await fetch('http://localhost:5000/api/dispatch-notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel, recipient, content })
      });

      const data = await response.json();
      
      if (data.success) {
        setStatus("Success: Core event recorded smoothly!");
        await uiLogger.log('frontend', 'info', 'page', 'Server execution returned HTTP 200 state successfully.');
      } else {
        setStatus(`Error: ${data.error}`);
        await uiLogger.log('frontend', 'error', 'state', `Gateway operational rejection: ${data.error}`);
      }
    } catch (err: any) {
      setStatus("Critical pipeline communication failure.");
      await uiLogger.log('frontend', 'fatal', 'utils', `Network stream capture break: ${err.message}`);
    }
  };

  return (
    <div className="dashboard-container">
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Core Interface Panel</h2>
      <form onSubmit={handleDispatch}>
        <label>Transmission Mode</label>
        <select className="input-field" value={channel} onChange={(e) => setChannel(e.target.value)}>
          <option value="email">Email Distribution</option>
          <option value="sms">SMS Text Stream</option>
          <option value="push">Push Notification Endpoint</option>
        </select>

        <label>Destination Identity Target</label>
        <input 
          type="text" 
          className="input-field" 
          placeholder="e.g., user@domain.com"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
          required 
        />

        <label>Message Content Context</label>
        <textarea 
          className="input-field" 
          rows={4}
          placeholder="Enter structured transmission information payload..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />

        <button type="submit" className="action-btn">Execute Distribution Pipeline</button>
      </form>

      {status && <div className="status-toast">{status}</div>}
    </div>
  );
}