import { describe, it, expect } from 'vitest'
import { validateResumeText, validateJDText } from '../utils/validators'

describe('validateResumeText', () => {
  it('returns error when text is empty', () => {
    expect(validateResumeText('')).toBe('Resume text is required')
  })

  it('returns error when text is only whitespace', () => {
    expect(validateResumeText('   ')).toBe('Resume text is required')
  })

  it('returns error when text is under 100 characters', () => {
    expect(validateResumeText('Short resume')).toBe('Resume must be at least 100 characters')
  })

  it('returns error when text exceeds 15000 characters', () => {
    const longText = 'a'.repeat(15001)
    expect(validateResumeText(longText)).toBe('Resume must be under 15,000 characters')
  })

  it('returns null for valid resume text', () => {
    const validResume = 'John Doe\njohn@example.com\n\nEXPERIENCE\nSoftware Engineer at Acme Corp 2020-2024\n- Built scalable microservices using Python and FastAPI\n- Improved system performance by 40% through query optimisation'
    expect(validateResumeText(validResume)).toBeNull()
  })

  it('returns null for text exactly at the 100-character boundary', () => {
    const exactText = 'a'.repeat(100)
    expect(validateResumeText(exactText)).toBeNull()
  })
})

describe('validateJDText', () => {
  it('returns error when text is empty', () => {
    expect(validateJDText('')).toBe('Job description is required')
  })

  it('returns error when text is under 50 characters', () => {
    expect(validateJDText('Short JD')).toBe('Job description must be at least 50 characters')
  })

  it('returns error when text exceeds 8000 characters', () => {
    const longText = 'a'.repeat(8001)
    expect(validateJDText(longText)).toBe('Job description must be under 8,000 characters')
  })

  it('returns null for valid job description', () => {
    const validJD = 'We are looking for a Senior Software Engineer with 5+ years of experience in Python and FastAPI.'
    expect(validateJDText(validJD)).toBeNull()
  })
})
