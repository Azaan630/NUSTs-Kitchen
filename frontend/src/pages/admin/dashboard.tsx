import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getAllStudents, getAllFoodItems, getMonthlyBillingSummary, getAllIngredients } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/page-header'
import { PageLoading } from '@/components/loading-spinner'
import { PageTransition, FadeIn, StaggerChildren, staggerItem } from '@/components/page-transition'
import { motion } from 'framer-motion'
import { formatCurrency, formatNumber } from '@/lib/utils'
import { Users, Utensils, Package, TrendingUp, Activity } from 'lucide-react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

export function AdminDashboard() {
  const { email } = useAuth()

  const { data: students, isLoading: studentsLoading } = useQuery({
    queryKey: ['students', email],
    queryFn: () => getAllStudents(email),
  })
  const { data: items } = useQuery({ queryKey: ['foodItems', email], queryFn: () => getAllFoodItems(email) })
  const { data: ingredients } = useQuery({ queryKey: ['ingredients', email], queryFn: () => getAllIngredients(email) })
  const { data: billing } = useQuery({ queryKey: ['billingSummary', email], queryFn: () => getMonthlyBillingSummary(email) })

  if (studentsLoading) return <PageLoading />

  const totalBilled = billing?.reduce((sum, b) => sum + (b.TotalAmount || 0), 0) ?? 0
  const totalPaid = billing?.reduce((sum, b) => sum + (b.AmountPaid || 0), 0) ?? 0
  const activeStudents = students?.filter((s) => s.IsActive).length ?? 0
  const pendingBills = billing?.filter((b) => b.Status === 'Pending').length ?? 0
  const paidBills = billing?.filter((b) => b.Status === 'Paid').length ?? 0
  const overdueBills = billing?.filter((b) => b.Status === 'Overdue').length ?? 0
  const collectionRate = totalBilled > 0 ? Math.round((totalPaid / totalBilled) * 100) : 0

  const stats = [
    { title: 'Active Students', value: formatNumber(activeStudents), icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10', description: `${students?.length ?? 0} total registered` },
    { title: 'Food Items', value: formatNumber(items?.length ?? 0), icon: Utensils, color: 'text-emerald-500', bg: 'bg-emerald-500/10', description: 'On the menu' },
    { title: 'Collection Rate', value: `${collectionRate}%`, icon: TrendingUp, color: 'text-amber-500', bg: 'bg-amber-500/10', description: `${formatCurrency(totalPaid)} of ${formatCurrency(totalBilled)}` },
    { title: 'Ingredients', value: formatNumber(ingredients?.length ?? 0), icon: Package, color: 'text-purple-500', bg: 'bg-purple-500/10', description: 'In inventory' },
  ]

  const pieData = [
    { name: 'Paid', value: paidBills, color: '#22c55e' },
    { name: 'Pending', value: pendingBills, color: '#eab308' },
    { name: 'Overdue', value: overdueBills, color: '#ef4444' },
  ].filter((d) => d.value > 0)

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Admin Dashboard" description="Overview of the mess management system" icon={Activity} />

        <StaggerChildren className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <motion.div key={stat.title} variants={staggerItem}>
              <Card className="overflow-hidden transition-all hover:shadow-md hover:-translate-y-0.5">
                <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                  <div className={`rounded-lg p-2 ${stat.bg}`}>
                    <stat.icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </StaggerChildren>

        <div className="grid gap-4 lg:grid-cols-2">
          <FadeIn delay={0.1}>
            <Card>
              <CardHeader><CardTitle className="text-lg">Recent Students</CardTitle></CardHeader>
              <CardContent>
                {students && students.length > 0 ? (
                  <div className="space-y-2">
                    {students.slice(0, 5).map((s) => (
                      <div key={s.UserID} className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50">
                        <div className="min-w-0">
                          <p className="font-medium truncate">{s.Full_Name}</p>
                          <p className="text-sm text-muted-foreground truncate">{s.RegNo}</p>
                        </div>
                        <span className={`shrink-0 text-sm font-medium ${s.IsActive ? 'text-emerald-500' : 'text-red-500'}`}>
                          {s.IsActive ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No students registered</p>
                )}
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn delay={0.2}>
            <Card>
              <CardHeader><CardTitle className="text-lg">Billing Overview</CardTitle></CardHeader>
              <CardContent>
                {pieData.length > 0 ? (
                  <div className="flex items-center gap-4">
                    <div className="h-48 w-48 shrink-0">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                            {pieData.map((entry, index) => (
                              <Cell key={index} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="space-y-3">
                      {pieData.map((d) => (
                        <div key={d.name} className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: d.color }} />
                          <span className="text-sm text-muted-foreground">{d.name}</span>
                          <span className="text-sm font-medium ml-auto">{d.value}</span>
                        </div>
                      ))}
                      <div className="pt-2 border-t">
                        <p className="text-sm text-muted-foreground">Collection Rate</p>
                        <p className="text-lg font-bold">{collectionRate}%</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No billing data available</p>
                )}
              </CardContent>
            </Card>
          </FadeIn>
        </div>
      </div>
    </PageTransition>
  )
}
