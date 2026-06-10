import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate, cn, getInitials } from '@/lib/utils'

describe('Utils', () => {
  describe('formatCurrency', () => {
    it('formats PKR currency', () => {
      const result = formatCurrency(1500)
      expect(result).toContain('1,500')
    })

    it('handles zero', () => {
      const result = formatCurrency(0)
      expect(result).toContain('0')
    })
  })

  describe('formatDate', () => {
    it('formats a date string', () => {
      const result = formatDate('2024-01-15')
      expect(result).toBeTruthy()
    })
  })

  describe('cn', () => {
    it('merges class names', () => {
      const result = cn('px-4', 'py-2', 'px-6')
      expect(result).toBe('py-2 px-6')
    })
  })

  describe('getInitials', () => {
    it('gets initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD')
    })

    it('handles single name', () => {
      expect(getInitials('John')).toBe('J')
    })

    it('handles three names', () => {
      expect(getInitials('John Michael Doe')).toBe('JM')
    })
  })
})
