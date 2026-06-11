import axios from 'axios'
import type {
  User, Student, Staff, Ingredient, FoodItem, MenuScheduleItem,
  Bill, Transaction, PollResult, Rating, MessOff, FoodItemCost,
  CreateStudentPayload, CreateStaffPayload, CreateFoodItemPayload,
  CreateIngredientPayload, CreateBillPayload, PaymentPayload, MessOffRequestPayload,
  StaffCategory, MenuFoodItem, BillingSummaryItem, Recipe,
} from '@/types'
import { API_URL } from './constants'

const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail || err.response?.data?.message || err.message || 'An error occurred'
    return Promise.reject(new Error(message))
  },
)

function authParams(email: string) {
  return { params: { email } }
}

// ─── Field mapping helpers ───────────────────────────────────────────────────

function fullName(u: any): string {
  return `${u.First_Name ?? ''} ${u.Last_Name ?? ''}`.trim()
}

function mapUser(u: any): User {
  return {
    UserID: u.UserID,
    Email: u.Email,
    Full_Name: fullName(u),
    Account_Type: u.Account_Type,
    RegisteredAt: '',
  }
}

function mapStudent(s: any): Student {
  return {
    UserID: s.UserID,
    Email: s.Email ?? '',
    Full_Name: fullName(s),
    RegisteredAt: '',
    RegNo: s.RegNo ?? '',
    MessPackage: s.MessPackage ?? null,
    MessPackageStart: s.MessPackageStart ?? null,
    MessPackageEnd: s.MessPackageEnd ?? null,
    Balance: s.Balance ?? 0,
    IsActive: s.IsActive ?? true,
  }
}

function mapMenuScheduleItem(item: any): MenuScheduleItem {
  return {
    ScheduleID: item.ScheduleID ?? item.Schedule_ID ?? 0,
    Date: item.Date,
    Meal_Type: item.Meal_Type ?? item.meal_type ?? '',
    ItemID: item.ItemID ?? item.Item_ID ?? 0,
    ItemName: item.ItemName ?? item.Name ?? '',
    Category: item.Category ?? '',
    Price: Number(item.Price ?? 0),
    IsVegetarian: item.IsVegetarian ?? false,
    Ratings_Average: Number(item.Ratings_Average ?? 0),
    Vote_Count: item.Vote_Count ?? 0,
  }
}

function mapBill(b: any): Bill {
  return {
    BillingID: b.BillingID ?? b.Billing_ID ?? 0,
    UserID: b.UserID ?? b.User_ID ?? 0,
    Full_Name: b.Full_Name ?? fullName(b),
    Month: b.Month ?? '',
    Year: b.Year ?? (b.Month ? new Date(b.Month).getFullYear() : 0),
    TotalDays: b.TotalDays ?? 0,
    MessOffDays: b.MessOffDays ?? 0,
    DailyRate: b.DailyRate ?? 0,
    TotalAmount: Number(b.TotalAmount ?? b.Amount ?? 0),
    Status: b.Status ?? 'Pending',
    DueDate: b.DueDate ?? b.Due_Date ?? '',
  }
}

