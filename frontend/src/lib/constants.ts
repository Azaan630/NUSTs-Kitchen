export const API_URL = import.meta.env.VITE_API_URL || '/api'
export const APP_NAME = import.meta.env.VITE_APP_NAME || "NUST's Kitchen"

export const MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner'] as const

export const NAV_ITEMS = {
  Admin: [
    { label: 'Dashboard', path: '/admin/dashboard', icon: 'LayoutDashboard' },
    { label: 'Students', path: '/admin/students', icon: 'Users' },
    { label: 'Staff', path: '/admin/staff', icon: 'UserCog' },
    { label: 'Food Items', path: '/admin/food-items', icon: 'Utensils' },
    { label: 'Ingredients', path: '/admin/ingredients', icon: 'Package' },
    { label: 'Recipes', path: '/admin/recipes', icon: 'BookOpen' },
    { label: 'Menu Schedule', path: '/admin/menu-schedule', icon: 'Calendar' },
    { label: 'Bills', path: '/admin/bills', icon: 'Receipt' },
    { label: 'Polls', path: '/admin/polls', icon: 'Vote' },
    { label: 'Mess Off', path: '/admin/mess-off', icon: 'DoorOpen' },
  ],
  Staff: [
    { label: "Today's Menu", path: '/staff/today', icon: 'CalendarCheck' },
    { label: 'Weekly Menu', path: '/staff/weekly', icon: 'Calendar' },
    { label: 'Food Items', path: '/staff/food-items', icon: 'Utensils' },
    { label: 'Ingredients', path: '/staff/ingredients', icon: 'Package' },
    { label: 'Recipes', path: '/staff/recipes', icon: 'BookOpen' },
  ],
  Student: [
    { label: "Today's Menu", path: '/student/today', icon: 'CalendarCheck' },
    { label: 'Weekly Menu', path: '/student/weekly', icon: 'Calendar' },
    { label: 'Vote on Menu', path: '/student/vote', icon: 'Vote' },
    { label: 'Mess Off', path: '/student/mess-off', icon: 'DoorOpen' },
    { label: 'My Bills', path: '/student/bills', icon: 'Receipt' },
    { label: 'Profile', path: '/student/profile', icon: 'User' },
  ],
} as const

export type NavItem = (typeof NAV_ITEMS)[keyof typeof NAV_ITEMS][number]
