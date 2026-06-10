import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getMyBills, getMyBillHistory } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { formatCurrency, formatDate, getStatusBadgeVariant } from '@/lib/utils'
import { Receipt, History } from 'lucide-react'
import type { Bill, Transaction } from '@/types'

export function StudentBills() {
  const { email } = useAuth()
  const [tab, setTab] = useState('bills')

  const { data: bills, isLoading: billsLoading } = useQuery({
    queryKey: ['myBills', email],
    queryFn: () => getMyBills(email),
  })

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['myBillHistory', email],
    queryFn: () => getMyBillHistory(email),
  })

  const billColumns: Column<Bill>[] = [
    { key: 'Month', header: 'Period', render: (b) => `${b.Month} ${b.Year}` },
    { key: 'TotalAmount', header: 'Amount', sortable: true, render: (b) => formatCurrency(b.TotalAmount) },
    { key: 'DueDate', header: 'Due Date', render: (b) => formatDate(b.DueDate), hideOnMobile: true },
    {
      key: 'Status', header: 'Status', sortable: true,
      render: (b) => <Badge variant={getStatusBadgeVariant(b.Status)}>{b.Status}</Badge>,
    },
  ]

  const historyColumns: Column<Transaction>[] = [
    { key: 'PaymentDate', header: 'Date', sortable: true, render: (h) => formatDate(h.PaymentDate) },
    { key: 'AmountPaid', header: 'Amount', render: (h) => formatCurrency(h.AmountPaid) },
    { key: 'PaymentMethod', header: 'Method', sortable: true },
  ]

  if (billsLoading) return <PageLoading />

  return (
    <PageTransition>
      <div className="space-y-6 max-w-4xl mx-auto">
        <PageHeader title="My Bills" description="View your billing and payment history" icon={Receipt} />

        <Tabs value={tab} onValueChange={setTab} defaultValue="bills">
          <TabsList>
            <TabsTrigger value="bills" className="gap-2">
              <Receipt className="h-4 w-4" /> Bills
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <History className="h-4 w-4" /> Payment History
            </TabsTrigger>
          </TabsList>
          <TabsContent value="bills" className="mt-6">
            <Card>
              <CardContent className="pt-6">
                <DataTable
                  columns={billColumns}
                  data={bills || []}
                  keyExtractor={(b) => b.BillingID}
                  emptyMessage="No bills found"
                />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="history" className="mt-6">
            <Card>
              <CardContent className="pt-6">
                <DataTable
                  columns={historyColumns}
                  data={history || []}
                  keyExtractor={(h) => h.TransactionID}
                  isLoading={historyLoading}
                  emptyMessage="No payment history"
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </PageTransition>
  )
}
