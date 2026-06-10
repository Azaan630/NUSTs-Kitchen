import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getRecipes } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { BookOpen } from 'lucide-react'
import type { Recipe } from '@/types'

export function StaffRecipes() {
  const { email } = useAuth()

  const { data: recipes, isLoading } = useQuery({
    queryKey: ['recipes', email],
    queryFn: () => getRecipes(email),
  })

  const columns: Column<Recipe>[] = [
    { key: 'ItemName', header: 'Food Item', sortable: true },
    { key: 'IngredientName', header: 'Ingredient', sortable: true },
    { key: 'Quantity', header: 'Quantity', sortable: true },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Recipes" description="View ingredient-to-food mappings" icon={BookOpen} />
        <Card>
          <CardContent className="pt-6">
            <DataTable
              columns={columns}
              data={(recipes as Recipe[]) || []}
              keyExtractor={(r) => `${r.ItemID}-${r.IngredientID}`}
              searchable searchKeys={['ItemName', 'IngredientName']}
              isLoading={isLoading}
              emptyMessage="No recipes found"
            />
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  )
}
