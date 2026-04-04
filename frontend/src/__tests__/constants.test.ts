import { describe, it, expect } from 'vitest'
import { getScoreColor, getSignalColor, COLORS } from '../utils/constants'

describe('getScoreColor', () => {
  it('returns success color for score >= 70', () => {
    expect(getScoreColor(70)).toBe(COLORS.success)
    expect(getScoreColor(100)).toBe(COLORS.success)
    expect(getScoreColor(85)).toBe(COLORS.success)
  })

  it('returns warning color for score between 40 and 69', () => {
    expect(getScoreColor(40)).toBe(COLORS.warning)
    expect(getScoreColor(55)).toBe(COLORS.warning)
    expect(getScoreColor(69)).toBe(COLORS.warning)
  })

  it('returns danger color for score below 40', () => {
    expect(getScoreColor(0)).toBe(COLORS.danger)
    expect(getScoreColor(25)).toBe(COLORS.danger)
    expect(getScoreColor(39)).toBe(COLORS.danger)
  })

  it('inverted=true flips the logic — high score means danger', () => {
    // AI detection score: high = bad, so inverted=true
    // score=80 inverted -> effective=20 -> danger
    expect(getScoreColor(80, true)).toBe(COLORS.danger)
    // score=20 inverted -> effective=80 -> success
    expect(getScoreColor(20, true)).toBe(COLORS.success)
  })
})

describe('getSignalColor', () => {
  it('returns danger when signal pct >= 60%', () => {
    expect(getSignalColor(6, 10)).toBe(COLORS.danger)
    expect(getSignalColor(10, 10)).toBe(COLORS.danger)
  })

  it('returns warning when signal pct is between 25% and 59%', () => {
    expect(getSignalColor(2.5, 10)).toBe(COLORS.warning)
    expect(getSignalColor(5, 10)).toBe(COLORS.warning)
  })

  it('returns success when signal pct is below 25%', () => {
    expect(getSignalColor(0, 10)).toBe(COLORS.success)
    expect(getSignalColor(2, 10)).toBe(COLORS.success)
  })
})
