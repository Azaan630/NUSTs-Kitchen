export type AccountType = 'Admin' | 'Staff' | 'Student'

export interface User {
  UserID: number
  Email: string
  Full_Name: string
  Account_Type: AccountType
  RegisteredAt: string
}

export interface Student {
  UserID: number
  Email: string
  Full_Name: string
  RegisteredAt: string
  RegNo: string
  MessPackage: string | null
  MessPackageStart: string | null
  MessPackageEnd: string | null
  Balance: number
  IsActive: boolean
}

export interface StaffCategory {
  CategoryID: number
  CategoryName: string
  Salary: number
}

export interface Staff {
  UserID: number
  Email: string
  Full_Name: string
  RegisteredAt: string
  ContactNumbers: string[]
  Category: string
  Salary: number
  HireDate: string
}

export interface Ingredient {
  IngredientID: number
  IngredientName: string
  Unit: string
  StockQuantity: number
  UnitPrice: number
}

export interface FoodItem {
  ItemID: number
  ItemName: string
  Category: string
  Price: number
  IsVegetarian: boolean
  Vote_Count: number
  Ratings_Average: number
  Description?: string
}

export interface MenuScheduleItem {
  ScheduleID: number
  Date: string
  Meal_Type: string
  ItemID: number
  ItemName: string
  Category: string
  Price: number
  IsVegetarian: boolean
  Ratings_Average: number
  Vote_Count: number
}

export interface Bill {
  BillingID: number
  UserID: number
  Full_Name: string
  Month: string
  Year: number
  TotalDays: number
  MessOffDays: number
  DailyRate: number
  TotalAmount: number
  Status: 'Pending' | 'Paid' | 'Overdue'
  DueDate: string
}

export interface Transaction {
  TransactionID: number
  BillingID: number
  AmountPaid: number
  PaymentDate: string
  PaymentMethod: string
}

export interface PollResult {
  ItemID: number
  ItemName: string
  Vote_Count: number
  Category: string
}

export interface Rating {
  RatingID: number
  UserID: number
  ItemID: number
  Date: string
  Meal_Type: string
  Score: number
}

export interface MessOff {
  MessOffID: number
  UserID: number
  Full_Name: string
  StartDate: string
  EndDate: string
  Status: 'Pending' | 'Approved' | 'Cancelled'
  RequestDate: string
  ApprovedBy: number | null
}

export interface MenuFoodItem {
  ItemID: number
  ItemName: string
  Category: string
  Price: number
  IsVegetarian: boolean
}

export interface FoodItemCost {
  ItemID: number
  ItemName: string
  EstimatedCost: number
  Price: number
}

export interface BillingSummaryItem {
  BillingID: number
  UserID: number
  Full_Name: string
  Month: string
  Year: number
  TotalDays: number
  MessOffDays: number
  DailyRate: number
  TotalAmount: number
  AmountPaid: number
  Status: string
  DueDate: string
}

export interface Recipe {
  ItemID: number
  ItemName: string
  IngredientID: number
  IngredientName: string
  Quantity: number
}

export interface CreateStudentPayload {
  email: string
  full_name: string
  reg_no: string
  mess_package?: string
  mess_package_start?: string
  mess_package_end?: string
}

export interface CreateStaffPayload {
  email: string
  full_name: string
  category_id: number
  hire_date: string
}

export interface CreateFoodItemPayload {
  item_name: string
  category: string
  price: number
  is_vegetarian: boolean
  description?: string
}

export interface CreateIngredientPayload {
  ingredient_name: string
  unit: string
  stock_quantity: number
  unit_price: number
}

export interface CreateBillPayload {
  user_id: number
  month: string
  year: number
  total_days: number
  mess_off_days: number
  daily_rate: number
  total_amount: number
  due_date: string
}

export interface PaymentPayload {
  amount_paid: number
  payment_date: string
  payment_method: string
}

export interface MessOffRequestPayload {
  user_id: number
  start_date: string
  end_date: string
}

export interface ApiError {
  detail: string
}
