import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getAllIngredients } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { Package } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'
import type { Ingredient } from '@/types'

export function StaffIngredients() {
  const { email } = useAuth()

  const { data: ingredients, isLoading } = useQuery({
    queryKey: ['ingredients', email],
    queryFn: () => getAllIngredients(email),
  })

  const columns: Column<Ingredient>[] = [
    { key: 'IngredientName', header: 'Name', sortable: true },
    { key: 'Unit', header: 'Unit', sortable: true },
    { key: 'StockQuantity', header: 'Stock', sortable: true, render: (i) => `${i.StockQuantity} ${i.Unit}` },
    { key: 'UnitPrice', header: 'Unit Price', sortable: true, render: (i) => formatCurrency(i.UnitPrice) },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Ingredients" description="View ingredient inventory" icon={Package} />
        <Card>
          <CardContent className="pt-6">
            <DataTable
              columns={columns} data={ingredients || []}
              keyExtractor={(i) => i.IngredientID}
              searchable searchKeys={['IngredientName', 'Unit']}
              isLoading={isLoading}
              emptyMessage="No ingredients found"
            />
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  )
}
