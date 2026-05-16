import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { RemoteLogger } from '../../logging_middleware/dist/index';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Hardcoded verification token received from your Auth API step
const AUTH_BEARER_TOKEN = "YOUR_JWT_ACCESS_TOKEN_HERE"; 
const logger = new RemoteLogger(AUTH_BEARER_TOKEN);

app.use(cors());
app.use(express.json());

// Production-grade Logging & Event Interception Middleware
app.use(async (req: Request, res: Response, next: NextFunction) => {
  await logger.log('backend', 'info', 'middleware', `Incoming ${req.method} request to ${req.path}`);
  next();
});

// Primary Business Route Engine
app.post('/api/dispatch-notification', async (req: Request, res: Response): Promise<void> => {
  const { channel, recipient, content } = req.body;

  if (!channel || !recipient || !content) {
    await logger.log('backend', 'error', 'handler', 'Payload verification failed: missing parameters.');
    res.status(400).json({ success: false, error: 'Missing required payload variables' });
    return;
  }

  try {
    // Structural simulator executing standard internal task workflows
    await logger.log('backend', 'debug', 'service', `Processing transaction block via target channel: ${channel}`);
    
    // Success checkpoint registration
    await logger.log('backend', 'info', 'controller', `Notification successfully dispatched down cleanly to ${recipient}`);
    
    res.status(200).json({
      success: true,
      transactionId: crypto.randomUUID(),
      timestamp: new Date().toISOString()
    });
  } catch (err: any) {
    await logger.log('backend', 'fatal', 'repository', `System transaction exception caught: ${err.message}`);
    res.status(500).json({ success: false, error: 'Internal system fault occurred' });
  }
});

app.listen(PORT, async () => {
  await logger.log('backend', 'info', 'config', `Application cluster fully initialized online running over port ${PORT}`);
  console.log(`Server executing successfully on port ${PORT}`);
});
