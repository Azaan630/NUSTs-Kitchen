import { useState, useMemo } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/auth-context'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn, getInitials } from '@/lib/utils'
import { NAV_ITEMS } from '@/lib/constants'
import {
  LayoutDashboard, Users, UserCog, Utensils, Package, BookOpen,
  Calendar, Receipt, Vote, DoorOpen, CalendarCheck, User,
  Menu, LogOut, ChevronLeft, ChefHat,
} from 'lucide-react'

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard, Users, UserCog, Utensils, Package, BookOpen,
  Calendar, Receipt, Vote, DoorOpen, CalendarCheck, User,
}

export function Layout() {
  const { user, role, logout, email } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  const navItems = useMemo(() => (role ? NAV_ITEMS[role] : []), [role])
  const displayName = user?.Full_Name || email.split('@')[0] || 'User'

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden animate-fade-in"
          onClick={() => setSidebarOpen(false)}
          aria-hidden
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300 ease-in-out lg:static',
          collapsed ? 'w-[68px]' : 'w-64',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        )}
        aria-label="Sidebar navigation"
      >
        <div
          className={cn(
            'flex h-16 shrink-0 items-center border-b border-sidebar-border px-4',
            collapsed ? 'justify-center' : 'justify-between',
          )}
        >
          {!collapsed && (
            <div className="flex items-center gap-3 min-w-0">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary shadow-sm">
                <ChefHat className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold truncate text-sidebar-foreground">NUST's Kitchen</p>
                <p className="text-xs text-sidebar-foreground/60 truncate capitalize">{role}</p>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary shadow-sm">
              <ChefHat className="h-5 w-5 text-primary-foreground" />
            </div>
          )}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex shrink-0 text-sidebar-foreground/60 hover:text-sidebar-foreground"
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <ChevronLeft className={cn('h-4 w-4 transition-transform', collapsed && 'rotate-180')} />
          </Button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin">
          {navItems.map((item) => {
            const Icon = iconMap[item.icon] || LayoutDashboard
            const isActive =
              location.pathname === item.path ||
              (item.path !== '/admin/dashboard' &&
                item.path !== '/student/today' &&
                item.path !== '/staff/today' &&
                location.pathname.startsWith(item.path))

            return (
              <button
                key={item.path}
                onClick={() => { navigate(item.path); setSidebarOpen(false) }}
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground shadow-sm'
                    : 'text-sidebar-foreground/60 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground',
                  collapsed && 'justify-center px-2',
                )}
                title={collapsed ? item.label : undefined}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" aria-hidden />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            )
          })}
        </nav>

        <div className={cn('border-t border-sidebar-border p-3', collapsed && 'flex flex-col items-center gap-2')}>
          {collapsed ? (
            <>
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-primary/10 text-primary text-xs">{getInitials(displayName)}</AvatarFallback>
              </Avatar>
              <Button variant="ghost" size="icon-sm" onClick={handleLogout} className="h-8 w-8 text-sidebar-foreground/60 hover:text-destructive" aria-label="Logout">
                <LogOut className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <div className="flex items-center gap-3">
              <Avatar className="h-9 w-9 shrink-0">
                <AvatarFallback className="bg-primary/10 text-primary text-xs">{getInitials(displayName)}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate text-sidebar-foreground">{displayName}</p>
                <p className="text-xs text-sidebar-foreground/60 truncate">{email}</p>
              </div>
              <Button variant="ghost" size="icon-sm" onClick={handleLogout} className="h-8 w-8 shrink-0 text-sidebar-foreground/60 hover:text-destructive" aria-label="Logout">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 shrink-0 items-center gap-4 border-b bg-background px-4 lg:px-6">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)} className="lg:hidden" aria-label="Open sidebar">
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex-1" />
          <ThemeToggle />
        </header>
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 scrollbar-thin">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
