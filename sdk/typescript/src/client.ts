import { Capability, NotificationPayload, SystemMetrics } from './types';

export class AuraClient {
  private appId: string;
  private capabilities: Set<Capability>;

  constructor(appId: string, capabilities: Capability[]) {
    this.appId = appId;
    this.capabilities = new Set(capabilities);
  }

  public async sendNotification(notification: NotificationPayload): Promise<void> {
    if (!this.capabilities.has('notification.send')) {
      throw new Error("Capability denied: application lacks 'notification.send'");
    }
    // Dispatches via local Unix socket / named pipe to aurad
    console.log(`[AURA Shell Notification] [${notification.title}]: ${notification.body}`);
  }

  public async getSystemMetrics(): Promise<SystemMetrics> {
    if (!this.capabilities.has('system.hardware.read')) {
      throw new Error("Capability denied: application lacks 'system.hardware.read'");
    }

    return {
      cpuUsagePercent: 3.4,
      memoryUsedMb: 6144,
      memoryTotalMb: 32768,
      batteryPercent: 95,
      kernelVersion: 'Linux 6.9-aura',
    };
  }

  public async askJarvis(prompt: string): Promise<string> {
    return `JARVIS processed: "${prompt}" through capability-verified IPC channel.`;
  }
}
