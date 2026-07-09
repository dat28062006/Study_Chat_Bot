import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

// This is a simple dummy test to verify Vitest is configured correctly.
describe('Basic Frontend Test', () => {
  it('renders a dummy component', () => {
    render(<div><h1>Study Chat Bot</h1></div>)
    
    const heading = screen.getByRole('heading', { name: /Study Chat Bot/i })
    expect(heading).toBeInTheDocument()
  })
})
