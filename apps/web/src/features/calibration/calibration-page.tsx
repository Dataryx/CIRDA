import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useCalibration } from '@/api/queries/use-calibration';
import { useUpdateCalibration } from '@/api/mutations/use-update-calibration';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { calibrationSchema, type CalibrationFormValues } from '@/lib/zod-schemas';

export function CalibrationPage() {
  const calibration = useCalibration();
  const update = useUpdateCalibration();

  const { register, handleSubmit, reset, formState } = useForm<CalibrationFormValues>({
    resolver: zodResolver(calibrationSchema),
    defaultValues: { theta_c: 0.62, theta_p: 0.28, c_min: 0.85 },
  });

  useEffect(() => {
    if (calibration.data) {
      reset({
        theta_c: calibration.data.theta_c,
        theta_p: calibration.data.theta_p,
        c_min: calibration.data.c_min,
      });
    }
  }, [calibration.data, reset]);

  if (calibration.isLoading) return <LoadingSpinner label="Loading calibration…" />;
  if (calibration.error) return <ErrorAlert error={calibration.error} />;

  return (
    <div>
      <PageHeader
        title="Calibration"
        description="Manage fusion thresholds (θ_c, θ_p) and coverage minimum (C_min)."
      />

      <Card className="max-w-lg">
        <CardHeader>
          <CardTitle className="text-base">
            {calibration.data?.name ?? 'Active profile'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="space-y-4"
            onSubmit={handleSubmit((values) => update.mutate(values))}
          >
            <div className="space-y-2">
              <label htmlFor="theta_c" className="text-sm font-medium">
                θ_c (confirmed threshold)
              </label>
              <Input id="theta_c" type="number" step="0.01" min="0" max="1" {...register('theta_c')} />
            </div>
            <div className="space-y-2">
              <label htmlFor="theta_p" className="text-sm font-medium">
                θ_p (possible threshold)
              </label>
              <Input id="theta_p" type="number" step="0.01" min="0" max="1" {...register('theta_p')} />
            </div>
            <div className="space-y-2">
              <label htmlFor="c_min" className="text-sm font-medium">
                C_min (coverage minimum)
              </label>
              <Input id="c_min" type="number" step="0.01" min="0" max="1" {...register('c_min')} />
            </div>
            {formState.errors.theta_p ? (
              <p className="text-sm text-destructive">{formState.errors.theta_p.message}</p>
            ) : null}
            {update.error ? <ErrorAlert error={update.error} title="Update failed" /> : null}
            <Button type="submit" disabled={update.isPending}>
              {update.isPending ? 'Saving…' : 'Save calibration'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
