import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/auth-context'
import { PageLoading } from '@/components/loading-spinner'
import type { AccountType } from '@/types'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: AccountType[]
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, role, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <PageLoading />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    const defaultPath =
      role === 'Admin' ? '/admin/dashboard' : role === 'Staff' ? '/staff/today' : '/student/today'
    return <Navigate to={defaultPath} replace />
  }

  return <>{children}</>
}
