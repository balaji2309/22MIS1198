import axios from "axios";

export type LogStack = "backend" | "frontend";
export type LogLevel = "debug" | "info" | "warn" | "error" | "fatal";
export type LogPackage = 
  | "cache" | "controller" | "cron_job" | "db" | "domain" | "handler" | "repository" | "route" | "service"
  | "api" | "component" | "hook" | "page" | "state" | "style"
  | "auth" | "config" | "middleware" | "utils";

export interface LogPayload {
  stack: LogStack;
  level: LogLevel;
  package: LogPackage;
  message: string;
}

export class RemoteLogger {
  private targetUrl = "http://4.224.186.213/evaluation-service/logs";
  private authToken: string;

  constructor(token: string) {
    if (!token) {
      throw new Error("A valid Bearer Token is required to initialize the Logger.");
    }
    this.authToken = token;
  }

  public async log(
    stack: LogStack,
    level: LogLevel,
    pkg: LogPackage,
    message: string
  ): Promise<{ logID: string; message: string } | null> {
    
    const payload: LogPayload = {
      stack: stack.toLowerCase() as LogStack,
      level: level.toLowerCase() as LogLevel,
      package: pkg.toLowerCase() as LogPackage,
      message
    };

    try {
      const response = await axios.post(this.targetUrl, payload, {
        headers: {
          "Authorization": `Bearer ${this.authToken}`,
          "Content-Type": "application/json"
        },
        timeout: 5000
      });
      return response.data;
    } catch (error: any) {
      console.error(`[Logger Failure]: ${error.response?.data?.message || error.message}`);
      return null;
    }
  }
}