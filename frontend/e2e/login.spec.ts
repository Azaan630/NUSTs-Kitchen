import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test('should render login form', async ({ page }) => {
    await page.goto('/login')

    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
  })

  test('should show error on empty email', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page.getByText(/email.*required/i)).toBeVisible()
  })

  test('should redirect to admin dashboard on valid admin email', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('admin@seecs.edu.pk')
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page).toHaveURL(/\/admin\/dashboard/, { timeout: 10000 })
  })

  test('should redirect to student dashboard on valid student email', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel(/email/i).fill('student@seecs.edu.pk')
    await page.getByRole('button', { name: /sign in/i }).click()
    await expect(page).toHaveURL(/\/student\/today/, { timeout: 10000 })
  })

  test('should toggle theme', async ({ page }) => {
    await page.goto('/login')
    const html = page.locator('html')
    const initialTheme = await html.getAttribute('class')

    await page.getByRole('button', { name: /toggle theme/i }).click()
    const toggledTheme = await html.getAttribute('class')
    expect(toggledTheme).not.toBe(initialTheme)
  })
})
