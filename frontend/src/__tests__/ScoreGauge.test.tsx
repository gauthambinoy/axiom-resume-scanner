import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreGauge } from '../components/Results/ScoreGauge'

describe('ScoreGauge', () => {
  it('renders the label', () => {
    render(<ScoreGauge score={75} label="ATS Score" />)
    expect(screen.getByText('ATS Score')).toBeInTheDocument()
  })

  it('renders a subtitle when provided', () => {
    render(<ScoreGauge score={50} label="AI Risk" subtitle="Moderate risk" />)
    expect(screen.getByText('Moderate risk')).toBeInTheDocument()
  })

  it('does not render a subtitle when not provided', () => {
    render(<ScoreGauge score={50} label="ATS Score" />)
    expect(screen.queryByText('Moderate risk')).toBeNull()
  })

  it('renders an SVG circle gauge', () => {
    const { container } = render(<ScoreGauge score={80} label="Score" />)
    const svg = container.querySelector('svg')
    expect(svg).not.toBeNull()
    const circles = container.querySelectorAll('circle')
    expect(circles.length).toBe(2) // background + progress circle
  })
})
