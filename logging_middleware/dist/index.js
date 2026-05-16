"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RemoteLogger = void 0;
const axios_1 = __importDefault(require("axios"));
class RemoteLogger {
    targetUrl = "http://4.224.186.213/evaluation-service/logs";
    authToken;
    constructor(token) {
        if (!token) {
            throw new Error("A valid Bearer Token is required to initialize the Logger.");
        }
        this.authToken = token;
    }
    async log(stack, level, pkg, message) {
        const payload = {
            stack: stack.toLowerCase(),
            level: level.toLowerCase(),
            package: pkg.toLowerCase(),
            message
        };
        try {
            const response = await axios_1.default.post(this.targetUrl, payload, {
                headers: {
                    "Authorization": `Bearer ${this.authToken}`,
                    "Content-Type": "application/json"
                },
                timeout: 5000
            });
            return response.data;
        }
        catch (error) {
            console.error(`[Logger Failure]: ${error.response?.data?.message || error.message}`);
            return null;
        }
    }
}
exports.RemoteLogger = RemoteLogger;
