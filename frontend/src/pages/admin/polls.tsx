import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getActivePoll, startPoll, endPoll, getPollResults, getAllFoodItems } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataTable, type Column } from '@/components/data-table'
import { PageHeader } from '@/components/page-header'
import { PageTransition, FadeIn } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { useToast } from '@/hooks/use-toast'
import { MEAL_TYPES } from '@/lib/constants'
import { Vote, Play, Square, BarChart3, Search, Plus, Trash2 } from 'lucide-react'
import type { PollResult, FoodItem } from '@/types'

export function AdminPolls() {
  const { email } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()

  const [startDialogOpen, setStartDialogOpen] = useState(false)
  const [endConfirmOpen, setEndConfirmOpen] = useState(false)
  const [selectedItems, setSelectedItems] = useState<FoodItem[]>([])
  const [mealType, setMealType] = useState<string>('')
  const [itemSearch, setItemSearch] = useState('')

  const { data: activeItems, isLoading: activeLoading } = useQuery({
    queryKey: ['activePoll', email],
    queryFn: () => getActivePoll(email),
  })

  const { data: results, isLoading: resultsLoading } = useQuery({
    queryKey: ['pollResults', email],
    queryFn: () => getPollResults(email),
  })

  const { data: allFoodItems } = useQuery({
    queryKey: ['foodItems', email],
    queryFn: () => getAllFoodItems(email),
  })

  const startPollMutation = useMutation({
    mutationFn: () => startPoll(email, selectedItems.map((i) => i.ItemID), mealType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activePoll'] })
      queryClient.invalidateQueries({ queryKey: ['pollResults'] })
      toast.success('Poll started! Students can now vote.')
      setStartDialogOpen(false)
      setSelectedItems([])
      setMealType('')
      setItemSearch('')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const endPollMutation = useMutation({
    mutationFn: () => endPoll(email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activePoll'] })
      queryClient.invalidateQueries({ queryKey: ['pollResults'] })
      toast.success('Poll ended.')
      setEndConfirmOpen(false)
    },
    onError: (err: Error) => toast.error(err.message),
  })

  const hasActivePoll = activeItems && activeItems.length > 0

  const filteredItems = (allFoodItems || []).filter(
    (item) =>
      !selectedItems.some((s) => s.ItemID === item.ItemID) &&
      (item.ItemName.toLowerCase().includes(itemSearch.toLowerCase()) ||
        item.Category.toLowerCase().includes(itemSearch.toLowerCase())),
  )

  function toggleItem(item: FoodItem) {
    setSelectedItems((prev) =>
      prev.some((s) => s.ItemID === item.ItemID)
        ? prev.filter((s) => s.ItemID !== item.ItemID)
        : [...prev, item],
    )
  }

  function removeItem(itemId: number) {
    setSelectedItems((prev) => prev.filter((s) => s.ItemID !== itemId))
  }

  function handleStartPoll() {
    if (selectedItems.length === 0) {
      toast.error('Select at least one food item')
      return
    }
    if (!mealType) {
      toast.error('Select a meal type')
      return
    }
    startPollMutation.mutate()
  }

  const resultColumns: Column<PollResult>[] = [
    { key: 'ItemName', header: 'Item', sortable: true },
    { key: 'Category', header: 'Category', sortable: true },
    { key: 'Vote_Count', header: 'Votes', sortable: true },
  ]

  return (
    <PageTransition>
      <div className="space-y-6">
        <PageHeader
          title="Poll Management"
          description="Start polls and view voting results"
          icon={Vote}
          action={
            <div className="flex gap-2">
              {hasActivePoll && (
                <Button
                  variant="destructive"
                  onClick={() => setEndConfirmOpen(true)}
                  disabled={endPollMutation.isPending}
                  className="gap-2"
                >
                  <Square className="h-4 w-4" />
                  {endPollMutation.isPending ? 'Ending...' : 'End Poll'}
                </Button>
              )}
              <Button onClick={() => setStartDialogOpen(true)} className="gap-2" disabled={hasActivePoll}>
                <Play className="h-4 w-4" />
                Start New Poll
              </Button>
            </div>
          }
        />

        <div className="grid gap-6 lg:grid-cols-2">
          <FadeIn delay={0.1}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <BarChart3 className="h-5 w-5" /> Active Poll Items
                </CardTitle>
                <CardDescription>Items currently available for voting</CardDescription>
              </CardHeader>
              <CardContent>
                {activeLoading ? (
                  <PageLoading />
                ) : activeItems && activeItems.length > 0 ? (
                  <div className="space-y-3">
                    {activeItems.map((item) => (
                      <div key={item.ItemID} className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{item.ItemName}</span>
                          {item.IsVegetarian && <Badge variant="secondary" className="text-xs">Veg</Badge>}
                        </div>
                        <span className="text-sm font-semibold">Rs. {item.Price}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No active poll. Start one!</p>
                )}
              </CardContent>
            </Card>
          </FadeIn>

          <FadeIn delay={0.2}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Poll Results</CardTitle>
                <CardDescription>Vote counts for all items</CardDescription>
              </CardHeader>
              <CardContent>
                <DataTable
                  columns={resultColumns}
                  data={results || []}
                  keyExtractor={(r) => r.ItemID}
                  searchable
                  searchKeys={['ItemName', 'Category']}
                  searchPlaceholder="Search results..."
                  isLoading={resultsLoading}
                  emptyMessage="No poll results yet"
                />
              </CardContent>
            </Card>
          </FadeIn>
        </div>

        {/* Start Poll Dialog */}
        <Dialog open={startDialogOpen} onOpenChange={(open) => {
          if (!open) {
            setStartDialogOpen(false)
            setSelectedItems([])
            setMealType('')
            setItemSearch('')
          }
        }}>
          <DialogHeader>
            <DialogTitle>Start New Poll</DialogTitle>
            <DialogDescription>
              Select food items and a meal type to start a new voting poll.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Meal Type</Label>
              <Select
                value={mealType}
                onChange={(e) => setMealType(e.target.value)}
                options={MEAL_TYPES.map((m) => ({ value: m, label: m }))}
                placeholder="Select meal type"
              />
            </div>

            <div className="space-y-2">
              <Label>Search Food Items</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name or category..."
                  value={itemSearch}
                  onChange={(e) => setItemSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            {selectedItems.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Items ({selectedItems.length})</Label>
                <div className="flex flex-wrap gap-2">
                  {selectedItems.map((item) => (
                    <Badge key={item.ItemID} variant="secondary" className="gap-1 pr-1">
                      {item.ItemName}
                      <button
                        onClick={() => removeItem(item.ItemID)}
                        className="ml-1 rounded-full p-0.5 hover:bg-muted"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label>Available Items</Label>
              <div className="max-h-48 overflow-y-auto rounded-md border space-y-1 p-2">
                {filteredItems.length > 0 ? (
                  filteredItems.map((item) => (
                    <button
                      key={item.ItemID}
                      onClick={() => toggleItem(item)}
                      className="flex items-center justify-between w-full rounded-md px-3 py-2 text-sm hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span>{item.ItemName}</span>
                        {item.IsVegetarian && <Badge variant="secondary" className="text-xs">Veg</Badge>}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">Rs. {item.Price}</span>
                        <Plus className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </button>
                  ))
                ) : (
                  <p className="text-center text-muted-foreground py-4 text-sm">
                    {itemSearch ? 'No items match your search' : 'No items available'}
                  </p>
                )}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setStartDialogOpen(false); setSelectedItems([]); setMealType(''); setItemSearch('') }}>
              Cancel
            </Button>
            <Button
              onClick={handleStartPoll}
              disabled={startPollMutation.isPending || selectedItems.length === 0 || !mealType}
              className="gap-2"
            >
              <Play className="h-4 w-4" />
              {startPollMutation.isPending ? 'Starting...' : 'Start Poll'}
            </Button>
          </DialogFooter>
        </Dialog>

        {/* End Poll Confirmation */}
        <ConfirmDialog
          open={endConfirmOpen}
          onOpenChange={setEndConfirmOpen}
          title="End Active Poll"
          description="Are you sure you want to end the current poll? Students will no longer be able to vote."
          confirmLabel="End Poll"
          onConfirm={() => endPollMutation.mutate()}
          isLoading={endPollMutation.isPending}
        />
      </div>
    </PageTransition>
  )
}
