import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button from './Button'

describe('Button Component', () => {
  it('renders with default props', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(<Button onClick={handleClick}>Click</Button>)
    const button = screen.getByRole('button')
    
    await user.click(button)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('renders with primary variant', () => {
    render(<Button variant="primary">Primary</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-blue-600')
  })

  it('renders with secondary variant', () => {
    render(<Button variant="secondary">Secondary</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-gray-200')
  })

  it('renders with danger variant', () => {
    render(<Button variant="danger">Delete</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-red-600')
  })

  it('renders with small size', () => {
    render(<Button size="sm">Small</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('px-3', 'py-1', 'text-sm')
  })

  it('renders with medium size', () => {
    render(<Button size="md">Medium</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('px-4', 'py-2', 'text-base')
  })

  it('renders with large size', () => {
    render(<Button size="lg">Large</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('px-6', 'py-3', 'text-lg')
  })

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveTextContent('...')
    expect(button).toBeDisabled()
  })

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('passes through custom className', () => {
    render(<Button className="custom-class">Custom</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('accepts all standard button attributes', () => {
    const { container } = render(
      <Button type="submit" aria-label="custom-label">
        Submit
      </Button>
    )
    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('type', 'submit')
    expect(button).toHaveAttribute('aria-label', 'custom-label')
  })
})
