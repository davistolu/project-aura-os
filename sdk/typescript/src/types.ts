export type Capability =
  | 'system.hardware.read'
  | 'system.process.list'
  | 'system.process.kill'
  | 'filesystem.read'
  | 'filesystem.write'
  | 'filesystem.delete'
  | 'terminal.execute'
  | 'network.request'
  | 'package.manage'
  | 'workspace.manage'
  | 'notification.send'
  | 'vm.manage'
  | 'automation.manage';

export type PermissionTier =
  | 'OBSERVE'
  | 'SUGGEST'
  | 'EXECUTE_SAFE'
  | 'EXECUTE_PRIVILEGED'
  | 'AUTONOMOUS';

export interface SystemMetrics {
  cpuUsagePercent: number;
  memoryUsedMb: number;
  memoryTotalMb: number;
  batteryPercent?: number;
  kernelVersion: string;
}

export interface NotificationPayload {
  title: string;
  body: string;
  urgency?: 'low' | 'normal' | 'critical';
}
