import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/auth-context'
import { getMe } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { PageHeader } from '@/components/page-header'
import { PageTransition } from '@/components/page-transition'
import { PageLoading } from '@/components/loading-spinner'
import { formatDate, getInitials } from '@/lib/utils'
import { User, Mail, Calendar, Shield } from 'lucide-react'

export function StudentProfile() {
  const { email, user } = useAuth()

  const { data: profile, isLoading } = useQuery({
    queryKey: ['me', email],
    queryFn: () => getMe(email),
    enabled: !!email,
  })

  if (isLoading) return <PageLoading />

  const displayUser = profile || user

  if (!displayUser) {
    return (
      <PageTransition>
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Unable to load profile information.
          </CardContent>
        </Card>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6 max-w-2xl mx-auto">
        <PageHeader title="My Profile" description="Your account information" icon={User} />

        <Card>
          <CardHeader className="flex flex-row items-center gap-4 pb-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-lg">{getInitials(displayUser.Full_Name)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-xl">{displayUser.Full_Name}</CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary">{displayUser.Account_Type}</Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-3 rounded-lg border p-3">
                <Mail className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{displayUser.Email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-lg border p-3">
                <Shield className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Account Type</p>
                  <p className="font-medium">{displayUser.Account_Type}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-lg border p-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Registered</p>
                  <p className="font-medium">{formatDate(displayUser.RegisteredAt)}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  )
}
