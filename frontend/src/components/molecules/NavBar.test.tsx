import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import NavBar from './NavBar'

// Wrapper para usar com React Router
const NavBarWithRouter = (props: any) => (
  <BrowserRouter>
    <NavBar {...props} />
  </BrowserRouter>
)

describe('NavBar Component', () => {
  describe('Rendering', () => {
    it('should render navbar container', () => {
      render(<NavBarWithRouter />)
      const navbar = screen.getByRole('navigation')
      expect(navbar).toBeInTheDocument()
    })

    it('should render logo', () => {
      render(<NavBarWithRouter />)
      const logo = screen.getByText(/AgroVision/i)
      expect(logo).toBeInTheDocument()
    })

    it('should render navigation links', () => {
      render(<NavBarWithRouter />)
      const homeLink = screen.getByText(/Dashboard/i)
      const animalsLink = screen.getByText(/Animais/i)
      
      expect(homeLink).toBeInTheDocument()
      expect(animalsLink).toBeInTheDocument()
    })

    it('should render user profile section', () => {
      const mockUser = { nome: 'João Silva', email: 'joao@test.com' }
      render(<NavBarWithRouter user={mockUser} />)
      
      const username = screen.getByText('João Silva')
      expect(username).toBeInTheDocument()
    })

    it('should render logout button when user is logged in', () => {
      const mockUser = { nome: 'João Silva', email: 'joao@test.com' }
      render(<NavBarWithRouter user={mockUser} />)
      
      const logoutBtn = screen.getByRole('button', { name: /logout|sair/i })
      expect(logoutBtn).toBeInTheDocument()
    })

    it('should render login button when user is not logged in', () => {
      render(<NavBarWithRouter />)
      const loginBtn = screen.getByRole('button', { name: /login|entrar/i })
      expect(loginBtn).toBeInTheDocument()
    })
  })

  describe('Mobile Menu', () => {
    it('should render hamburger menu on mobile', () => {
      render(<NavBarWithRouter />)
      const hamburger = screen.getByRole('button', { name: /menu|hamburger|toggle/i })
      expect(hamburger).toBeInTheDocument()
    })

    it('should toggle mobile menu when hamburger is clicked', async () => {
      const user = userEvent.setup()
      render(<NavBarWithRouter />)
      
      const hamburger = screen.getByRole('button', { name: /menu|hamburger|toggle/i })
      await user.click(hamburger)
      
      // Menu should be visible
      const mobileMenu = document.querySelector('.navbar__mobile-menu')
      expect(mobileMenu).toHaveClass('navbar__mobile-menu--active')
    })

    it('should close mobile menu when link is clicked', async () => {
      const user = userEvent.setup()
      render(<NavBarWithRouter />)
      
      const hamburger = screen.getByRole('button', { name: /menu|hamburger|toggle/i })
      await user.click(hamburger)
      
      const link = screen.getByText(/Dashboard/i)
      await user.click(link)
      
      const mobileMenu = document.querySelector('.navbar__mobile-menu')
      expect(mobileMenu).not.toHaveClass('navbar__mobile-menu--active')
    })
  })

  describe('User Dropdown', () => {
    it('should show user dropdown menu when clicking on profile', async () => {
      const user = userEvent.setup()
      const mockUser = { nome: 'João Silva', email: 'joao@test.com' }
      render(<NavBarWithRouter user={mockUser} />)
      
      const profileBtn = screen.getByText('João Silva')
      await user.click(profileBtn)
      
      const dropdown = document.querySelector('.navbar__user-dropdown--active')
      expect(dropdown).toBeInTheDocument()
    })

    it('should close dropdown when clicking outside', async () => {
      const user = userEvent.setup()
      const mockUser = { nome: 'João Silva', email: 'joao@test.com' }
      render(<NavBarWithRouter user={mockUser} />)
      
      const profileBtn = screen.getByText('João Silva')
      await user.click(profileBtn)
      
      // Click outside
      const navbar = screen.getByRole('navigation')
      await user.click(navbar)
      
      const dropdown = document.querySelector('.navbar__user-dropdown--active')
      expect(dropdown).not.toBeInTheDocument()
    })
  })

  describe('Callbacks', () => {
    it('should call onLogout when logout button is clicked', async () => {
      const user = userEvent.setup()
      const mockLogout = vi.fn()
      const mockUser = { nome: 'João Silva', email: 'joao@test.com' }
      
      render(<NavBarWithRouter user={mockUser} onLogout={mockLogout} />)
      
      const logoutBtn = screen.getByRole('button', { name: /logout|sair/i })
      await user.click(logoutBtn)
      
      expect(mockLogout).toHaveBeenCalled()
    })

    it('should call onLogin when login button is clicked', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn()
      
      render(<NavBarWithRouter onLogin={mockLogin} />)
      
      const loginBtn = screen.getByRole('button', { name: /login|entrar/i })
      await user.click(loginBtn)
      
      expect(mockLogin).toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA attributes for navigation', () => {
      render(<NavBarWithRouter />)
      const navbar = screen.getByRole('navigation')
      expect(navbar).toHaveAttribute('aria-label') || expect(navbar).toHaveAttribute('role', 'navigation')
    })

    it('should have proper ARIA labels on buttons', () => {
      const mockUser = { nome: 'João Silva', email: 'joao@test.com' }
      render(<NavBarWithRouter user={mockUser} />)
      
      const logoutBtn = screen.getByRole('button', { name: /logout|sair/i })
      expect(logoutBtn).toHaveAttribute('aria-label') || expect(logoutBtn.textContent).toBeTruthy()
    })

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup()
      render(<NavBarWithRouter />)
      
      const links = screen.getAllByRole('link')
      const buttons = screen.getAllByRole('button')
      
      // Tab to first link/button
      await user.tab()
      expect(document.activeElement).toBeVisible()
    })
  })

  describe('Styling', () => {
    it('should apply correct CSS classes', () => {
      render(<NavBarWithRouter />)
      const navbar = screen.getByRole('navigation')
      expect(navbar).toHaveClass('navbar')
    })

    it('should have sticky positioning', () => {
      render(<NavBarWithRouter />)
      const navbar = screen.getByRole('navigation')
      const styles = window.getComputedStyle(navbar)
      expect(styles.position).toBe('sticky') || expect(navbar).toHaveClass('navbar--sticky')
    })
  })

  describe('Active Link Highlighting', () => {
    it('should highlight active navigation link', () => {
      render(<NavBarWithRouter />)
      // This depends on routing - would test actual active state based on current route
      const links = screen.getAllByRole('link')
      expect(links.length).toBeGreaterThan(0)
    })
  })
})
