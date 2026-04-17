import React, { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './NavBar.css'

interface User {
  nome: string
  email: string
}

interface NavBarProps {
  user?: User | null
  onLogout?: () => void
  onLogin?: () => void
}

const NavBar: React.FC<NavBarProps> = ({
  user = null,
  onLogout,
  onLogin,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [userDropdownOpen, setUserDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const location = useLocation()

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setUserDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location])

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const handleLogout = () => {
    setUserDropdownOpen(false)
    onLogout?.()
  }

  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      <div className="navbar__container">
        {/* Logo */}
        <Link to="/" className="navbar__logo">
          <span className="navbar__logo-icon">🐄</span>
          <span className="navbar__logo-text">AgroVision</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="navbar__desktop-menu">
          <Link 
            to="/" 
            className={`navbar__link ${isActive('/') ? 'navbar__link--active' : ''}`}
          >
            Dashboard
          </Link>
          <Link 
            to="/animals" 
            className={`navbar__link ${isActive('/animals') ? 'navbar__link--active' : ''}`}
          >
            Animais
          </Link>
          <Link 
            to="/reports" 
            className={`navbar__link ${isActive('/reports') ? 'navbar__link--active' : ''}`}
          >
            Relatórios
          </Link>
          <Link 
            to="/settings" 
            className={`navbar__link ${isActive('/settings') ? 'navbar__link--active' : ''}`}
          >
            Configurações
          </Link>
        </div>

        {/* Right Section */}
        <div className="navbar__right">
          {user ? (
            <div className="navbar__user-section" ref={dropdownRef}>
              <button
                className="navbar__user-button"
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                aria-label={`User menu for ${user.nome}`}
              >
                <span className="navbar__user-avatar">
                  {user.nome.charAt(0).toUpperCase()}
                </span>
                <span className="navbar__user-name">{user.nome}</span>
                <svg className="navbar__dropdown-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M7 10l5 5 5-5z" />
                </svg>
              </button>

              {/* User Dropdown Menu */}
              <div className={`navbar__user-dropdown ${userDropdownOpen ? 'navbar__user-dropdown--active' : ''}`}>
                <div className="navbar__user-info">
                  <p className="navbar__user-email">{user.email}</p>
                </div>
                <button
                  className="navbar__logout-button"
                  onClick={handleLogout}
                  aria-label="Logout"
                >
                  Sair
                </button>
              </div>
            </div>
          ) : (
            <button
              className="navbar__login-button"
              onClick={onLogin}
              aria-label="Login"
            >
              Entrar
            </button>
          )}

          {/* Mobile Menu Toggle */}
          <button
            className="navbar__hamburger"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            <span className="navbar__hamburger-line" />
            <span className="navbar__hamburger-line" />
            <span className="navbar__hamburger-line" />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={`navbar__mobile-menu ${mobileMenuOpen ? 'navbar__mobile-menu--active' : ''}`}>
        <Link 
          to="/" 
          className={`navbar__mobile-link ${isActive('/') ? 'navbar__mobile-link--active' : ''}`}
        >
          Dashboard
        </Link>
        <Link 
          to="/animals" 
          className={`navbar__mobile-link ${isActive('/animals') ? 'navbar__mobile-link--active' : ''}`}
        >
          Animais
        </Link>
        <Link 
          to="/reports" 
          className={`navbar__mobile-link ${isActive('/reports') ? 'navbar__mobile-link--active' : ''}`}
        >
          Relatórios
        </Link>
        <Link 
          to="/settings" 
          className={`navbar__mobile-link ${isActive('/settings') ? 'navbar__mobile-link--active' : ''}`}
        >
          Configurações
        </Link>
      </div>
    </nav>
  )
}

export default NavBar
