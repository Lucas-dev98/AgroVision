import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import useAuth from '@hooks/useAuth'
import LoginForm from '@components/organisms/LoginForm'
import RegisterForm from '@components/organisms/RegisterForm'
import ForgotPasswordForm from '@components/organisms/ForgotPasswordForm'
import ResetPasswordForm from '@components/organisms/ResetPasswordForm'
import Dashboard from '@pages/Dashboard'

/**
 * Componente de rota privada
 * Redireciona para login se o usuário não estiver autenticado
 */
const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div>Carregando...</div>
  }

  return isAuthenticated ? (
    <>{children}</>
  ) : (
    <Navigate to="/login" replace />
  )
}

/**
 * Componente de rota pública
 * Redireciona para dashboard se o usuário já estiver autenticado
 */
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div>Carregando...</div>
  }

  return !isAuthenticated ? (
    <>{children}</>
  ) : (
    <Navigate to="/dashboard" replace />
  )
}

/**
 * Configuração de rotas da aplicação
 */
const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Rotas públicas */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginForm />
          </PublicRoute>
        }
      />
      <Route
        path="/cadastro"
        element={
          <PublicRoute>
            <RegisterForm />
          </PublicRoute>
        }
      />
      <Route
        path="/esqueci-senha"
        element={
          <PublicRoute>
            <ForgotPasswordForm />
          </PublicRoute>
        }
      />
      <Route
        path="/reset-password"
        element={
          <PublicRoute>
            <ResetPasswordForm />
          </PublicRoute>
        }
      />

      {/* Rotas privadas */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />

      {/* Rota padrão */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Rota 404 */}
      <Route path="*" element={<div>Página não encontrada</div>} />
    </Routes>
  )
}

export default AppRoutes
