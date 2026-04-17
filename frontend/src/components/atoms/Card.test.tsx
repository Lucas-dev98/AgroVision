import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Card from './Card'

describe('Card Component', () => {
  it('renders card with children', () => {
    render(<Card>Test content</Card>)
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('renders with title', () => {
    render(<Card title="Card Title">Content</Card>)
    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('applies base styles', () => {
    const { container } = render(<Card>Content</Card>)
    const card = container.firstChild
    expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow-md', 'p-4')
  })

  it('handles click events when onClick is provided', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    const { container } = render(
      <Card onClick={handleClick}>Content</Card>
    )
    const card = container.firstChild

    await user.click(card as HTMLElement)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is not clickable without onClick handler', () => {
    const { container } = render(<Card>Content</Card>)
    const card = container.firstChild
    expect(card).not.toHaveAttribute('role', 'button')
  })

  it('has button role when clickable', () => {
    const handleClick = vi.fn()
    const { container } = render(
      <Card onClick={handleClick}>Content</Card>
    )
    const card = container.firstChild
    expect(card).toHaveAttribute('role', 'button')
  })

  it('is keyboard accessible', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    const { container } = render(
      <Card onClick={handleClick}>Content</Card>
    )
    const card = container.firstChild as HTMLElement

    card.focus()
    await user.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalled()
  })

  it('accepts custom className', () => {
    const { container } = render(
      <Card className="custom-class">Content</Card>
    )
    const card = container.firstChild
    expect(card).toHaveClass('custom-class')
  })

  it('renders complex children', () => {
    render(
      <Card title="Complex Card">
        <div>
          <p>Paragraph 1</p>
          <p>Paragraph 2</p>
        </div>
      </Card>
    )
    expect(screen.getByText('Paragraph 1')).toBeInTheDocument()
    expect(screen.getByText('Paragraph 2')).toBeInTheDocument()
  })
})
