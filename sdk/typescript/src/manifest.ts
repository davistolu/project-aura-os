import { Capability } from './types';

export interface AppManifest {
  id: string;
  name: string;
  version: string;
  description?: string;
  publisher: string;
  executable: string;
  runtime: 'native' | 'wine' | 'proton' | 'container' | 'vm';
  requiredCapabilities: Capability[];
  sandboxIsolated: boolean;
}

export class ManifestValidator {
  public static validate(manifest: unknown): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    if (!manifest || typeof manifest !== 'object') {
      return { valid: false, errors: ['Manifest must be an object'] };
    }

    const m = manifest as Record<string, unknown>;
    if (!m.id || typeof m.id !== 'string') errors.push("Missing or invalid field 'id'");
    if (!m.name || typeof m.name !== 'string') errors.push("Missing or invalid field 'name'");
    if (!m.version || typeof m.version !== 'string') errors.push("Missing or invalid field 'version'");
    if (!m.publisher || typeof m.publisher !== 'string') errors.push("Missing or invalid field 'publisher'");
    if (!Array.isArray(m.requiredCapabilities)) errors.push("Field 'requiredCapabilities' must be an array");

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
