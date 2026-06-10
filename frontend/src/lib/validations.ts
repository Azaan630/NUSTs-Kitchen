import { z } from 'zod'

export const emailSchema = z.string().email('Invalid email address').min(1, 'Email is required')

export const studentFormSchema = z.object({
  email: emailSchema,
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  reg_no: z.string().min(1, 'Registration number is required'),
  mess_package: z.string().optional(),
  mess_package_start: z.string().optional(),
  mess_package_end: z.string().optional(),
})

export const staffFormSchema = z.object({
  email: emailSchema,
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  category_id: z.coerce.number().min(1, 'Category is required'),
  hire_date: z.string().min(1, 'Hire date is required'),
})

export const foodItemFormSchema = z.object({
  item_name: z.string().min(1, 'Item name is required'),
  category: z.string().min(1, 'Category is required'),
  price: z.coerce.number().min(1, 'Price must be greater than 0'),
  is_vegetarian: z.boolean().default(false),
  description: z.string().optional(),
})

export const ingredientFormSchema = z.object({
  ingredient_name: z.string().min(1, 'Ingredient name is required'),
  unit: z.string().min(1, 'Unit is required'),
  stock_quantity: z.coerce.number().min(0, 'Stock cannot be negative'),
  unit_price: z.coerce.number().min(0, 'Unit price cannot be negative'),
})

export const billFormSchema = z.object({
  user_id: z.coerce.number().min(1, 'Student is required'),
  month: z.string().min(1, 'Month is required'),
  year: z.coerce.number().min(2020, 'Invalid year'),
  total_days: z.coerce.number().min(1, 'Total days must be at least 1'),
  mess_off_days: z.coerce.number().min(0, 'Cannot be negative'),
  daily_rate: z.coerce.number().min(1, 'Daily rate is required'),
  total_amount: z.coerce.number().min(1, 'Total amount is required'),
  due_date: z.string().min(1, 'Due date is required'),
})

export const paymentFormSchema = z.object({
  amount_paid: z.coerce.number().min(1, 'Amount must be greater than 0'),
  payment_date: z.string().min(1, 'Payment date is required'),
  payment_method: z.string().min(1, 'Payment method is required'),
})

export const messOffFormSchema = z
  .object({
    start_date: z.string().min(1, 'Start date is required'),
    end_date: z.string().min(1, 'End date is required'),
  })
  .refine((data) => new Date(data.end_date) >= new Date(data.start_date), {
    message: 'End date must be after or on start date',
    path: ['end_date'],
  })

export const scheduleFormSchema = z.object({
  item_id: z.coerce.number().min(1, 'Food item is required'),
  date: z.string().min(1, 'Date is required'),
  meal_type: z.string().min(1, 'Meal type is required'),
})

export const recipeFormSchema = z.object({
  item_id: z.coerce.number().min(1, 'Food item is required'),
  ingredient_id: z.coerce.number().min(1, 'Ingredient is required'),
  quantity: z.coerce.number().min(0.01, 'Quantity must be greater than 0'),
})

export type StudentFormValues = z.infer<typeof studentFormSchema>
export type StaffFormValues = z.infer<typeof staffFormSchema>
export type FoodItemFormValues = z.infer<typeof foodItemFormSchema>
export type IngredientFormValues = z.infer<typeof ingredientFormSchema>
export type BillFormValues = z.infer<typeof billFormSchema>
export type PaymentFormValues = z.infer<typeof paymentFormSchema>
export type MessOffFormValues = z.infer<typeof messOffFormSchema>
export type ScheduleFormValues = z.infer<typeof scheduleFormSchema>
export type RecipeFormValues = z.infer<typeof recipeFormSchema>
