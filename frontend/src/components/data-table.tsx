import { useState, useMemo, type ReactNode } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  Search,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/empty-state'

export interface Column<T> {
  key: string
  header: string
  sortable?: boolean
  render?: (item: T) => ReactNode
  className?: string
  hideOnMobile?: boolean
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (item: T) => string | number
  searchable?: boolean
  searchKeys?: (keyof T)[]
  searchPlaceholder?: string
  pageSize?: number
  isLoading?: boolean
  emptyMessage?: string
  emptyDescription?: string
  emptyAction?: ReactNode
  onRowClick?: (item: T) => void
  pageSizeOptions?: number[]
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  searchable = false,
  searchKeys,
  searchPlaceholder = 'Search...',
  pageSize = 10,
  isLoading = false,
  emptyMessage = 'No data found',
  emptyDescription,
  emptyAction,
  onRowClick,
  pageSizeOptions = [5, 10, 20, 50],
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [pageSizeState, setPageSizeState] = useState(pageSize)

  const filtered = useMemo(() => {
    if (!search || !searchKeys) return data
    const q = search.toLowerCase()
    return data.filter((item) =>
      searchKeys.some((key) => String((item as Record<string, unknown>)[key as string] ?? '').toLowerCase().includes(q)),
    )
  }, [data, search, searchKeys])

  const sorted = useMemo(() => {
    if (!sortKey) return filtered
    return [...filtered].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortKey] ?? ''
      const bVal = (b as Record<string, unknown>)[sortKey] ?? ''
      const cmp = String(aVal).localeCompare(String(bVal), undefined, { numeric: true })
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [filtered, sortKey, sortDir])

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSizeState))
  const safePage = Math.min(page, totalPages - 1)
  const paginated = sorted.slice(safePage * pageSizeState, (safePage + 1) * pageSizeState)

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
    setPage(0)
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {searchable && <Skeleton className="h-10 w-64" />}
        <div className="rounded-md border">
          <div className="p-4 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (sorted.length === 0) {
    return (
      <EmptyState
        title={emptyMessage}
        description={emptyDescription}
        action={emptyAction}
      />
    )
  }

  return (
    <div className="space-y-4">
      {searchable && (
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={searchPlaceholder}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(0)
            }}
            className="pl-9"
          />
        </div>
      )}

      <div className="rounded-md border overflow-hidden">
        <div className="overflow-x-auto scrollbar-thin">
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((col) => (
                  <TableHead
                    key={col.key}
                    className={cn(
                      col.sortable && 'cursor-pointer select-none',
                      col.hideOnMobile && 'hidden md:table-cell',
                      col.className,
                    )}
                    onClick={col.sortable ? () => handleSort(col.key) : undefined}
                    aria-sort={
                      col.sortable && sortKey === col.key
                        ? sortDir === 'asc'
                          ? 'ascending'
                          : 'descending'
                        : undefined
                    }
                  >
                    <div className="flex items-center gap-1">
                      {col.header}
                      {col.sortable && (
                        <span className="shrink-0">
                          {sortKey === col.key ? (
                            sortDir === 'asc' ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )
                          ) : (
                            <ChevronsUpDown className="h-4 w-4 opacity-30" />
                          )}
                        </span>
                      )}
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginated.map((item) => (
                <TableRow
                  key={keyExtractor(item)}
                  className={cn(onRowClick && 'cursor-pointer')}
                  onClick={() => onRowClick?.(item)}
                >
                  {columns.map((col) => (
                    <TableCell
                      key={col.key}
                      className={cn(col.hideOnMobile && 'hidden md:table-cell', col.className)}
                    >
                      {col.render ? col.render(item) : ((item as Record<string, unknown>)[col.key] as ReactNode)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-sm text-muted-foreground order-2 sm:order-1">
          {safePage * pageSizeState + 1}–
          {Math.min((safePage + 1) * pageSizeState, sorted.length)} of{' '}
          {sorted.length}
        </p>
        <div className="flex items-center gap-2 order-1 sm:order-2">
          <select
            value={pageSizeState}
            onChange={(e) => {
              setPageSizeState(Number(e.target.value))
              setPage(0)
            }}
            className="h-8 rounded-md border border-input bg-background px-2 text-xs"
            aria-label="Rows per page"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size} / page
              </option>
            ))}
          </select>
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setPage(0)}
              disabled={safePage === 0}
              aria-label="First page"
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={safePage === 0}
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={safePage >= totalPages - 1}
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setPage(totalPages - 1)}
              disabled={safePage >= totalPages - 1}
              aria-label="Last page"
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
