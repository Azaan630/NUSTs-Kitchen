import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getActivePoll, startPoll, getPollResults } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition, FadeIn } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { useToast } from '@/hooks/use-toast'
import { Vote, Play, BarChart3 } from 'lucide-react'
import type { PollResult } from '@/types'

export function AdminPolls() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const { data: activeItems, isLoading: activeLoading } = useQuery({
    queryKey: ['activePoll', email],
    queryFn: () => getActivePoll(email),
  })

  const { data: results, isLoading: resultsLoading } = useQuery({
    queryKey: ['pollResults', email],
    queryFn: () => getPollResults(email),
  })

  const startPollMutation = useMutation({
    mutationFn: () => startPoll(email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activePoll'] })
      toast.success('Poll started! Students can now vote.')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const resultColumns: Column<PollResult>[] = [
    { key: 'ItemName', header: 'Item', sortable: true },
    { key: 'Category', header: 'Category', sortable: true },
    { key: 'Vote_Count', header: 'Votes', sortable: true },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader
          title="Poll Management"
          description="Start polls and view voting results"
          icon={Vote}
          action={
            <Button onClick={() => startPollMutation.mutate()} disabled={startPollMutation.isPending} className="gap-2">
              <Play className="h-4 w-4" />
              {startPollMutation.isPending ? 'Starting...' : 'Start New Poll'}
            </Button>
          }
        />

        <div className="grid gap-6 lg:grid-cols-2">
          <FadeIn delay={0.1}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <BarChart3 className="h-5 w-5" /> Active Poll Items
                </CardTitle>
                <CardDescription>Items currently available for voting</CardDescription>
              </CardHeader>
              <CardContent>
                {activeLoading ? (
                  <PageLoading />
                ) : activeItems && activeItems.length > 0 ? (
                  <div className="space-y-3">
                    {activeItems.map((item) => (
                      <div key={item.ItemID} className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{item.ItemName}</span>
                          {item.IsVegetarian && <Badge variant="secondary" className="text-xs">Veg</Badge>}
                        </div>
                        <span className="text-sm font-semibold">Rs. {item.Price}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No active poll. Start one!</p>
                )}
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn delay={0.2}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Poll Results</CardTitle>
                <CardDescription>Vote counts for all items</CardDescription>
              </CardHeader>
              <CardContent>
                <DataTable
                  columns={resultColumns}
                  data={results || []}
                  keyExtractor={(r) => r.ItemID}
                  isLoading={resultsLoading}
                  emptyMessage="No poll results yet"
                />
              </CardContent>
            </Card>
          </FadeIn>
        </div>
      </div>
    </PageTransition>
  )
}
