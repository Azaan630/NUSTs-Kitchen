import { useState, type FormEvent } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { ThemeToggle } from '@/components/theme-toggle'
import { ChefHat, Loader2, Mail, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return
    try {
      const user = await login(email.trim())
      const role = user.Account_Type
      const defaultPath =
        role === 'Admin' ? '/admin/dashboard' : role === 'Staff' ? '/staff/today' : '/student/today'
      navigate(from || defaultPath, { replace: true })
    } catch {
      // handled by AuthProvider
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5" />
      <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-to-bl from-primary/5 to-transparent rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-primary/5 to-transparent rounded-full blur-3xl" />

      <div className="absolute top-4 right-4 z-10">
        <ThemeToggle />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md relative z-10"
      >
        <Card className="border-primary/10 shadow-2xl shadow-primary/5 backdrop-blur-sm">
          <CardHeader className="text-center pb-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary shadow-lg shadow-primary/20"
            >
              <ChefHat className="h-8 w-8 text-primary-foreground" />
            </motion.div>
            <CardTitle className="text-2xl">NUST's Kitchen</CardTitle>
            <CardDescription>Mess Management System — Sign in with your NUST email</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email" type="email" placeholder="you@seecs.edu.pk"
                    value={email} onChange={(e) => setEmail(e.target.value)}
                    className="pl-9 h-11" autoFocus required autoComplete="email"
                  />
                </div>
              </div>
              <Button type="submit" className="w-full h-11 gap-2" disabled={isLoading || !email.trim()}>
                {isLoading ? (
                  <><Loader2 className="h-4 w-4 animate-spin" /> Verifying...</>
                ) : (
                  <><Sparkles className="h-4 w-4" /> Continue</>
                )}
              </Button>
            </form>
            <p className="mt-6 text-center text-xs text-muted-foreground">
              Use your registered university email to sign in
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
