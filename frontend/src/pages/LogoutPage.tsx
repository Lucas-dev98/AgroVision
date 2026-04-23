import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * Página de logout
 * Limpa os tokens e redireciona para login
 */
const LogoutPage: React.FC = () => {
  const navigate = useNavigate()

  useEffect(() => {
    // Limpar localStorage e fazer logout
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    sessionStorage.clear()
    
    // Pequeño delay para garantir que os tokens foram removidos
    setTimeout(() => {
      // Fazer reload da página para que o React atualize o estado
      window.location.href = '/login'
    }, 100)
  }, [navigate])

  return <div style={{ padding: '20px' }}>Saindo...</div>
}

export default LogoutPage
