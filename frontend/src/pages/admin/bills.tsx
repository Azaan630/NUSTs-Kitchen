import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getAllStudents, createBill, deleteBill, payBill, getMonthlyBillingSummary } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { formatCurrency, formatDate, getStatusBadgeVariant } from '@/lib/utils'
import { Receipt, Plus, Trash2, DollarSign } from 'lucide-react'
import type { BillingSummaryItem } from '@/types'

export function AdminBills() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const [createOpen, setCreateOpen] = useState(false)
  const [payOpen, setPayOpen] = useState(false)
  const [payingBill, setPayingBill] = useState<BillingSummaryItem | null>(null)
  const [createForm, setCreateForm] = useState({
    user_id: 0, month: '', year: new Date().getFullYear(),
    total_days: 30, mess_off_days: 0, daily_rate: 500, total_amount: 15000, due_date: '',
  })
  const [paymentForm, setPaymentForm] = useState({
    amount_paid: 0, payment_date: new Date().toISOString().split('T')[0] ?? '', payment_method: 'Cash',
  })

  const { data: summary, isLoading } = useQuery({
    queryKey: ['billingSummary', email], queryFn: () => getMonthlyBillingSummary(email),
  })

  const { data: students } = useQuery({
    queryKey: ['students', email], queryFn: () => getAllStudents(email),
  })

  const createMutation = useMutation({
    mutationFn: () => createBill(email, createForm),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['billingSummary'] }); toast.success('Bill created!'); setCreateOpen(false) },
    onError: (err: Error) => toast.error(err.message),
  })

  const payMutation = useMutation({
    mutationFn: () => payBill(email, payingBill!.BillingID, paymentForm),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['billingSummary'] }); toast.success('Payment recorded!'); setPayOpen(false) },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteBill(email, id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['billingSummary'] }); toast.success('Bill deleted') },
    onError: (err: Error) => toast.error(err.message),
  })

  const columns: Column<BillingSummaryItem>[] = [
    { key: 'Full_Name', header: 'Student', sortable: true },
    { key: 'Month', header: 'Period', render: (b) => `${b.Month} ${b.Year}`, hideOnMobile: true },
    { key: 'TotalAmount', header: 'Amount', sortable: true, render: (b) => formatCurrency(b.TotalAmount) },
    { key: 'AmountPaid', header: 'Paid', render: (b) => formatCurrency(b.AmountPaid || 0), hideOnMobile: true },
    { key: 'DueDate', header: 'Due', render: (b) => formatDate(b.DueDate), hideOnMobile: true },
    { key: 'Status', header: 'Status', sortable: true, render: (b) => <Badge variant={getStatusBadgeVariant(b.Status)}>{b.Status}</Badge> },
    { key: 'actions', header: '', render: (b) => (
      <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
        {b.Status !== 'Paid' && (
          <Button variant="ghost" size="icon-sm" onClick={() => { setPayingBill(b); setPaymentForm({ ...paymentForm, amount_paid: b.TotalAmount }); setPayOpen(true) }}>
            <DollarSign className="h-4 w-4 text-emerald-500" />
          </Button>
        )}
        <Button variant="ghost" size="icon-sm" onClick={() => deleteMutation.mutate(b.BillingID)}>
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </div>
    )},
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Bills Management" description="Create and manage student bills" icon={Receipt}
          action={<Button onClick={() => setCreateOpen(true)} className="gap-2"><Plus className="h-4 w-4" /> Create Bill</Button>} />
        <Card>
          <CardContent className="pt-6">
            <DataTable columns={columns} data={summary || []} keyExtractor={(b) => b.BillingID}
              searchable searchKeys={['Full_Name', 'Month', 'Status']} isLoading={isLoading} emptyMessage="No bills found" />
          </CardContent>
        </Card>

        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogHeader><DialogTitle>Create Bill</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Student</Label>
              <Select value={String(createForm.user_id)} onChange={(e) => setCreateForm({ ...createForm, user_id: Number(e.target.value) })}
                options={students?.map((s) => ({ value: String(s.UserID), label: `${s.Full_Name} (${s.RegNo})` })) || []} placeholder="Select student" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Month</Label><Input value={createForm.month} onChange={(e) => setCreateForm({ ...createForm, month: e.target.value })} placeholder="January" /></div>
              <div className="space-y-2"><Label>Year</Label><Input type="number" value={createForm.year} onChange={(e) => setCreateForm({ ...createForm, year: Number(e.target.value) })} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Total Days</Label><Input type="number" value={createForm.total_days} onChange={(e) => setCreateForm({ ...createForm, total_days: Number(e.target.value) })} /></div>
              <div className="space-y-2"><Label>Mess Off Days</Label><Input type="number" value={createForm.mess_off_days} onChange={(e) => setCreateForm({ ...createForm, mess_off_days: Number(e.target.value) })} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Daily Rate (Rs)</Label><Input type="number" value={createForm.daily_rate} onChange={(e) => setCreateForm({ ...createForm, daily_rate: Number(e.target.value) })} /></div>
              <div className="space-y-2"><Label>Total Amount (Rs)</Label><Input type="number" value={createForm.total_amount} onChange={(e) => setCreateForm({ ...createForm, total_amount: Number(e.target.value) })} /></div>
            </div>
            <div className="space-y-2"><Label>Due Date</Label><Input type="date" value={createForm.due_date} onChange={(e) => setCreateForm({ ...createForm, due_date: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button onClick={() => createMutation.mutate()} disabled={!createForm.user_id || !createForm.month || !createForm.due_date || createMutation.isPending}>Create Bill</Button>
          </DialogFooter>
        </Dialog>

        <Dialog open={payOpen} onOpenChange={setPayOpen}>
          <DialogHeader>
            <DialogTitle>Record Payment</DialogTitle>
            <DialogDescription>{payingBill && `Bill for ${payingBill.Full_Name} — ${formatCurrency(payingBill.TotalAmount)}`}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Amount (Rs)</Label><Input type="number" value={paymentForm.amount_paid} onChange={(e) => setPaymentForm({ ...paymentForm, amount_paid: Number(e.target.value) })} /></div>
            <div className="space-y-2"><Label>Payment Date</Label><Input type="date" value={paymentForm.payment_date} onChange={(e) => setPaymentForm({ ...paymentForm, payment_date: e.target.value })} /></div>
            <div className="space-y-2"><Label>Payment Method</Label>
              <Select value={paymentForm.payment_method} onChange={(e) => setPaymentForm({ ...paymentForm, payment_method: e.target.value })}
                options={[{ value: 'Cash', label: 'Cash' }, { value: 'Bank Transfer', label: 'Bank Transfer' }, { value: 'JazzCash', label: 'JazzCash' }, { value: 'Easypaisa', label: 'Easypaisa' }]} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPayOpen(false)}>Cancel</Button>
            <Button onClick={() => payMutation.mutate()} disabled={payMutation.isPending}>Record Payment</Button>
          </DialogFooter>
        </Dialog>
      </div>
    </PageTransition>
  )
}
