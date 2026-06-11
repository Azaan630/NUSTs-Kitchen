import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getAllIngredients, createIngredient, updateIngredient, deleteIngredient } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { ingredientFormSchema, type IngredientFormValues } from '@/lib/validations'
import { Package, Plus, Pencil, Trash2 } from 'lucide-react'
import type { Ingredient } from '@/types'
import { formatCurrency } from '@/lib/utils'

export function AdminIngredients() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Ingredient | null>(null)
  const [deleting, setDeleting] = useState<Ingredient | null>(null)

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<IngredientFormValues>({
    resolver: zodResolver(ingredientFormSchema),
  })

  const { data: ingredients, isLoading } = useQuery({
    queryKey: ['ingredients', email], queryFn: () => getAllIngredients(email),
  })

  const createMutation = useMutation({
    mutationFn: (data: IngredientFormValues) => createIngredient(email, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ingredients'] }); toast.success('Ingredient created!'); closeDialog() },
    onError: (err: Error) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: (data: IngredientFormValues) => updateIngredient(email, editing!.IngredientID, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ingredients'] }); toast.success('Ingredient updated!'); closeDialog() },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteIngredient(email, id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ingredients'] }); toast.success('Ingredient deleted!') },
    onError: (err: Error) => toast.error(err.message),
  })

  function openNew() { setEditing(null); reset({ ingredient_name: '', unit: '', stock_quantity: 0, unit_price: 0 }); setDialogOpen(true) }
  function closeDialog() { setDialogOpen(false); setEditing(null); reset() }

  const onSubmit = (data: IngredientFormValues) => {
    if (editing) updateMutation.mutate(data)
    else createMutation.mutate(data)
  }

  const columns: Column<Ingredient>[] = [
    { key: 'IngredientName', header: 'Name', sortable: true },
    { key: 'Unit', header: 'Unit', sortable: true, hideOnMobile: true },
    { key: 'StockQuantity', header: 'Stock', sortable: true, render: (i) => `${i.StockQuantity} ${i.Unit}` },
    { key: 'UnitPrice', header: 'Unit Price', sortable: true, render: (i) => formatCurrency(i.UnitPrice) },
    { key: 'actions', header: '', render: (i) => (
      <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
        <Button variant="ghost" size="icon-sm" onClick={() => { setEditing(i); reset({ ingredient_name: i.IngredientName, unit: i.Unit, stock_quantity: i.StockQuantity, unit_price: i.UnitPrice }); setDialogOpen(true) }}><Pencil className="h-4 w-4" /></Button>
        <Button variant="ghost" size="icon-sm" onClick={() => setDeleting(i)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
      </div>
    )},
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Ingredients" description="Manage ingredient inventory" icon={Package}
          action={<Button onClick={openNew} className="gap-2"><Plus className="h-4 w-4" /> Add Ingredient</Button>} />
        <Card>
          <CardContent className="pt-6">
            <DataTable columns={columns} data={ingredients || []} keyExtractor={(i) => i.IngredientID}
              searchable searchKeys={['IngredientName', 'Unit']} isLoading={isLoading} emptyMessage="No ingredients found" />
          </CardContent>
        </Card>
        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) closeDialog() }}>
          <DialogHeader><DialogTitle>{editing ? 'Edit Ingredient' : 'Add Ingredient'}</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="ingredient_name">Ingredient Name</Label>
                <Input id="ingredient_name" {...register('ingredient_name')} />
                {errors.ingredient_name && <p className="text-xs text-destructive">{errors.ingredient_name.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="unit">Unit</Label>
                  <Input id="unit" {...register('unit')} placeholder="kg, liters" />
                  {errors.unit && <p className="text-xs text-destructive">{errors.unit.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unit_price">Unit Price (Rs)</Label>
                  <Input id="unit_price" type="number" step="0.01" {...register('unit_price', { valueAsNumber: true })} />
                  {errors.unit_price && <p className="text-xs text-destructive">{errors.unit_price.message}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="stock_quantity">Stock Quantity</Label>
                <Input id="stock_quantity" type="number" step="0.01" {...register('stock_quantity', { valueAsNumber: true })} />
                {errors.stock_quantity && <p className="text-xs text-destructive">{errors.stock_quantity.message}</p>}
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeDialog}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>Save</Button>
            </DialogFooter>
          </form>
        </Dialog>

        <ConfirmDialog
          open={!!deleting}
          onOpenChange={(open) => { if (!open) setDeleting(null) }}
          title="Delete Ingredient"
          description={`Are you sure you want to delete "${deleting?.IngredientName}"? This action cannot be undone.`}
          onConfirm={() => {
            if (deleting) {
              deleteMutation.mutate(deleting.IngredientID)
              setDeleting(null)
            }
          }}
          isLoading={deleteMutation.isPending}
        />
      </div>
    </PageTransition>
  )
}
