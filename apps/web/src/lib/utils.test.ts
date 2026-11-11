import { describe, expect, it } from 'vitest'
import {
  formatCurrency,
  formatProbability,
  getPriorityBg,
  getPriorityColor,
} from './utils'

describe('formatProbability', () => {
  it('formats decimal probabilities as percentages', () => {
    expect(formatProbability(0.91)).toBe('91.0%')
    expect(formatProbability(0.045)).toBe('4.5%')
  })
})

describe('formatCurrency', () => {
  it('formats USD values', () => {
    expect(formatCurrency(485000)).toBe('$485,000')
  })

  it('handles undefined', () => {
    expect(formatCurrency(undefined)).toBe('N/A')
  })
})

describe('priority styles', () => {
  it('returns priority color classes', () => {
    expect(getPriorityColor('P1')).toBe('text-p1')
    expect(getPriorityColor('P2')).toBe('text-p2')
    expect(getPriorityColor('P3')).toBe('text-p3')
  })

  it('returns priority background classes', () => {
    expect(getPriorityBg('P1')).toContain('bg-p1')
    expect(getPriorityBg('P2')).toContain('bg-p2')
    expect(getPriorityBg('P3')).toContain('bg-p3')
  })
})
