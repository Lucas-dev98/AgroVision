import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Input from './Input'

describe('Input Component', () => {
  it('renders input field', () => {
    render(<Input />)
    const input = screen.getByRole('textbox')
    expect(input).toBeInTheDocument()
  })

  it('renders with label', () => {
    render(<Input label="Email" />)
    const label = screen.getByText('Email')
    expect(label).toBeInTheDocument()
  })

  it('handles input changes', async () => {
    const user = userEvent.setup()
    const { container } = render(<Input />)
    const input = container.querySelector('input') as HTMLInputElement
    
    await user.type(input, 'test value')
    expect(input.value).toBe('test value')
  })

  it('renders with placeholder', () => {
    render(<Input placeholder="Enter text" />)
    const input = screen.getByPlaceholderText('Enter text')
    expect(input).toBeInTheDocument()
  })

  it('displays error message', () => {
    render(<Input error="This field is required" />)
    const errorMsg = screen.getByText('This field is required')
    expect(errorMsg).toBeInTheDocument()
    expect(errorMsg).toHaveClass('text-red-600')
  })

  it('displays helper text when no error', () => {
    render(<Input helperText="This field is optional" />)
    const helperText = screen.getByText('This field is optional')
    expect(helperText).toBeInTheDocument()
    expect(helperText).toHaveClass('text-gray-500')
  })

  it('hides helper text when error is present', () => {
    render(
      <Input 
        error="Required" 
        helperText="This field is optional"
      />
    )
    const errorMsg = screen.getByText('Required')
    const helperText = screen.queryByText('This field is optional')
    expect(errorMsg).toBeInTheDocument()
    expect(helperText).not.toBeInTheDocument()
  })

  it('applies full width class', () => {
    const { container } = render(<Input fullWidth />)
    const wrapper = container.firstChild
    expect(wrapper).toHaveClass('w-full')
  })

  it('handles different input types', () => {
    render(<Input type="email" />)
    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('type', 'email')
  })

  it('disables input when disabled prop is true', () => {
    render(<Input disabled />)
    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
  })

  it('passes through standard HTML attributes', () => {
    render(
      <Input 
        required 
        minLength={5}
        maxLength={20}
        pattern="[0-9]*"
      />
    )
    const input = screen.getByRole('textbox')
    expect(input).toHaveAttribute('required')
    expect(input).toHaveAttribute('minlength', '5')
    expect(input).toHaveAttribute('maxlength', '20')
    expect(input).toHaveAttribute('pattern', '[0-9]*')
  })

  it('accepts custom className', () => {
    const { container } = render(<Input className="custom-class" />)
    const input = container.querySelector('input')
    expect(input).toHaveClass('custom-class')
  })
})
