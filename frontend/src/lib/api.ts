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

// Auth
export async function verifyUser(email: string): Promise<User> {
  const { data } = await api.get<User>('/users/verify', { params: { email } })
  return data
}

export async function getMe(email: string): Promise<User> {
  const { data } = await api.get<User>('/users/me', authParams(email))
  return data
}

// Menu
export async function getTodayMenu(email: string): Promise<MenuScheduleItem[]> {
  const { data } = await api.get<MenuScheduleItem[]>('/menu/today', authParams(email))
  return data
}

export async function getWeeklyMenu(email: string): Promise<MenuScheduleItem[]> {
  const { data } = await api.get<MenuScheduleItem[]>('/menu/weekly', authParams(email))
  return data
}

// Students (Admin)
export async function getAllStudents(email: string): Promise<Student[]> {
  const { data } = await api.get<Student[]>('/admin/students/all', authParams(email))
  return data
}

export async function registerStudent(email: string, payload: CreateStudentPayload): Promise<Student> {
  const { data } = await api.post('/admin/students/register', payload, authParams(email))
  return data
}

export async function updateStudent(
  email: string,
  userId: number,
  payload: Partial<CreateStudentPayload>,
): Promise<Student> {
  const { data } = await api.patch(`/admin/students/update/${userId}`, payload, authParams(email))
  return data
}

export async function deleteStudent(email: string, userId: number): Promise<void> {
  await api.delete(`/admin/students/delete/${userId}`, authParams(email))
}

// Staff (Admin)
export async function getStaffDetails(email: string, userId: number): Promise<Staff> {
  const { data } = await api.get<Staff>(`/admin/staff/details/${userId}`, authParams(email))
  return data
}

export async function registerStaff(email: string, payload: CreateStaffPayload): Promise<Staff> {
  const { data } = await api.post('/admin/staff/register', payload, authParams(email))
  return data
}

export async function updateStaff(
  email: string,
  payload: Partial<CreateStaffPayload> & { user_id: number },
): Promise<Staff> {
  const { data } = await api.post('/admin/staff/update', payload, authParams(email))
  return data
}

export async function deleteStaff(email: string, userId: number): Promise<void> {
  await api.delete(`/admin/staff/delete/${userId}`, authParams(email))
}

export async function getStaffCategories(email: string): Promise<StaffCategory[]> {
  const { data } = await api.get<StaffCategory[]>('/admin/staff/category', authParams(email))
  return data
}

// Food Items
export async function getAllFoodItems(email: string): Promise<FoodItem[]> {
  const { data } = await api.get<FoodItem[]>('/admin/food/costs', authParams(email))
  return data
}

export async function getFoodItem(email: string, itemId: number): Promise<FoodItem> {
  const { data } = await api.get<FoodItem>(`/admin/food/${itemId}`, authParams(email))
  return data
}

export async function createFoodItem(email: string, payload: CreateFoodItemPayload): Promise<FoodItem> {
  const { data } = await api.post('/admin/food_items/create', payload, authParams(email))
  return data
}

export async function updateFoodItem(
  email: string,
  itemId: number,
  payload: Partial<CreateFoodItemPayload>,
): Promise<FoodItem> {
  const { data } = await api.patch(`/admin/food_items/update/${itemId}`, payload, authParams(email))
  return data
}

export async function deleteFoodItem(email: string, itemId: number): Promise<void> {
  await api.delete(`/admin/food_items/delete/${itemId}`, authParams(email))
}

// Ingredients
export async function getAllIngredients(email: string): Promise<Ingredient[]> {
  const { data } = await api.get<Ingredient[]>('/analytics/ingredients', authParams(email))
  return data
}

export async function createIngredient(email: string, payload: CreateIngredientPayload): Promise<Ingredient> {
  const { data } = await api.post('/admin/ingredients/create', payload, authParams(email))
  return data
}

export async function updateIngredient(
  email: string,
  id: number,
  payload: Partial<CreateIngredientPayload>,
): Promise<Ingredient> {
  const { data } = await api.patch(`/admin/ingredients/update/${id}`, payload, authParams(email))
  return data
}

export async function deleteIngredient(email: string, id: number): Promise<void> {
  await api.delete(`/admin/ingredients/delete/${id}`, authParams(email))
}

// Recipes
export async function getRecipes(email: string): Promise<Recipe[]> {
  const { data } = await api.get('/recipes', authParams(email))
  return data
}

export async function addRecipe(
  email: string,
  itemId: number,
  ingredientId: number,
  quantity: number,
): Promise<void> {
  await api.post(`/admin/add_recipe/${itemId}/${ingredientId}/${quantity}`, null, authParams(email))
}

export async function updateRecipe(
  email: string,
  itemId: number,
  ingredientId: number,
  quantity: number,
): Promise<void> {
  await api.patch(`/admin/recipe/update/${itemId}/${ingredientId}`, null, {
    ...authParams(email),
    params: { quantity },
  })
}

