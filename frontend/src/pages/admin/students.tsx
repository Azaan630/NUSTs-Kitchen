import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getAllStudents, registerStudent, updateStudent, deleteStudent } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { studentFormSchema, type StudentFormValues } from '@/lib/validations'
import { Users, Plus, Pencil, Trash2 } from 'lucide-react'
import type { Student } from '@/types'

export function AdminStudents() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Student | null>(null)

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<StudentFormValues>({
    resolver: zodResolver(studentFormSchema),
  })

  const { data: students, isLoading } = useQuery({
    queryKey: ['students', email],
    queryFn: () => getAllStudents(email),
  })

  const createMutation = useMutation({
    mutationFn: (data: StudentFormValues) => registerStudent(email, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['students'] }); toast.success('Student registered!'); closeDialog() },
    onError: (err: Error) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: (data: StudentFormValues) => updateStudent(email, editing!.UserID, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['students'] }); toast.success('Student updated!'); closeDialog() },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteStudent(email, id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['students'] }); toast.success('Student deleted!') },
    onError: (err: Error) => toast.error(err.message),
  })

  function openNew() { setEditing(null); reset({ email: '', full_name: '', reg_no: '' }); setDialogOpen(true) }
  function closeDialog() { setDialogOpen(false); setEditing(null); reset() }

  const onSubmit = (data: StudentFormValues) => {
    if (editing) updateMutation.mutate(data)
    else createMutation.mutate(data)
  }

  const columns: Column<Student>[] = [
    { key: 'Full_Name', header: 'Name', sortable: true },
    { key: 'Email', header: 'Email', sortable: true },
    { key: 'RegNo', header: 'Reg No', sortable: true, hideOnMobile: true },
    { key: 'Balance', header: 'Balance', sortable: true, render: (s) => `Rs. ${s.Balance}` },
    { key: 'IsActive', header: 'Status', sortable: true, render: (s) => <Badge variant={s.IsActive ? 'success' : 'secondary'}>{s.IsActive ? 'Active' : 'Inactive'}</Badge> },
    { key: 'actions', header: '', render: (s) => (
      <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
        <Button variant="ghost" size="icon-sm" onClick={() => { setEditing(s); reset({ email: s.Email, full_name: s.Full_Name, reg_no: s.RegNo }); setDialogOpen(true) }}><Pencil className="h-4 w-4" /></Button>
        <Button variant="ghost" size="icon-sm" onClick={() => deleteMutation.mutate(s.UserID)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
      </div>
    )},
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Students" description="Manage all registered students" icon={Users}
          action={<Button onClick={openNew} className="gap-2"><Plus className="h-4 w-4" /> Add Student</Button>} />
        <Card>
          <CardContent className="pt-6">
            <DataTable columns={columns} data={students || []} keyExtractor={(s) => s.UserID}
              searchable searchKeys={['Full_Name', 'Email', 'RegNo']} isLoading={isLoading} emptyMessage="No students found" />
          </CardContent>
        </Card>
        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) closeDialog() }}>
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Student' : 'Register Student'}</DialogTitle>
            <DialogDescription>{editing ? 'Update student information.' : 'Add a new student to the system.'}</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input id="full_name" {...register('full_name')} placeholder="John Doe" />
                {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" {...register('email')} placeholder="student@seecs.edu.pk" type="email" />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="reg_no">Registration No</Label>
                <Input id="reg_no" {...register('reg_no')} placeholder="SEECS-XX-XXX" />
                {errors.reg_no && <p className="text-xs text-destructive">{errors.reg_no.message}</p>}
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeDialog}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>{editing ? 'Update' : 'Register'}</Button>
            </DialogFooter>
          </form>
        </Dialog>
      </div>
    </PageTransition>
  )
}
