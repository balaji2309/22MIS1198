export type LogStack = "backend" | "frontend";
export type LogLevel = "debug" | "info" | "warn" | "error" | "fatal";
export type LogPackage = "cache" | "controller" | "cron_job" | "db" | "domain" | "handler" | "repository" | "route" | "service" | "api" | "component" | "hook" | "page" | "state" | "style" | "auth" | "config" | "middleware" | "utils";
export interface LogPayload {
    stack: LogStack;
    level: LogLevel;
    package: LogPackage;
    message: string;
}
export declare class RemoteLogger {
    private targetUrl;
    private authToken;
    constructor(token: string);
    log(stack: LogStack, level: LogLevel, pkg: LogPackage, message: string): Promise<{
        logID: string;
        message: string;
    } | null>;
}
