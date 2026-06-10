import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getActivePoll, castVote } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { useToast } from '@/hooks/use-toast'
import { Vote, ThumbsUp } from 'lucide-react'

export function StudentVote() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const { data: activeItems, isLoading } = useQuery({
    queryKey: ['activePoll', email],
    queryFn: () => getActivePoll(email),
    refetchInterval: 30000,
  })

  const voteMutation = useMutation({
    mutationFn: (itemId: number) => castVote(email, 0, itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activePoll'] })
      toast.success('Your vote has been cast!')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  if (isLoading) return <PageLoading />

  return (
    <PageTransition>
      <div className="space-y-6 max-w-2xl mx-auto">
        <PageHeader
          title="Vote on Menu"
          description="Cast your vote for tomorrow's menu items"
          icon={Vote}
        />

        {!activeItems || activeItems.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No active poll at the moment. Check back later!
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {activeItems.map((item) => (
              <Card key={item.ItemID} className="transition-all hover:shadow-md">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{item.ItemName}</CardTitle>
                      <p className="text-sm text-muted-foreground">{item.Category}</p>
                    </div>
                    {item.IsVegetarian && (
                      <Badge variant="secondary" className="text-xs">Veg</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold">Rs. {item.Price}</span>
                    <Button
                      size="sm"
                      onClick={() => voteMutation.mutate(item.ItemID)}
                      disabled={voteMutation.isPending}
                      className="gap-1.5"
                    >
                      <ThumbsUp className="h-4 w-4" />
                      Vote
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </PageTransition>
  )
}
