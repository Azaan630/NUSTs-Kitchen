import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '@/context/auth-context'
import { getRecipes, addRecipe, deleteRecipe, getAllFoodItems, getAllIngredients } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Dialog, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { useToast } from '@/hooks/use-toast'
import { recipeFormSchema, type RecipeFormValues } from '@/lib/validations'
import { BookOpen, Plus, Trash2 } from 'lucide-react'
import type { Recipe } from '@/types'

export function AdminRecipes() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()
  const [dialogOpen, setDialogOpen] = useState(false)

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<RecipeFormValues>({
    resolver: zodResolver(recipeFormSchema),
  })

  const { data: recipes, isLoading } = useQuery({ queryKey: ['recipes', email], queryFn: () => getRecipes(email) })
  const { data: foodItems } = useQuery({ queryKey: ['foodItems', email], queryFn: () => getAllFoodItems(email) })
  const { data: ingredients } = useQuery({ queryKey: ['ingredients', email], queryFn: () => getAllIngredients(email) })

  const addMutation = useMutation({
    mutationFn: (data: RecipeFormValues) => addRecipe(email, data.item_id, data.ingredient_id, data.quantity),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['recipes'] }); toast.success('Recipe entry added!'); setDialogOpen(false); reset() },
    onError: (err: Error) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: ({ itemId, ingredientId }: { itemId: number; ingredientId: number }) => deleteRecipe(email, itemId, ingredientId),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['recipes'] }); toast.success('Recipe entry deleted') },
    onError: (err: Error) => toast.error(err.message),
  })

  const onSubmit = (data: RecipeFormValues) => addMutation.mutate(data)

  const columns: Column<Recipe>[] = [
    { key: 'ItemName', header: 'Food Item', sortable: true },
    { key: 'IngredientName', header: 'Ingredient', sortable: true },
    { key: 'Quantity', header: 'Quantity', sortable: true },
    { key: 'actions', header: '', render: (r) => (
      <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
        <Button variant="ghost" size="icon-sm" onClick={() => deleteMutation.mutate({ itemId: r.ItemID, ingredientId: r.IngredientID })}>
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </div>
    )},
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Recipes" description="Map ingredients to food items" icon={BookOpen}
          action={<Button onClick={() => { reset(); setDialogOpen(true) }} className="gap-2"><Plus className="h-4 w-4" /> Add Entry</Button>} />
        <Card>
          <CardContent className="pt-6">
            <DataTable columns={columns} data={(recipes as Recipe[]) || []} keyExtractor={(r) => `${r.ItemID}-${r.IngredientID}`}
              searchable searchKeys={['ItemName', 'IngredientName']} isLoading={isLoading} emptyMessage="No recipes found" />
          </CardContent>
        </Card>
        <Dialog open={dialogOpen} onOpenChange={(open) => { if (!open) { setDialogOpen(false); reset() } }}>
          <DialogHeader><DialogTitle>Add Recipe Entry</DialogTitle></DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="item_id">Food Item</Label>
                <Select {...register('item_id')} options={foodItems?.map((f) => ({ value: String(f.ItemID), label: f.ItemName })) || []} placeholder="Select item" />
                {errors.item_id && <p className="text-xs text-destructive">{errors.item_id.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="ingredient_id">Ingredient</Label>
                <Select {...register('ingredient_id')} options={ingredients?.map((i) => ({ value: String(i.IngredientID), label: `${i.IngredientName} (${i.Unit})` })) || []} placeholder="Select ingredient" />
                {errors.ingredient_id && <p className="text-xs text-destructive">{errors.ingredient_id.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity</Label>
                <Input id="quantity" type="number" step="0.01" {...register('quantity', { valueAsNumber: true })} />
                {errors.quantity && <p className="text-xs text-destructive">{errors.quantity.message}</p>}
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => { setDialogOpen(false); reset() }}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>Add</Button>
            </DialogFooter>
          </form>
        </Dialog>
      </div>
    </PageTransition>
  )
}
