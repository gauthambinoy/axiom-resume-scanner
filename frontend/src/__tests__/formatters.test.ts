import { describe, it, expect } from 'vitest'
import { formatScore, formatPercentage, formatMs, formatFileSize } from '../utils/formatters'

describe('formatScore', () => {
  it('rounds a decimal score to integer string', () => {
    expect(formatScore(87.6)).toBe('88')
    expect(formatScore(50.4)).toBe('50')
  })

  it('handles exact integers', () => {
    expect(formatScore(100)).toBe('100')
    expect(formatScore(0)).toBe('0')
  })
})

describe('formatPercentage', () => {
  it('appends % sign and rounds', () => {
    expect(formatPercentage(75.3)).toBe('75%')
    expect(formatPercentage(0)).toBe('0%')
    expect(formatPercentage(100)).toBe('100%')
  })
})

describe('formatMs', () => {
  it('shows ms for values under 1000', () => {
    expect(formatMs(500)).toBe('500ms')
    expect(formatMs(999)).toBe('999ms')
  })

  it('converts to seconds for values >= 1000', () => {
    expect(formatMs(1000)).toBe('1.0s')
    expect(formatMs(2500)).toBe('2.5s')
  })
})

describe('formatFileSize', () => {
  it('shows bytes for small files', () => {
    expect(formatFileSize(512)).toBe('512B')
  })

  it('converts to KB for files >= 1024 bytes', () => {
    expect(formatFileSize(1024)).toBe('1.0KB')
    expect(formatFileSize(2048)).toBe('2.0KB')
  })

  it('converts to MB for large files', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1.0MB')
    expect(formatFileSize(2.5 * 1024 * 1024)).toBe('2.5MB')
  })
})
