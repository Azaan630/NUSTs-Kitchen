import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getWeeklyMenu } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/page-header'
import { PageTransition, FadeIn } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { formatDate } from '@/lib/utils'
import { MEAL_TYPES } from '@/lib/constants'
import { Calendar, Star, Sun, Sunset, Moon } from 'lucide-react'

const mealIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  Breakfast: Sun, Lunch: Sunset, Dinner: Moon,
}

export function StudentWeeklyMenu() {
  const { email } = useAuth()
  const { data: menu, isLoading } = useQuery({
    queryKey: ['weeklyMenu', email],
    queryFn: () => getWeeklyMenu(email),
  })

  if (isLoading) return <PageLoading />

  const groupedByDate: Record<string, typeof menu> = {}
  menu?.forEach((item) => {
    if (!groupedByDate[item.Date]) groupedByDate[item.Date] = []
    groupedByDate[item.Date]!.push(item)
  })

  const sortedDates = Object.keys(groupedByDate).sort()

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader
          title="Weekly Menu"
          description="View the menu for the coming week"
          icon={Calendar}
        />

        {sortedDates.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No menu has been scheduled for this week.
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {sortedDates.map((date, dateIdx) => {
              const dayItems = groupedByDate[date]!
              return (
                <FadeIn key={date} delay={dateIdx * 0.05}>
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">{formatDate(date)}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4 sm:grid-cols-3">
                        {MEAL_TYPES.map((mealType) => {
                          const mealItems = dayItems.filter((i) => i.Meal_Type === mealType)
                          const Icon = mealIcons[mealType] || Sun

                          return (
                            <div key={mealType} className="rounded-lg border p-3">
                              <div className="flex items-center gap-2 mb-2">
                                <Icon className="h-4 w-4 text-muted-foreground" />
                                <span className="text-sm font-medium capitalize">{mealType}</span>
                              </div>
                              {mealItems.length > 0 ? (
                                <div className="space-y-2">
                                  {mealItems.map((item) => (
                                    <div key={item.ScheduleID} className="flex items-center justify-between">
                                      <div className="flex items-center gap-1.5 min-w-0">
                                        <span className="text-sm truncate">{item.ItemName}</span>
                                        {item.IsVegetarian && (
                                          <Badge variant="secondary" className="text-[9px] px-1 py-0">
                                            Veg
                                          </Badge>
                                        )}
                                      </div>
                                      <div className="flex items-center gap-2 shrink-0">
                                        {item.Ratings_Average > 0 && (
                                          <span className="text-xs text-amber-500 flex items-center gap-0.5">
                                            <Star className="h-3 w-3 fill-current" />
                                            {item.Ratings_Average.toFixed(1)}
                                          </span>
                                        )}
                                        <span className="text-xs font-medium">Rs.{item.Price}</span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-muted-foreground italic">Not scheduled</p>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </CardContent>
                  </Card>
                </FadeIn>
              )
            })}
          </div>
        )}
      </div>
    </PageTransition>
  )
}
