// Componentes de autenticação
export { default as LoginForm } from './components/organisms/LoginForm'
export { default as RegisterForm } from './components/organisms/RegisterForm'
export { default as MFAVerification } from './components/organisms/MFAVerification'
export { default as ForgotPasswordForm } from './components/organisms/ForgotPasswordForm'
export { default as ResetPasswordForm } from './components/organisms/ResetPasswordForm'

// Serviços
export { default as authService } from './services/authService'
export type { 
  LoginResponse, 
  LoginResponseWithMFA,
  RegisterData, 
  RegisterResponse 
} from './services/authService'

// Hooks
export { default as useAuth } from './hooks/useAuth'
export { default as useMFA } from './hooks/useMFA'
export type { AuthUser } from './hooks/useAuth'
export type { MFAState } from './hooks/useMFA'

// Rotas
export { default as AppRoutes } from './routes/AppRoutes'
