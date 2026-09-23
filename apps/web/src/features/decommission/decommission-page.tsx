import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useDecisionsByEntity } from '@/api/queries/use-decisions';
import { useEvaluateDecision } from '@/api/mutations/use-evaluate-decision';
import { VerdictBadge } from '@/components/data-display/verdict-badge';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { evaluateDecisionSchema, type EvaluateDecisionFormValues } from '@/lib/zod-schemas';
import { formatDateTime } from '@/lib/datetime';

export function DecommissionPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const evaluate = useEvaluateDecision();
  const defaultEntity = params.get('entity') ?? '';

  const { register, handleSubmit, watch } = useForm<EvaluateDecisionFormValues>({
    resolver: zodResolver(evaluateDecisionSchema),
    defaultValues: { entity_id: defaultEntity, change_type: 'decommission' },
  });

  const entityId = watch('entity_id');
  const history = useDecisionsByEntity(entityId, { limit: 10 });

  return (
    <div>
      <PageHeader
        title="Decommission"
        description="Evaluate tri-state safety verdicts before irreversible decommission actions."
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Evaluate entity</CardTitle>
          </CardHeader>
          <CardContent>
            <form
              className="space-y-4"
              onSubmit={handleSubmit((values) => {
                evaluate.mutate(values, {
                  onSuccess: (data) => {
                    navigate(`/decommission/${encodeURIComponent(data.decision_id)}`);
                  },
                });
              })}
            >
              <div className="space-y-2">
                <label htmlFor="entity_id" className="text-sm font-medium">
                  Entity ID
                </label>
                <Input id="entity_id" placeholder="entity-id" {...register('entity_id')} />
              </div>
              <div className="space-y-2">
                <label htmlFor="change_type" className="text-sm font-medium">
                  Change type
                </label>
                <Input id="change_type" placeholder="decommission" {...register('change_type')} />
              </div>
              {evaluate.error ? <ErrorAlert error={evaluate.error} title="Evaluation failed" /> : null}
              <Button type="submit" variant="brand" disabled={evaluate.isPending}>
                {evaluate.isPending ? 'Evaluating…' : 'Evaluate decision'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent decisions</CardTitle>
          </CardHeader>
          <CardContent>
            {!entityId ? (
              <p className="text-sm text-muted-foreground">Enter an entity ID to view decision history.</p>
            ) : null}
            {entityId && history.isLoading ? <LoadingSpinner label="Loading history…" /> : null}
            {entityId && history.error ? <ErrorAlert error={history.error} /> : null}
            {entityId && history.data && history.data.items.length === 0 ? (
              <p className="text-sm text-muted-foreground">No prior decisions for this entity.</p>
            ) : null}
            {entityId && history.data && history.data.items.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Verdict</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.data.items.map((d) => (
                    <TableRow key={d.decision_id}>
                      <TableCell>
                        <VerdictBadge verdict={d.verdict} size="sm" />
                      </TableCell>
                      <TableCell className="text-sm">{formatDateTime(d.as_of)}</TableCell>
                      <TableCell>
                        <Link
                          to={`/decommission/${encodeURIComponent(d.decision_id)}`}
                          className="text-sm text-primary hover:underline"
                        >
                          Report
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
