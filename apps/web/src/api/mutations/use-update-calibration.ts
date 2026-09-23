import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateCalibration } from '@/api/endpoints/calibration';
import { queryKeys } from '@/api/query-keys';
import type { CalibrationUpdate } from '@/api/generated/schema.d';

export function useUpdateCalibration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CalibrationUpdate) => updateCalibration(body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.calibration });
    },
  });
}
