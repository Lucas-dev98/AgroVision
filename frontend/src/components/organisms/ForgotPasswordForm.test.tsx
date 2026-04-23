import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import ForgotPasswordForm from './ForgotPasswordForm'

// Mock do AuthService
vi.mock('@services/authService', () => ({
  default: {
    forgotPassword: vi.fn(),
  },
}))

import authService from '@services/authService'

describe('ForgotPasswordForm Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('deve renderizar formulário de esqueci minha senha', () => {
    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    expect(screen.getByText(/Esqueci Minha Senha/i)).toBeInTheDocument()
    expect(
      screen.getByText(/Insira seu CPF\/CNPJ ou email/i)
    ).toBeInTheDocument()
    expect(screen.getByLabelText(/CPF\/CNPJ ou Email/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Enviar/i })).toBeInTheDocument()
  })

  it('deve validar campo vazio', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(screen.getByText(/Campo obrigatório/i)).toBeInTheDocument()
    })
  })

  it('deve validar formato de CPF (11 dígitos)', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(
        screen.getByText(/CPF\/CNPJ deve ter 11 ou 14 dígitos/i)
      ).toBeInTheDocument()
    })
  })

  it('deve validar formato de CNPJ (14 dígitos)', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '123456789012345')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(
        screen.getByText(/CPF\/CNPJ inválido/i)
      ).toBeInTheDocument()
    })
  })

  it('deve validar formato de email', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, 'email-invalido@')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(screen.getByText(/Email inválido/i)).toBeInTheDocument()
    })
  })

  it('deve aceitar CPF válido', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockResolvedValue({
      message: 'Email enviado',
    })

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(authService.forgotPassword).toHaveBeenCalledWith('12345678901')
    })
  })

  it('deve aceitar CNPJ válido', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockResolvedValue({
      message: 'Email enviado',
    })

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901234')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(authService.forgotPassword).toHaveBeenCalledWith('12345678901234')
    })
  })

  it('deve aceitar email válido', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockResolvedValue({
      message: 'Email enviado',
    })

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, 'usuario@example.com')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(authService.forgotPassword).toHaveBeenCalledWith('usuario@example.com')
    })
  })

  it('deve exibir mensagem de sucesso', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockResolvedValue({
      message: 'Email enviado com sucesso',
    })

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(
        screen.getByText(/Email de recuperação enviado/i)
      ).toBeInTheDocument()
    })
  })

  it('deve exibir erro quando usuário não existe', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockRejectedValue(
      new Error('Usuário não encontrado')
    )

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901')
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(screen.getByText(/Usuário não encontrado/i)).toBeInTheDocument()
    })
  })

  it('deve mostrar loading enquanto envia', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                message: 'Email enviado',
              }),
            100
          )
        )
    )

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901')
    await user.click(botaoEnviar)

    // Enquanto está loading
    expect(screen.getByRole('button', { name: /Enviando/i })).toBeDisabled()
  })

  it('deve limpar erro ao digitar no campo', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    // Primeiro clique com erro
    await user.click(botaoEnviar)

    await waitFor(() => {
      expect(screen.getByText(/Campo obrigatório/i)).toBeInTheDocument()
    })

    // Digitar algo
    await user.type(input, 'a')

    // Erro deve desaparecer
    await waitFor(() => {
      expect(screen.queryByText(/Campo obrigatório/i)).not.toBeInTheDocument()
    })
  })

  it('deve ter link para voltar ao login', () => {
    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const linkVoltar = screen.getByText(/Voltar ao login/i)
    expect(linkVoltar).toBeInTheDocument()
    expect(linkVoltar.closest('a')).toHaveAttribute('href', '/login')
  })

  it('deve ter link para se cadastrar', () => {
    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const linkCadastro = screen.getByText(/Não tem conta\?|Cadastre-se/i)
    expect(linkCadastro).toBeInTheDocument()
  })

  it('deve desabilitar botão enquanto envia', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                message: 'Email enviado',
              }),
            200
          )
        )
    )

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901')
    await user.click(botaoEnviar)

    expect(botaoEnviar).toBeDisabled()
  })

  it('deve desabilitar campo enquanto envia', async () => {
    const user = userEvent.setup()
    ;(authService.forgotPassword as any).mockImplementation(
      () =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                message: 'Email enviado',
              }),
            200
          )
        )
    )

    render(
      <BrowserRouter>
        <ForgotPasswordForm />
      </BrowserRouter>
    )

    const input = screen.getByLabelText(/CPF\/CNPJ ou Email/i)
    const botaoEnviar = screen.getByRole('button', { name: /Enviar/i })

    await user.type(input, '12345678901')
    await user.click(botaoEnviar)

    expect(input).toBeDisabled()
  })
})
