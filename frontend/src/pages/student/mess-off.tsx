import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getMessOffHistory, requestMessOff, cancelMessOff } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { PageHeader } from '@/components/page-header'
import { PageTransition, FadeIn } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { useToast } from '@/hooks/use-toast'
import { messOffFormSchema, type MessOffFormValues } from '@/lib/validations'
import { formatDate, getStatusBadgeVariant } from '@/lib/utils'
import { DoorOpen, Plus, X, Calendar } from 'lucide-react'

export function StudentMessOff() {
  const { email, user } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()
  const [showForm, setShowForm] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<MessOffFormValues>({
    resolver: zodResolver(messOffFormSchema),
  })

  const { data: history, isLoading } = useQuery({
    queryKey: ['messOffHistory', email],
    queryFn: () => getMessOffHistory(email),
  })

  const requestMutation = useMutation({
    mutationFn: (data: MessOffFormValues) =>
      requestMessOff(email, { user_id: user!.UserID, start_date: data.start_date, end_date: data.end_date }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messOffHistory'] })
      toast.success('Mess off request submitted!')
      setShowForm(false)
      reset()
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const cancelMutation = useMutation({
    mutationFn: (id: number) => cancelMessOff(email, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messOffHistory'] })
      toast.success('Request cancelled')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const approvedCount = history?.filter((h) => h.Status === 'Approved').length ?? 0

  if (isLoading) return <PageLoading />

  return (
    <PageTransition>
      <div className="space-y-6 max-w-3xl mx-auto">
        <PageHeader
          title="Mess Off"
          description="Request time off from the mess"
          icon={DoorOpen}
          action={
            <Button onClick={() => setShowForm(true)} className="gap-2">
              <Plus className="h-4 w-4" /> New Request
            </Button>
          }
        />

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Monthly Quota</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="relative h-20 w-20 shrink-0">
                <svg className="h-full w-full -rotate-90" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="15.5" fill="none" stroke="hsl(var(--muted))" strokeWidth="3" />
                  <circle
                    cx="18" cy="18" r="15.5" fill="none" stroke="hsl(var(--primary))" strokeWidth="3"
                    strokeDasharray={`${(approvedCount / 12) * 100} ${100 - (approvedCount / 12) * 100}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg font-bold">{approvedCount}/12</span>
                </div>
              </div>
              <div className="text-sm text-muted-foreground">
                <p>You've used {approvedCount} out of 12 allowed mess-off days this month.</p>
                <p className="mt-1">Each day off saves you from being charged the daily mess rate.</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Request History</CardTitle>
            <CardDescription>All your mess-off requests</CardDescription>
          </CardHeader>
          <CardContent>
            {!history || history.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No mess-off requests yet.</p>
            ) : (
              <div className="space-y-3">
                {history.map((req) => (
                  <FadeIn key={req.MessOffID}>
                    <div className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-muted/50">
                      <div className="flex items-center gap-4 min-w-0">
                        <Calendar className="h-5 w-5 text-muted-foreground shrink-0" />
                        <div>
                          <p className="font-medium">
                            {formatDate(req.StartDate)} — {formatDate(req.EndDate)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            Requested {formatDate(req.RequestDate)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <Badge variant={getStatusBadgeVariant(req.Status)}>{req.Status}</Badge>
                        {req.Status === 'Pending' && (
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => cancelMutation.mutate(req.MessOffID)}
                            aria-label="Cancel request"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </FadeIn>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Dialog open={showForm} onOpenChange={(open) => { if (!open) { setShowForm(false); reset() } }}>
          <DialogHeader>
            <DialogTitle>New Mess Off Request</DialogTitle>
            <DialogDescription>Select the dates you'd like to skip the mess</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit((data) => requestMutation.mutate(data))}>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input id="start_date" type="date" {...register('start_date')} />
                {errors.start_date && <p className="text-xs text-destructive">{errors.start_date.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input id="end_date" type="date" {...register('end_date')} />
                {errors.end_date && <p className="text-xs text-destructive">{errors.end_date.message}</p>}
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => { setShowForm(false); reset() }}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting || requestMutation.isPending}>
                {requestMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </Button>
            </DialogFooter>
          </form>
        </Dialog>
      </div>
    </PageTransition>
  )
}
