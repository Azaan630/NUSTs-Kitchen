import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { FileQuestion, Home } from 'lucide-react'
import { useAuth } from '@/context/auth-context'

export function NotFoundPage() {
  const navigate = useNavigate()
  const { isAuthenticated, role } = useAuth()

  const homePath = !isAuthenticated
    ? '/login'
    : role === 'Admin'
      ? '/admin/dashboard'
      : role === 'Staff'
        ? '/staff/today'
        : '/student/today'

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
        <FileQuestion className="h-10 w-10 text-muted-foreground" />
      </div>
      <h1 className="mt-6 text-4xl font-bold">404</h1>
      <p className="mt-2 text-lg text-muted-foreground">Page not found</p>
      <p className="mt-1 text-sm text-muted-foreground">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Button className="mt-6 gap-2" onClick={() => navigate(homePath)}>
        <Home className="h-4 w-4" /> Go Home
      </Button>
    </div>
  )
}
