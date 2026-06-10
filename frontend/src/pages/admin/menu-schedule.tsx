import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getWeeklyMenu, addToSchedule, removeFromSchedule, getAllFoodItems } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Dialog, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { scheduleFormSchema, type ScheduleFormValues } from '@/lib/validations'
import { MEAL_TYPES } from '@/lib/constants'
import { formatDate } from '@/lib/utils'
import { Calendar, Plus, Trash2 } from 'lucide-react'
import type { MenuScheduleItem } from '@/types'

export function AdminMenuSchedule() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const [dialogOpen, setDialogOpen] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ScheduleFormValues>({
    resolver: zodResolver(scheduleFormSchema),
  })

  const { data: menu, isLoading } = useQuery({
    queryKey: ['weeklyMenu', email],
    queryFn: () => getWeeklyMenu(email),
  })

  const { data: foodItems } = useQuery({
    queryKey: ['foodItems', email],
    queryFn: () => getAllFoodItems(email),
  })

  const addMutation = useMutation({
    mutationFn: (data: ScheduleFormValues) => addToSchedule(email, data.item_id, data.date, data.meal_type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weeklyMenu'] })
      toast.success('Item added to schedule!')
      setDialogOpen(false)
      reset()
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const removeMutation = useMutation({
    mutationFn: ({ itemId, scheduleId }: { itemId: number; scheduleId: number }) =>
      removeFromSchedule(email, itemId, scheduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weeklyMenu'] })
      toast.success('Item removed from schedule')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const onSubmit = (data: ScheduleFormValues) => addMutation.mutate(data)

  const columns: Column<MenuScheduleItem>[] = [
    { key: 'Date', header: 'Date', sortable: true, render: (s) => formatDate(s.Date) },
    { key: 'Meal_Type', header: 'Meal', sortable: true, render: (s) => s.Meal_Type },
    { key: 'ItemName', header: 'Item', sortable: true },
    { key: 'Category', header: 'Category', hideOnMobile: true },
    { key: 'Price', header: 'Price', render: (s) => `Rs. ${s.Price}` },
    {
      key: 'actions', header: '',
      render: (s) => (
        <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
          <Button
            variant="ghost" size="icon-sm"
            onClick={() => removeMutation.mutate({ itemId: s.ItemID, scheduleId: s.ScheduleID })}
            aria-label="Remove from schedule"
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader
          title="Menu Schedule"
          description="Schedule food items for each day and meal time"
          icon={Calendar}
          action={
            <Button onClick={() => { reset({ date: new Date().toISOString().split('T')[0] }); setDialogOpen(true) }} className="gap-2">
              <Plus className="h-4 w-4" /> Add to Schedule
            </Button>
          }
        />
        <Card>
          <CardContent className="pt-6">
            <DataTable
              columns={columns}
              data={menu || []}
              keyExtractor={(s) => s.ScheduleID}
              searchable
              searchKeys={['ItemName', 'Category', 'Meal_Type', 'Date']}
              isLoading={isLoading}
              emptyMessage="No items scheduled"
              emptyDescription="Add food items to the schedule for the coming days."
            />
          </CardContent>
        </Card>

        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) { setDialogOpen(false); reset() } }}>
          <DialogHeader>
            <DialogTitle>Schedule Food Item</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="item_id">Food Item</Label>
                <Select
                  {...register('item_id')}
                  options={foodItems?.map((f) => ({ value: String(f.ItemID), label: f.ItemName })) || []}
                  placeholder="Select item"
                />
                {errors.item_id && <p className="text-xs text-destructive">{errors.item_id.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <input
                  id="date"
                  type="date"
                  {...register('date')}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
                {errors.date && <p className="text-xs text-destructive">{errors.date.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="meal_type">Meal Type</Label>
                <Select
                  {...register('meal_type')}
                  options={MEAL_TYPES.map((m) => ({ value: m, label: m }))}
                  placeholder="Select meal type"
                />
                {errors.meal_type && <p className="text-xs text-destructive">{errors.meal_type.message}</p>}
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => { setDialogOpen(false); reset() }}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>Schedule</Button>
            </DialogFooter>
          </form>
        </Dialog>
      </div>
    </PageTransition>
  )
}
