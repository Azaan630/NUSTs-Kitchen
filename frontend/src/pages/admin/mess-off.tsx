import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getMessOffHistory, approveMessOff } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { formatDate, getStatusBadgeVariant } from '@/lib/utils'
import { DoorOpen, CheckCheck } from 'lucide-react'
import type { MessOff } from '@/types'

export function AdminMessOff() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const { data: requests, isLoading } = useQuery({
    queryKey: ['messOffHistory', email],
    queryFn: () => getMessOffHistory(email),
  })

  const approveMutation = useMutation({
    mutationFn: (id: number) => approveMessOff(email, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messOffHistory'] })
      toast.success('Mess off request approved!')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const columns: Column<MessOff>[] = [
    { key: 'Full_Name', header: 'Student', sortable: true },
    { key: 'StartDate', header: 'From', sortable: true, render: (r) => formatDate(r.StartDate) },
    { key: 'EndDate', header: 'To', sortable: true, render: (r) => formatDate(r.EndDate) },
    { key: 'RequestDate', header: 'Requested', render: (r) => formatDate(r.RequestDate), hideOnMobile: true },
    {
      key: 'Status', header: 'Status', sortable: true,
      render: (r) => <Badge variant={getStatusBadgeVariant(r.Status)}>{r.Status}</Badge>,
    },
    {
      key: 'actions', header: '',
      render: (r) =>
        r.Status === 'Pending' ? (
          <div onClick={(e) => e.stopPropagation()}>
            <Button size="sm" onClick={() => approveMutation.mutate(r.MessOffID)} className="gap-1">
              <CheckCheck className="h-4 w-4" /> Approve
            </Button>
          </div>
        ) : null,
    },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader
          title="Mess Off Requests"
          description="Approve or review student mess-off requests"
          icon={DoorOpen}
        />
        <Card>
          <CardContent className="pt-6">
            <DataTable
              columns={columns}
              data={requests || []}
              keyExtractor={(r) => r.MessOffID}
              searchable searchKeys={['Full_Name', 'Status']}
              isLoading={isLoading}
              emptyMessage="No mess-off requests found"
            />
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  )
}
