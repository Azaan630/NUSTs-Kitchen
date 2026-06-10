import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getAllFoodItems } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { Utensils, Star } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'
import type { FoodItem } from '@/types'

export function StaffFoodItems() {
  const { email } = useAuth()

  const { data: items, isLoading } = useQuery({
    queryKey: ['foodItems', email],
    queryFn: () => getAllFoodItems(email),
  })

  const columns: Column<FoodItem>[] = [
    { key: 'ItemName', header: 'Name', sortable: true },
    { key: 'Category', header: 'Category', sortable: true },
    { key: 'Price', header: 'Price', sortable: true, render: (i) => formatCurrency(i.Price) },
    {
      key: 'IsVegetarian', header: 'Type', sortable: true,
      render: (i) => i.IsVegetarian ? <Badge variant="secondary" className="text-xs">Veg</Badge> : <Badge variant="outline" className="text-xs">Non-Veg</Badge>,
    },
    {
      key: 'Ratings_Average', header: 'Rating', sortable: true,
      render: (i) => i.Ratings_Average > 0 ? (
        <div className="flex items-center gap-1 text-amber-500">
          <Star className="h-3.5 w-3.5 fill-current" />
          <span>{i.Ratings_Average.toFixed(1)}</span>
        </div>
      ) : <span className="text-muted-foreground">—</span>,
    },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader title="Food Items" description="View all menu items" icon={Utensils} />
        <Card>
          <CardContent className="pt-6">
            <DataTable
              columns={columns} data={items || []}
              keyExtractor={(i) => i.ItemID}
              searchable searchKeys={['ItemName', 'Category']}
              isLoading={isLoading}
              emptyMessage="No food items found"
            />
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  )
}
