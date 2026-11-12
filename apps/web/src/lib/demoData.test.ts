import { describe, expect, it } from 'vitest'
import { DEMO_EVENTS, DEMO_TRIAGE, DEMO_USERS } from './demoData'

describe('demo data', () => {
  it('includes at least one active flood event', () => {
    expect(DEMO_EVENTS.length).toBeGreaterThan(0)
    expect(DEMO_EVENTS[0].event_type).toBe('flood')
    expect(DEMO_EVENTS[0].status).toBe('active')
  })

  it('covers all inspection priorities', () => {
    const priorities = new Set(DEMO_TRIAGE.map((item) => item.inspection_priority))
    expect(priorities.has('P1')).toBe(true)
    expect(priorities.has('P2')).toBe(true)
    expect(priorities.has('P3')).toBe(true)
  })

  it('includes demo admin credentials', () => {
    expect(DEMO_USERS['admin@example.com']?.password).toBe('admin123')
    expect(DEMO_USERS['admin@example.com']?.user.role).toBe('admin')
  })
})
