import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getTodayMenu } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/page-header'
import { PageTransition, StaggerChildren, staggerItem } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { formatDate } from '@/lib/utils'
import { motion } from 'framer-motion'
import { MEAL_TYPES } from '@/lib/constants'
import { CalendarCheck, Star, Sun, Sunset, Moon } from 'lucide-react'

const mealIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  Breakfast: Sun,
  Lunch: Sunset,
  Dinner: Moon,
}

export function StudentTodayMenu() {
  const { email } = useAuth()
  const { data: menu, isLoading } = useQuery({
    queryKey: ['todayMenu', email],
    queryFn: () => getTodayMenu(email),
    refetchInterval: 60000,
  })

  if (isLoading) return <PageLoading />

  const grouped: Record<string, typeof menu> = {}
  menu?.forEach((item) => {
    if (!grouped[item.Meal_Type]) grouped[item.Meal_Type] = []
    grouped[item.Meal_Type]!.push(item)
  })

  const today = menu?.length && menu[0] ? menu[0].Date : new Date().toISOString().split('T')[0] ?? ''

  return (
    <PageTransition>
      <div className="space-y-6 max-w-4xl mx-auto">
        <PageHeader
          title="Today's Menu"
          description={formatDate(today)}
          icon={CalendarCheck}
        />

        {!menu || menu.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No menu has been scheduled for today.
            </CardContent>
          </Card>
        ) : (
          <StaggerChildren className="grid gap-6">
            {MEAL_TYPES.map((mealType) => {
              const items = grouped[mealType]
              if (!items || items.length === 0) return null
              const Icon = mealIcons[mealType] || Sun

              return (
                <motion.div key={mealType} variants={staggerItem}>
                  <Card className="overflow-hidden transition-all hover:shadow-md">
                    <CardHeader className="bg-muted/30 pb-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                          <Icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-xl capitalize">{mealType}</CardTitle>
                          <p className="text-sm text-muted-foreground">
                            {items.length} item{items.length > 1 ? 's' : ''}
                          </p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <div className="space-y-3">
                        {items.map((item) => (
                          <div
                            key={item.ScheduleID}
                            className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50"
                          >
                            <div className="flex items-center gap-3 min-w-0">
                              <div className="flex flex-col">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium">{item.ItemName}</span>
                                  {item.IsVegetarian && (
                                    <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                                      Veg
                                    </Badge>
                                  )}
                                </div>
                                <span className="text-sm text-muted-foreground">
                                  {item.Category}
                                </span>
                              </div>
                            </div>
                            <div className="flex items-center gap-4 shrink-0">
                              {item.Ratings_Average > 0 && (
                                <div className="flex items-center gap-1 text-sm text-amber-500">
                                  <Star className="h-3.5 w-3.5 fill-current" />
                                  <span>{item.Ratings_Average.toFixed(1)}</span>
                                </div>
                              )}
                              <span className="text-sm font-semibold">
                                Rs. {item.Price}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </StaggerChildren>
        )}
      </div>
    </PageTransition>
  )
}
