import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getAllFoodItems, createFoodItem, updateFoodItem, deleteFoodItem } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { foodItemFormSchema, type FoodItemFormValues } from '@/lib/validations'
import { Utensils, Plus, Pencil, Trash2, Star } from 'lucide-react'
import type { FoodItem } from '@/types'
import { formatCurrency } from '@/lib/utils'

export function AdminFoodItems() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<FoodItem | null>(null)
  const [deleting, setDeleting] = useState<FoodItem | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FoodItemFormValues>({
    resolver: zodResolver(foodItemFormSchema),
    defaultValues: { is_vegetarian: false },
  })

  const { data: items, isLoading } = useQuery({
    queryKey: ['foodItems', email],
    queryFn: () => getAllFoodItems(email),
  })

  const createMutation = useMutation({
    mutationFn: (data: FoodItemFormValues) => createFoodItem(email, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['foodItems'] })
      toast.success('Food item created!')
      closeDialog()
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: (data: FoodItemFormValues) => updateFoodItem(email, editing!.ItemID, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['foodItems'] })
      toast.success('Food item updated!')
      closeDialog()
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteFoodItem(email, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['foodItems'] })
      toast.success('Food item deleted!')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  function openNew() {
    setEditing(null)
    reset({ item_name: '', category: '', price: 0, is_vegetarian: false, description: '' })
    setDialogOpen(true)
  }

  function openEdit(item: FoodItem) {
    setEditing(item)
    reset({
      item_name: item.ItemName,
      category: item.Category,
      price: item.Price,
      is_vegetarian: item.IsVegetarian,
      description: item.Description ?? '',
    })
    setDialogOpen(true)
  }

  function closeDialog() {
    setDialogOpen(false)
    setEditing(null)
    reset()
  }

  const onSubmit = (data: FoodItemFormValues) => {
    if (editing) {
      updateMutation.mutate(data)
    } else {
      createMutation.mutate(data)
    }
  }

  const columns: Column<FoodItem>[] = [
    { key: 'ItemName', header: 'Name', sortable: true },
    { key: 'Category', header: 'Category', sortable: true },
    { key: 'Price', header: 'Price', sortable: true, render: (i) => formatCurrency(i.Price) },
    {
      key: 'IsVegetarian',
      header: 'Type',
      sortable: true,
      render: (i) =>
        i.IsVegetarian ? (
          <Badge variant="secondary" className="text-xs">
            Veg
          </Badge>
        ) : (
          <Badge variant="outline" className="text-xs">
            Non-Veg
          </Badge>
        ),
    },
    {
      key: 'Vote_Count',
      header: 'Votes',
      sortable: true,
    },
    {
      key: 'Ratings_Average',
      header: 'Rating',
      sortable: true,
      render: (i) =>
        i.Ratings_Average > 0 ? (
          <div className="flex items-center gap-1 text-amber-500">
            <Star className="h-3.5 w-3.5 fill-current" />
            <span>{i.Ratings_Average.toFixed(1)}</span>
          </div>
        ) : (
          <span className="text-muted-foreground">—</span>
        ),
    },
    {
      key: 'actions',
      header: '',
      render: (i) => (
        <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
          <Button variant="ghost" size="icon-sm" onClick={() => openEdit(i)} aria-label="Edit item">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" onClick={() => setDeleting(i)} aria-label="Delete item">
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
          title="Food Items"
          description="Manage all menu food items"
          icon={Utensils}
          action={
            <Button onClick={openNew} className="gap-2">
              <Plus className="h-4 w-4" /> Add Item
            </Button>
          }
        />

        <Card>
          <CardContent className="pt-6">
            <DataTable
              columns={columns}
              data={items || []}
              keyExtractor={(i) => i.ItemID}
              searchable
              searchKeys={['ItemName', 'Category']}
              isLoading={isLoading}
              emptyMessage="No food items found"
            />
          </CardContent>
        </Card>

        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) closeDialog() }}>
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Food Item' : 'Create Food Item'}</DialogTitle>
            <DialogDescription>
              {editing ? 'Update the food item details.' : 'Add a new item to the menu.'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="item_name">Item Name</Label>
                <Input id="item_name" {...register('item_name')} placeholder="Chicken Biryani" />
                {errors.item_name && <p className="text-xs text-destructive">{errors.item_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input id="category" {...register('category')} placeholder="Main Course, Dessert..." />
                {errors.category && <p className="text-xs text-destructive">{errors.category.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="price">Price (Rs)</Label>
                  <Input id="price" type="number" min="0" {...register('price', { valueAsNumber: true })} />
                  {errors.price && <p className="text-xs text-destructive">{errors.price.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label>Vegetarian</Label>
                  <div className="flex items-center gap-2 pt-2">
                    <input
                      type="checkbox"
                      id="is_vegetarian"
                      className="h-4 w-4 rounded border-gray-300"
                      {...register('is_vegetarian')}
                    />
                    <Label htmlFor="is_vegetarian" className="cursor-pointer font-normal">
                      Yes
                    </Label>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input id="description" {...register('description')} placeholder="Optional description..." />
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
          title="Delete Food Item"
          description={`Are you sure you want to delete "${deleting?.ItemName}"? This action cannot be undone.`}
          onConfirm={() => {
            if (deleting) {
              deleteMutation.mutate(deleting.ItemID)
              setDeleting(null)
            }
          }}
          isLoading={deleteMutation.isPending}
        />
      </div>
    </PageTransition>
  )
}
