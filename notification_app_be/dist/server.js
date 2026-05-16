"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const dotenv_1 = __importDefault(require("dotenv"));
const index_1 = require("../../logging_middleware/dist/index");
dotenv_1.default.config();
const app = (0, express_1.default)();
const PORT = process.env.PORT || 5000;
const AUTH_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJiYWxhamkuazIwMjJiQHZpdHN0dWRlbnQuYWMuaW4iLCJleHAiOjE3Nzg5MzEzMjQsImlhdCI6MTc3ODkzMDQyNCwiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjE4NGE1M2ZjLTFmMDktNGIwNC1hNzZiLWE0NGVjZDRiNzAyYiIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImJhbGFqaSBrIiwic3ViIjoiYTlhYmQyMWYtZTliMi00OGI4LWJjNTYtM2Y2MTIwOGMxZDhmIn0sImVtYWlsIjoiYmFsYWppLmsyMDIyYkB2aXRzdHVkZW50LmFjLmluIiwibmFtZSI6ImJhbGFqaSBrIiwicm9sbE5vIjoiMjJtaXMxMTk4IiwiYWNjZXNzQ29kZSI6IlNmRnVXZyIsImNsaWVudElEIjoiYTlhYmQyMWYtZTliMi00OGI4LWJjNTYtM2Y2MTIwOGMxZDhmIiwiY2xpZW50U2VjcmV0IjoiZ3R4dEZua1RCTnl6VHNVeiJ9.JBM3qQI3YKHMYGFIAIiR-LDwpgBKWdVjkFt6CjabyIw";
const logger = new index_1.RemoteLogger(AUTH_BEARER_TOKEN);
app.use((0, cors_1.default)());
app.use(express_1.default.json());
// Production-grade Logging & Event Interception Middleware
app.use(async (req, res, next) => {
    await logger.log('backend', 'info', 'middleware', `Incoming ${req.method} request to ${req.path}`);
    next();
});
// Primary Business Route Engine
app.post('/api/dispatch-notification', async (req, res) => {
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
    }
    catch (err) {
        await logger.log('backend', 'fatal', 'repository', `System transaction exception caught: ${err.message}`);
        res.status(500).json({ success: false, error: 'Internal system fault occurred' });
    }
});
app.listen(PORT, async () => {
    await logger.log('backend', 'info', 'config', `Application cluster fully initialized online running over port ${PORT}`);
    console.log(`Server executing successfully on port ${PORT}`);
});
