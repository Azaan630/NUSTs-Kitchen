import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getAllStudents, registerStaff, updateStaff, deleteStaff, getStaffCategories } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { staffFormSchema, type StaffFormValues } from '@/lib/validations'
import { UserCog, Plus, Pencil, Trash2 } from 'lucide-react'
import type { Staff } from '@/types'

export function AdminStaff() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Staff | null>(null)

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<StaffFormValues>({
    resolver: zodResolver(staffFormSchema),
  })

  const { data: staffList, isLoading } = useQuery({
    queryKey: ['staffList', email],
    queryFn: async () => {
      const students = await getAllStudents(email)
      return students.filter((s) => s.UserID > 0) as unknown as Staff[]
    },
  })

  const { data: categories } = useQuery({
    queryKey: ['staffCategories', email],
    queryFn: () => getStaffCategories(email),
  })

  const createMutation = useMutation({
    mutationFn: (data: StaffFormValues) => registerStaff(email, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staffList'] }); toast.success('Staff registered!'); closeDialog() },
    onError: (err: Error) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: (data: StaffFormValues) => updateStaff(email, { ...data, user_id: editing!.UserID }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staffList'] }); toast.success('Staff updated!'); closeDialog() },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteStaff(email, id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staffList'] }); toast.success('Staff deleted!') },
    onError: (err: Error) => toast.error(err.message),
  })

  function openNew() { setEditing(null); reset({ email: '', full_name: '', category_id: 0, hire_date: '' }); setDialogOpen(true) }
  function closeDialog() { setDialogOpen(false); setEditing(null); reset() }

  const onSubmit = (data: StaffFormValues) => {
    if (editing) updateMutation.mutate(data)
    else createMutation.mutate(data)
  }

  const columns: Column<Staff>[] = [
    { key: 'Full_Name', header: 'Name', sortable: true },
    { key: 'Email', header: 'Email', sortable: true, hideOnMobile: true },
    { key: 'Category', header: 'Category', sortable: true },
    { key: 'Salary', header: 'Salary', sortable: true, render: (s) => `Rs. ${s.Salary.toLocaleString()}` },
    { key: 'actions', header: '', render: (s) => (
      <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
        <Button variant="ghost" size="icon-sm" onClick={() => { setEditing(s); setDialogOpen(true) }}><Pencil className="h-4 w-4" /></Button>
        <Button variant="ghost" size="icon-sm" onClick={() => deleteMutation.mutate(s.UserID)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
      </div>
    )},
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Staff Management" description="Manage kitchen staff" icon={UserCog}
          action={<Button onClick={openNew} className="gap-2"><Plus className="h-4 w-4" /> Add Staff</Button>} />
        <Card>
          <CardContent className="pt-6">
            <DataTable columns={columns} data={staffList || []} keyExtractor={(s) => s.UserID}
              searchable searchKeys={['Full_Name', 'Email', 'Category']} isLoading={isLoading} emptyMessage="No staff found" />
          </CardContent>
        </Card>
        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) closeDialog() }}>
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Staff' : 'Register Staff'}</DialogTitle>
            <DialogDescription>{editing ? 'Update staff information.' : 'Add a new staff member.'}</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input id="full_name" {...register('full_name')} placeholder="Jane Doe" />
                {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" {...register('email')} type="email" placeholder="staff@seecs.edu.pk" />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="category_id">Category</Label>
                <Select {...register('category_id')}
                  options={categories?.map((c) => ({ value: String(c.CategoryID), label: `${c.CategoryName} (Rs. ${c.Salary.toLocaleString()})` })) || []}
                  placeholder="Select category" />
                {errors.category_id && <p className="text-xs text-destructive">{errors.category_id.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="hire_date">Hire Date</Label>
                <Input id="hire_date" type="date" {...register('hire_date')} />
                {errors.hire_date && <p className="text-xs text-destructive">{errors.hire_date.message}</p>}
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeDialog}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>Save</Button>
            </DialogFooter>
          </form>
        </Dialog>
      </div>
    </PageTransition>
  )
}
