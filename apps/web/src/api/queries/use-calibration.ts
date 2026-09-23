import { useQuery } from '@tanstack/react-query';
import { fetchCalibration } from '@/api/endpoints/calibration';
import { queryKeys } from '@/api/query-keys';

export function useCalibration() {
  return useQuery({
    queryKey: queryKeys.calibration,
    queryFn: fetchCalibration,
  });
}