export async function deleteRecipe(email: string, itemId: number, ingredientId: number): Promise<void> {
  await api.delete(`/admin/recipe/${itemId}/${ingredientId}`, authParams(email))
}

// Menu Schedule
export async function addToSchedule(
  email: string,
  itemId: number,
  date: string,
  mealType: string,
): Promise<void> {
  await api.post(`/admin/menu_schedule/${itemId}/${date}/${mealType}`, null, authParams(email))
}

export async function updateScheduleItem(
  email: string,
  itemId: number,
  scheduleId: number,
): Promise<void> {
  await api.patch(`/admin/menu_schedule/${itemId}/${scheduleId}`, null, authParams(email))
}

export async function removeFromSchedule(email: string, itemId: number, scheduleId: number): Promise<void> {
  await api.delete(`/admin/recipe/${itemId}/${scheduleId}`, authParams(email))
}

// Polls
export async function startPoll(email: string): Promise<void> {
  await api.post('/admin/poll/start', null, authParams(email))
}

export async function getActivePoll(email: string): Promise<MenuFoodItem[]> {
  const { data } = await api.get<MenuFoodItem[]>('/poll/active', authParams(email))
  return data
}

export async function castVote(email: string, userId: number, itemId: number): Promise<void> {
  await api.post(`/poll/vote/${itemId}/${userId}`, null, authParams(email))
}

export async function getPollResults(email: string): Promise<PollResult[]> {
  const { data } = await api.get<PollResult[]>('/admin/poll/results', authParams(email))
  return data
}

// Bills
export async function createBill(email: string, payload: CreateBillPayload): Promise<Bill> {
  const { data } = await api.post('/admin/bills/create', payload, authParams(email))
  return data
}

export async function updateBill(
  email: string,
  billId: number,
  payload: Partial<CreateBillPayload>,
): Promise<Bill> {
  const { data } = await api.patch(`/admin/bills/update/${billId}`, payload, authParams(email))
  return data
}

export async function deleteBill(email: string, billId: number): Promise<void> {
  await api.delete(`/admin/bills/delete/${billId}`, authParams(email))
}

export async function payBill(email: string, billingId: number, payload: PaymentPayload): Promise<void> {
  await api.post(`/admin/bills/pay/${billingId}`, payload, authParams(email))
}

export async function getMonthlyBillingSummary(email: string): Promise<BillingSummaryItem[]> {
  const { data } = await api.get('/admin/monthly_billing_summary', authParams(email))
  return data
}

export async function getBillStatus(email: string, userId: number): Promise<Bill[]> {
  const { data } = await api.get(`/admin/${userId}/bill_status`, authParams(email))
  return data
}

export async function getMyBills(email: string): Promise<Bill[]> {
  const { data } = await api.get<Bill[]>('/users/my_bills', authParams(email))
  return data
}

export async function getMyBillHistory(email: string): Promise<Transaction[]> {
  const { data } = await api.get<Transaction[]>('/bills/my_history', authParams(email))
  return data
}

// Ratings
export async function rateFood(
  email: string,
  userId: number,
  itemId: number,
  date: string,
  mealType: string,
  score: number,
): Promise<Rating> {
  const { data } = await api.post(
    `/student/rating/${userId}/${itemId}/${date}/${mealType}/${score}`,
    null,
    authParams(email),
  )
  return data
}

export async function getFoodRating(
  email: string,
  itemId: number,
  date: string,
  mealType: string,
): Promise<Rating> {
  const { data } = await api.get(`/getFoodRating/${itemId}/${date}/${mealType}`, authParams(email))
  return data
}

// Mess Off
export async function requestMessOff(email: string, payload: MessOffRequestPayload): Promise<MessOff> {
  const { data } = await api.post(
    `/student/mess_off/request/${payload.user_id}/${payload.start_date}/${payload.end_date}`,
    null,
    authParams(email),
  )
  return data
}

export async function cancelMessOff(email: string, messOffId: number): Promise<void> {
  await api.post(`/student/mess_off/cancel/${messOffId}`, null, authParams(email))
}

export async function approveMessOff(email: string, requestId: number): Promise<void> {
  await api.post(`/admin/mess-off/approve/${requestId}`, null, authParams(email))
}

export async function getMessOffHistory(email: string): Promise<MessOff[]> {
  const { data } = await api.get<MessOff[]>('/student/mess-off/history', authParams(email))
  return data
}

export async function getMessOff(email: string, messOffId: number): Promise<MessOff> {
  const { data } = await api.get<MessOff>(`/student/mess-off/${messOffId}`, authParams(email))
  return data
}

// Food costs
export async function getFoodCosts(email: string): Promise<FoodItemCost[]> {
  const { data } = await api.get<FoodItemCost[]>('/admin/food/costs', authParams(email))
  return data
}
