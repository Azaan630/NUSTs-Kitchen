import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { ThemeToggle } from '@/components/theme-toggle'
import { ChefHat, Loader2, UserPlus, ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'
import { submitRegistrationRequest } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

const SEX_OPTIONS = [
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
]

const STAFF_CATEGORIES = [
  { value: 'Chef', label: 'Chef' },
  { value: 'Helper', label: 'Helper' },
  { value: 'Cleaner', label: 'Cleaner' },
]

export function RegisterPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [accountType, setAccountType] = useState('')
  const [form, setForm] = useState({
    First_Name: '',
    Last_Name: '',
    Email: '',
    Sex: '',
    DoB: '',
    Department: '',
    Contact_Number: '',
    Address: '',
    Father_Name: '',
    Hostel_Name: '',
    Room_Number: '',
    Category: '',
  })

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const payload = {
        ...form,
        Email: form.Email,
        Account_Type: accountType,
        DoB: form.DoB || undefined,
      }
      await submitRegistrationRequest(payload)
      setIsSuccess(true)
      toast.success('Registration request submitted! Wait for admin approval.')
    } catch (err: any) {
      toast.error(err.message || 'Submission failed')
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5" />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md relative z-10"
        >
          <Card className="border-primary/10 shadow-2xl">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary shadow-lg">
                <UserPlus className="h-8 w-8 text-primary-foreground" />
              </div>
              <CardTitle className="text-2xl">Request Submitted!</CardTitle>
              <CardDescription>
                Your registration request has been sent to the admin for approval. You'll be able to sign in once approved.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <Button onClick={() => navigate('/login')} className="w-full">
                Go to Login
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    )
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
        className="w-full max-w-lg relative z-10"
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
            <CardTitle className="text-2xl">Create Account</CardTitle>
            <CardDescription>Register for the Mess Management System</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Account Type */}
              <div className="space-y-2">
                <Label>Account Type *</Label>
                <Select
                  value={accountType}
                  onChange={(e) => setAccountType(e.target.value)}
                  options={[
                    { value: 'Student', label: 'Student' },
                    { value: 'Staff', label: 'Staff' },
                  ]}
                  placeholder="Select account type"
                  required
                />
              </div>

              {/* Full Name */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="First_Name">First Name *</Label>
                  <Input id="First_Name" value={form.First_Name} onChange={(e) => update('First_Name', e.target.value)} placeholder="John" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="Last_Name">Last Name *</Label>
                  <Input id="Last_Name" value={form.Last_Name} onChange={(e) => update('Last_Name', e.target.value)} placeholder="Doe" required />
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="Email">Email *</Label>
                <Input id="Email" type="email" value={form.Email} onChange={(e) => update('Email', e.target.value)} placeholder="you@seecs.edu.pk" required />
              </div>

              {/* Sex */}
              <div className="space-y-2">
                <Label>Sex</Label>
                <Select
                  value={form.Sex}
                  onChange={(e) => update('Sex', e.target.value)}
                  options={SEX_OPTIONS}
                  placeholder="Select sex"
                />
              </div>

              {accountType === 'Student' && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor="DoB">Date of Birth</Label>
                      <Input id="DoB" type="date" value={form.DoB} onChange={(e) => update('DoB', e.target.value)} />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="Department">Department</Label>
                      <Input id="Department" value={form.Department} onChange={(e) => update('Department', e.target.value)} placeholder="CS, SE, EE..." />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="Contact_Number">Contact Number</Label>
                    <Input id="Contact_Number" value={form.Contact_Number} onChange={(e) => update('Contact_Number', e.target.value)} placeholder="03XX-XXXXXXX" />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="Address">Address</Label>
                    <Input id="Address" value={form.Address} onChange={(e) => update('Address', e.target.value)} placeholder="Home address" />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="Father_Name">Father's Name</Label>
                    <Input id="Father_Name" value={form.Father_Name} onChange={(e) => update('Father_Name', e.target.value)} placeholder="Father's name" />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor="Hostel_Name">Hostel</Label>
                      <Input id="Hostel_Name" value={form.Hostel_Name} onChange={(e) => update('Hostel_Name', e.target.value)} placeholder="Hostel name" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="Room_Number">Room No.</Label>
                      <Input id="Room_Number" value={form.Room_Number} onChange={(e) => update('Room_Number', e.target.value)} placeholder="Room number" />
                    </div>
                  </div>
                </>
              )}

              {accountType === 'Staff' && (
                <div className="space-y-2">
                  <Label>Staff Category</Label>
                  <Select
                    value={form.Category}
                    onChange={(e) => update('Category', e.target.value)}
                    options={STAFF_CATEGORIES}
                    placeholder="Select category"
                  />
                </div>
              )}

              <Button type="submit" className="w-full h-11 gap-2" disabled={isLoading || !accountType || !form.First_Name || !form.Last_Name || !form.Email}>
                {isLoading ? (
                  <><Loader2 className="h-4 w-4 animate-spin" /> Submitting...</>
                ) : (
                  <><UserPlus className="h-4 w-4" /> Register</>
                )}
              </Button>

              <div className="text-center">
                <Link to="/login" className="text-sm text-muted-foreground hover:text-primary inline-flex items-center gap-1">
                  <ArrowLeft className="h-3 w-3" /> Already have an account? Sign in
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
