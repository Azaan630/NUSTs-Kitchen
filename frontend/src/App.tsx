import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from '@/context/theme-context'
import { AuthProvider } from '@/context/auth-context'
import { ProtectedRoute } from '@/components/protected-route'
import { Layout } from '@/components/layout'
import { ErrorBoundary } from '@/components/error-boundary'
import { PageLoading } from '@/components/loading-spinner'

const LoginPage = lazy(() => import('@/pages/login').then((m) => ({ default: m.LoginPage })))
const NotFoundPage = lazy(() => import('@/pages/not-found').then((m) => ({ default: m.NotFoundPage })))

const AdminDashboard = lazy(() => import('@/pages/admin/dashboard').then((m) => ({ default: m.AdminDashboard })))
const AdminStudents = lazy(() => import('@/pages/admin/students').then((m) => ({ default: m.AdminStudents })))
const AdminStaff = lazy(() => import('@/pages/admin/staff').then((m) => ({ default: m.AdminStaff })))
const AdminFoodItems = lazy(() => import('@/pages/admin/food-items').then((m) => ({ default: m.AdminFoodItems })))
const AdminIngredients = lazy(() => import('@/pages/admin/ingredients').then((m) => ({ default: m.AdminIngredients })))
const AdminRecipes = lazy(() => import('@/pages/admin/recipes').then((m) => ({ default: m.AdminRecipes })))
const AdminMenuSchedule = lazy(() => import('@/pages/admin/menu-schedule').then((m) => ({ default: m.AdminMenuSchedule })))
const AdminBills = lazy(() => import('@/pages/admin/bills').then((m) => ({ default: m.AdminBills })))
const AdminPolls = lazy(() => import('@/pages/admin/polls').then((m) => ({ default: m.AdminPolls })))
const AdminMessOff = lazy(() => import('@/pages/admin/mess-off').then((m) => ({ default: m.AdminMessOff })))

const StudentTodayMenu = lazy(() => import('@/pages/student/today-menu').then((m) => ({ default: m.StudentTodayMenu })))
const StudentWeeklyMenu = lazy(() => import('@/pages/student/weekly-menu').then((m) => ({ default: m.StudentWeeklyMenu })))
const StudentVote = lazy(() => import('@/pages/student/vote').then((m) => ({ default: m.StudentVote })))
const StudentMessOff = lazy(() => import('@/pages/student/mess-off').then((m) => ({ default: m.StudentMessOff })))
const StudentBills = lazy(() => import('@/pages/student/bills').then((m) => ({ default: m.StudentBills })))
const StudentProfile = lazy(() => import('@/pages/student/profile').then((m) => ({ default: m.StudentProfile })))

const StaffTodayMenu = lazy(() => import('@/pages/staff/today-menu').then((m) => ({ default: m.StaffTodayMenu })))
const StaffWeeklyMenu = lazy(() => import('@/pages/staff/weekly-menu').then((m) => ({ default: m.StaffWeeklyMenu })))
const StaffFoodItems = lazy(() => import('@/pages/staff/food-items').then((m) => ({ default: m.StaffFoodItems })))
const StaffIngredients = lazy(() => import('@/pages/staff/ingredients').then((m) => ({ default: m.StaffIngredients })))
const StaffRecipes = lazy(() => import('@/pages/staff/recipes').then((m) => ({ default: m.StaffRecipes })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
    },
  },
})

function AdminRoutes() {
  return (
    <ProtectedRoute allowedRoles={['Admin']}>
      <Layout />
    </ProtectedRoute>
  )
}

function StaffRoutes() {
  return (
    <ProtectedRoute allowedRoles={['Staff']}>
      <Layout />
    </ProtectedRoute>
  )
}

function StudentRoutes() {
  return (
    <ProtectedRoute allowedRoles={['Student']}>
      <Layout />
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <AuthProvider>
            <BrowserRouter>
              <Suspense fallback={<PageLoading />}>
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/" element={<Navigate to="/login" replace />} />

                  {/* Admin routes */}
                  <Route path="/admin" element={<AdminRoutes />}>
                    <Route index element={<Navigate to="dashboard" replace />} />
                    <Route path="dashboard" element={<AdminDashboard />} />
                    <Route path="students" element={<AdminStudents />} />
                    <Route path="staff" element={<AdminStaff />} />
                    <Route path="food-items" element={<AdminFoodItems />} />
                    <Route path="ingredients" element={<AdminIngredients />} />
                    <Route path="recipes" element={<AdminRecipes />} />
                    <Route path="menu-schedule" element={<AdminMenuSchedule />} />
                    <Route path="bills" element={<AdminBills />} />
                    <Route path="polls" element={<AdminPolls />} />
                    <Route path="mess-off" element={<AdminMessOff />} />
                  </Route>

                  {/* Student routes */}
                  <Route path="/student" element={<StudentRoutes />}>
                    <Route index element={<Navigate to="today" replace />} />
                    <Route path="today" element={<StudentTodayMenu />} />
                    <Route path="weekly" element={<StudentWeeklyMenu />} />
                    <Route path="vote" element={<StudentVote />} />
                    <Route path="mess-off" element={<StudentMessOff />} />
                    <Route path="bills" element={<StudentBills />} />
                    <Route path="profile" element={<StudentProfile />} />
                  </Route>

                  {/* Staff routes */}
                  <Route path="/staff" element={<StaffRoutes />}>
                    <Route index element={<Navigate to="today" replace />} />
                    <Route path="today" element={<StaffTodayMenu />} />
                    <Route path="weekly" element={<StaffWeeklyMenu />} />
                    <Route path="food-items" element={<StaffFoodItems />} />
                    <Route path="ingredients" element={<StaffIngredients />} />
                    <Route path="recipes" element={<StaffRecipes />} />
                  </Route>

                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>
            </BrowserRouter>
            <Toaster
              position="top-right"
              toastOptions={{
                style: {
                  borderRadius: '8px',
                  background: 'hsl(var(--card))',
                  color: 'hsl(var(--foreground))',
                  border: '1px solid hsl(var(--border))',
                },
              }}
            />
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
