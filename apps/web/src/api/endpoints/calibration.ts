import { apiRequest } from '@/api/client';
import type { CalibrationProfile, CalibrationUpdate } from '@/api/generated/schema.d';

export function fetchCalibration(): Promise<CalibrationProfile> {
  return apiRequest<CalibrationProfile>('/api/v1/calibration');
}

export function updateCalibration(body: CalibrationUpdate): Promise<CalibrationProfile> {
  return apiRequest<CalibrationProfile>('/api/v1/calibration', { method: 'PUT', body });
}