function mapMessOff(m: any): MessOff {
  return {
    MessOffID: m.MessOffID ?? m.Mess_Off_ID ?? 0,
    UserID: m.UserID ?? m.User_ID ?? 0,
    Full_Name: m.Full_Name ?? '',
    StartDate: m.StartDate ?? m.Start_Date ?? '',
    EndDate: m.EndDate ?? m.End_Date ?? '',
    Status: m.Status ?? 'Pending',
    RequestDate: m.RequestDate ?? m.Request_Date ?? '',
    ApprovedBy: m.ApprovedBy ?? null,
  }
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export async function verifyUser(email: string): Promise<User> {
  const { data } = await api.get<{ status: string; user_details: any }>('/users/verify', { params: { email } })
  return mapUser(data.user_details)
}

export async function getMe(email: string): Promise<User> {
  const { data } = await api.get<any>('/users/me', authParams(email))
  return mapUser(data)
}

// ─── Menu ────────────────────────────────────────────────────────────────────

export async function getTodayMenu(email: string): Promise<MenuScheduleItem[]> {
  const { data } = await api.get<{ date: string; item_count: number; menu: any[] }>('/menu/today', authParams(email))
  return (data.menu || []).map(mapMenuScheduleItem)
}

export async function getWeeklyMenu(email: string): Promise<MenuScheduleItem[]> {
  const { data } = await api.get<any[]>('/menu/weekly', authParams(email))
  return (data || []).map(mapMenuScheduleItem)
}

// ─── Students (Admin) ────────────────────────────────────────────────────────

export async function getAllStudents(email: string): Promise<Student[]> {
  const { data } = await api.get<any[]>('/admin/students/all', authParams(email))
  return (data || []).map(mapStudent)
}

export async function registerStudent(email: string, payload: CreateStudentPayload): Promise<Student> {
  const { data } = await api.post('/admin/students/register', payload, authParams(email))
  return data as unknown as Student
}

export async function updateStudent(
  email: string,
  userId: number,
  payload: Partial<CreateStudentPayload>,
): Promise<Student> {
  const { data } = await api.patch(`/admin/students/update/${userId}`, payload, authParams(email))
  return data as unknown as Student
}

export async function deleteStudent(email: string, userId: number): Promise<void> {
  await api.delete(`/admin/students/delete/${userId}`, authParams(email))
}

// ─── Staff (Admin) ───────────────────────────────────────────────────────────

export async function getAllStaff(email: string): Promise<Staff[]> {
  const { data } = await api.get<any[]>('/admin/staff/all', authParams(email))
  return (data || []).map((s: any) => ({
    UserID: s.UserID,
    Email: s.Email ?? '',
    Full_Name: fullName(s),
    RegisteredAt: '',
    ContactNumbers: [],
    Category: s.Category ?? '',
    Salary: Number(s.Salary ?? 0),
    HireDate: '',
  }))
}

export async function getStaffDetails(email: string, userId: number): Promise<Staff> {
  const { data } = await api.get<any[]>('/admin/staff/details/' + userId, authParams(email))
  const row = (data || [])[0] || {}
  return {
    UserID: row.UserID,
    Email: row.Email ?? '',
    Full_Name: fullName(row),
    RegisteredAt: '',
    ContactNumbers: [],
    Category: row.Category ?? '',
    Salary: Number(row.Salary ?? 0),
    HireDate: '',
  }
}

export async function registerStaff(email: string, payload: CreateStaffPayload): Promise<Staff> {
  const { data } = await api.post('/admin/staff/register', payload, authParams(email))
  return data as unknown as Staff
}

export async function updateStaff(
  email: string,
  payload: Partial<CreateStaffPayload> & { user_id: number },
): Promise<Staff> {
  const { user_id, ...rest } = payload
  const { data } = await api.patch('/admin/staff/update/' + user_id, rest, authParams(email))
  return data as unknown as Staff
}

export async function deleteStaff(email: string, userId: number): Promise<void> {
  await api.delete(`/admin/staff/delete/${userId}`, authParams(email))
}

export async function getStaffCategories(email: string): Promise<StaffCategory[]> {
  const { data } = await api.get<StaffCategory[]>('/admin/staff/category', authParams(email))
  return data
}

// ─── Food Items ──────────────────────────────────────────────────────────────

export async function getAllFoodItems(email: string): Promise<FoodItem[]> {
  const { data } = await api.get<any[]>('/admin/food/costs', authParams(email))
  return (data || []).map((item: any) => ({
    ItemID: item.ItemID ?? item.Item_ID ?? 0,
    ItemName: item.ItemName ?? item.Name ?? '',
    Category: item.Category ?? '',
    Price: Number(item.Price ?? item.Estimated_Cost ?? 0),
    IsVegetarian: item.IsVegetarian ?? false,
    Vote_Count: item.Vote_Count ?? 0,
    Ratings_Average: Number(item.Ratings_Average ?? 0),
    Description: item.Description ?? undefined,
  }))
}

export async function getFoodItem(email: string, itemId: number): Promise<FoodItem> {
  const { data } = await api.get<any[]>('/admin/food/' + itemId, authParams(email))
  const item = (data || [])[0] || {}
  return {
    ItemID: item.ItemID ?? item.Item_ID ?? itemId,
    ItemName: item.ItemName ?? item.Name ?? '',
    Category: item.Category ?? '',
    Price: Number(item.Price ?? 0),
    IsVegetarian: item.IsVegetarian ?? false,
    Vote_Count: item.Vote_Count ?? 0,
    Ratings_Average: Number(item.Ratings_Average ?? 0),
    Description: item.Description ?? undefined,
  }
}

export async function createFoodItem(email: string, payload: CreateFoodItemPayload): Promise<FoodItem> {
  const { data } = await api.post('/admin/food-items/create', payload, authParams(email))
  return data as unknown as FoodItem
}

export async function updateFoodItem(
  email: string,
  itemId: number,
  payload: Partial<CreateFoodItemPayload>,
): Promise<FoodItem> {
  const { data } = await api.patch('/admin/food-items/update/' + itemId, payload, authParams(email))
  return data as unknown as FoodItem
}

export async function deleteFoodItem(email: string, itemId: number): Promise<void> {
  await api.delete('/admin/food-items/delete/' + itemId, authParams(email))
}

// ─── Ingredients ─────────────────────────────────────────────────────────────

export async function getAllIngredients(email: string): Promise<Ingredient[]> {
  const { data } = await api.get<any[]>('/analytics/ingredients', authParams(email))
  return (data || []).map((item: any) => ({
    IngredientID: item.IngredientID ?? item.Ingredient_ID ?? 0,
    IngredientName: item.IngredientName ?? item.Name ?? '',
    Unit: item.Unit ?? '',
    StockQuantity: Number(item.StockQuantity ?? item.Total_Quantity ?? 0),
    UnitPrice: Number(item.UnitPrice ?? item.Unit_cost ?? 0),
  }))
}

export async function createIngredient(email: string, payload: CreateIngredientPayload): Promise<Ingredient> {
  const { data } = await api.post('/admin/ingredients/create', payload, authParams(email))
  return data as unknown as Ingredient
}

export async function updateIngredient(
  email: string,
  id: number,
  payload: Partial<CreateIngredientPayload>,
): Promise<Ingredient> {
  const { data } = await api.patch('/admin/ingredients/update/' + id, payload, authParams(email))
  return data as unknown as Ingredient
}

export async function deleteIngredient(email: string, id: number): Promise<void> {
  await api.delete('/admin/ingredients/delete/' + id, authParams(email))
}

// ─── Recipes ─────────────────────────────────────────────────────────────────

export async function getRecipes(email: string): Promise<Recipe[]> {
  const { data } = await api.get<any[]>('/recipes', authParams(email))
  return (data || []).map((r: any) => ({
    ItemID: r.ItemID ?? r.Item_ID ?? 0,
    ItemName: r.ItemName ?? '',
    IngredientID: r.IngredientID ?? r.Ingredient_ID ?? 0,
    IngredientName: r.IngredientName ?? r.Name ?? '',
    Quantity: Number(r.Quantity ?? r.Ingredient_Quantity ?? 0),
  }))
}

export async function addRecipe(
  email: string,
  itemId: number,
  ingredientId: number,
  quantity: number,
): Promise<void> {
  await api.post('/admin/add-recipe/' + itemId + '/' + ingredientId + '/' + quantity, null, authParams(email))
}

export async function updateRecipe(
  email: string,
  itemId: number,
  ingredientId: number,
  quantity: number,
): Promise<void> {
  await api.patch('/admin/recipe/update/' + itemId + '/' + ingredientId, null, {
    ...authParams(email),
    params: { quantity },
  })
}

export async function deleteRecipe(email: string, itemId: number, ingredientId: number): Promise<void> {
  await api.delete('/admin/recipe/' + itemId + '/' + ingredientId, authParams(email))
}

// ─── Menu Schedule ───────────────────────────────────────────────────────────

export async function addToSchedule(
  email: string,
  itemId: number,
  date: string,
  mealType: string,
): Promise<void> {
  await api.post('/admin/menu-schedule/' + itemId + '/' + date + '/' + mealType, null, authParams(email))
}

export async function updateScheduleItem(
  email: string,
  itemId: number,
  scheduleId: number,
): Promise<void> {
  await api.patch('/admin/menu-schedule/' + itemId + '/' + scheduleId, null, authParams(email))
}

export async function removeFromSchedule(email: string, itemId: number, scheduleId: number): Promise<void> {
  await api.delete('/admin/menu-schedule/' + itemId + '/' + scheduleId, authParams(email))
}

// ─── Polls ───────────────────────────────────────────────────────────────────

export async function startPoll(email: string, itemIds: number[], mealType: string): Promise<void> {
  await api.post('/admin/poll/start', { item_ids: itemIds, meal_type: mealType }, authParams(email))
}

export async function getActivePoll(email: string): Promise<MenuFoodItem[]> {
  const { data } = await api.get<{ active: boolean; items?: any[] }>('/poll/active', authParams(email))
  if (!data.active || !data.items) return []
  return data.items.map((item: any) => ({
    ItemID: item.ItemID ?? item.Item_ID ?? 0,
    ItemName: item.ItemName ?? item.Name ?? '',
    Category: item.Category ?? '',
    Price: Number(item.Price ?? 0),
    IsVegetarian: item.IsVegetarian ?? false,
  }))
}

export async function castVote(email: string, userId: number, itemId: number): Promise<void> {
  await api.post('/poll/vote/' + itemId + '/' + userId, null, authParams(email))
}

export async function searchFoodItems(email: string, query: string): Promise<FoodItem[]> {
  const { data } = await api.get<any[]>('/admin/food/search', { params: { email, q: query } })
  return (data || []).map((item: any) => ({
    ItemID: item.ItemID ?? item.Item_ID ?? 0,
    ItemName: item.ItemName ?? item.Name ?? '',
    Category: item.Category ?? '',
    Price: Number(item.Price ?? 0),
    IsVegetarian: item.IsVegetarian ?? false,
    Vote_Count: item.Vote_Count ?? 0,
    Ratings_Average: Number(item.Ratings_Average ?? 0),
    Description: item.Description ?? undefined,
  }))
}

export async function getPollResults(email: string): Promise<PollResult[]> {
  const { data } = await api.get<{ results: any[] }>('/admin/poll/results', authParams(email))
  return (data.results || []).map((item: any) => ({
    ItemID: item.ItemID ?? item.Item_ID ?? 0,
    ItemName: item.ItemName ?? item.Name ?? '',
    Vote_Count: item.Vote_Count ?? 0,
    Category: item.Category ?? '',
  }))
}

// ─── Bills ───────────────────────────────────────────────────────────────────

export async function createBill(email: string, payload: CreateBillPayload): Promise<Bill> {
  const { data } = await api.post('/admin/bills/create', payload, authParams(email))
  return data as unknown as Bill
}

export async function updateBill(
  email: string,
  billId: number,
  payload: Partial<CreateBillPayload>,
): Promise<Bill> {
  const { data } = await api.patch('/admin/bills/update/' + billId, payload, authParams(email))
  return data as unknown as Bill
}

export async function deleteBill(email: string, billId: number): Promise<void> {
  await api.delete('/admin/bills/delete/' + billId, authParams(email))
}

export async function payBill(email: string, billingId: number, payload: PaymentPayload): Promise<void> {
  await api.post('/admin/bills/pay/' + billingId, payload, authParams(email))
}

export async function getMonthlyBillingSummary(email: string): Promise<BillingSummaryItem[]> {
  const { data } = await api.get<any[]>('/admin/monthly_billing_summary', authParams(email))
  return (data || []).map((r: any) => ({
    BillingID: r.BillingID ?? 0,
    UserID: r.UserID ?? r.User_ID ?? 0,
    Full_Name: r.Full_Name ?? '',
    Month: r.Month ?? r.Billing_Month ?? '',
    Year: r.Year ?? (r.Billing_Month ? parseInt(r.Billing_Month.split('-')[0]) : 0),
    TotalDays: r.TotalDays ?? 0,
    MessOffDays: r.MessOffDays ?? 0,
    DailyRate: r.DailyRate ?? 0,
    TotalAmount: Number(r.TotalAmount ?? r.Total_Amount ?? 0),
    AmountPaid: Number(r.AmountPaid ?? r.Total_Collected ?? 0),
    Status: r.Status ?? '',
    DueDate: r.DueDate ?? r.Due_Date ?? '',
  }))
}

export async function getBillStatus(email: string, userId: number): Promise<Bill[]> {
  const { data } = await api.get<any[]>('/admin/' + userId + '/bill_status', authParams(email))
  return (data || []).map(mapBill)
}

export async function getMyBills(email: string): Promise<Bill[]> {
  const { data } = await api.get<any[]>('/users/my_bills', authParams(email))
  return (data || []).map(mapBill)
}

export async function getMyBillHistory(email: string): Promise<Transaction[]> {
  const { data } = await api.get<any[]>('/bills/my_history', authParams(email))
  return (data || []).map((r: any) => ({
    TransactionID: r.TransactionID ?? r.Transaction_ID ?? 0,
    BillingID: r.BillingID ?? r.Billing_ID ?? 0,
    AmountPaid: Number(r.AmountPaid ?? r.Amount_Paid ?? r.Amount ?? 0),
    PaymentDate: r.PaymentDate ?? r.Payment_Date ?? '',
    PaymentMethod: r.PaymentMethod ?? r.Payment_Method ?? '',
  }))
}

// ─── Ratings ─────────────────────────────────────────────────────────────────

export async function rateFood(
  email: string,
  userId: number,
  itemId: number,
  date: string,
  mealType: string,
  score: number,
): Promise<Rating> {
  const { data } = await api.post(
    '/student/rating/' + userId + '/' + itemId + '/' + date + '/' + mealType + '/' + score,
    null,
    authParams(email),
  )
  return data as unknown as Rating
}

export async function getFoodRating(
  email: string,
  itemId: number,
  date: string,
  mealType: string,
): Promise<Rating> {
  const { data } = await api.get<{ rating: any }>('/getFoodRating/' + itemId + '/' + date + '/' + mealType, authParams(email))
  const r = data?.rating ?? {}
  return r === 'NULL'
    ? { RatingID: 0, UserID: 0, ItemID: itemId, Date: date, Meal_Type: mealType, Score: 0 }
    : {
        RatingID: r.RatingID ?? r.Rating_ID ?? 0,
        UserID: r.UserID ?? r.User_ID ?? 0,
        ItemID: r.ItemID ?? r.Item_ID ?? itemId,
        Date: r.Date ?? date,
        Meal_Type: r.Meal_Type ?? mealType,
        Score: r.Score ?? 0,
      }
}

// ─── Mess Off ────────────────────────────────────────────────────────────────

export async function requestMessOff(email: string, payload: MessOffRequestPayload): Promise<MessOff> {
  const { data } = await api.post(
    '/student/mess_off/request/' + payload.user_id + '/' + payload.start_date + '/' + payload.end_date,
    null,
    authParams(email),
  )
  return data as unknown as MessOff
}

export async function cancelMessOff(email: string, messOffId: number): Promise<void> {
  await api.post('/student/mess_off/cancel/' + messOffId, null, authParams(email))
}

export async function approveMessOff(email: string, requestId: number): Promise<void> {
  await api.post('/admin/mess-off/approve/' + requestId, null, authParams(email))
}

export async function getMessOffHistory(email: string): Promise<MessOff[]> {
  const { data } = await api.get<{ status: any[] }>('/student/mess-off/history', authParams(email))
  const arr = data?.status ?? data ?? []
  return (Array.isArray(arr) ? arr : []).map(mapMessOff)
}

export async function getMessOff(email: string, messOffId: number): Promise<MessOff> {
  const { data } = await api.get<any>('/student/mess-off/' + messOffId, authParams(email))
  return mapMessOff(data)
}

// ─── Food costs ──────────────────────────────────────────────────────────────

export async function getFoodCosts(email: string): Promise<FoodItemCost[]> {
  const { data } = await api.get<any[]>('/admin/food/costs', authParams(email))
  return (data || []).map((item: any) => ({
    ItemID: item.ItemID ?? item.Item_ID ?? 0,
    ItemName: item.ItemName ?? item.Name ?? '',
    EstimatedCost: Number(item.EstimatedCost ?? item.Estimated_Cost ?? 0),
    Price: Number(item.Price ?? 0),
  }))
}
