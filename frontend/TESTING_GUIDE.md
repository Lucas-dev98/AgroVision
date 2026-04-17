# 🧪 Testing Guide - AgroVision Frontend

## Filosofia: Test-Driven Development (TDD)

Todos os componentes são criados seguindo **TDD rigorosamente**:

1. **RED**: Escrever teste que falha
2. **GREEN**: Implementar feature mínima para passar
3. **REFACTOR**: Melhorar código mantendo testes passando

---

## Setup de Testes

### Ferramentas
- **Framework**: Vitest
- **Library**: React Testing Library
- **Mocking**: Vitest vi
- **Async**: @testing-library/user-event

### Configuração
```bash
# vitest.config.ts
- globals: true (describe, it, expect sem imports)
- environment: jsdom
- setupFiles: src/tests/setup.ts
```

---

## Estrutura de Testes

### Arquivo de Teste
```typescript
// Button.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button from './Button'

describe('Button Component', () => {
  // testes aqui
})
```

### Anatomia de um Teste
```typescript
it('should render with primary variant', () => {
  // ARRANGE: preparar dados
  const label = 'Click me'

  // ACT: renderizar e interagir
  render(<Button variant="primary">{label}</Button>)

  // ASSERT: verificar resultado
  const button = screen.getByRole('button', { name: label })
  expect(button).toHaveClass('bg-blue-600')
})
```

---

## Convenções de Testes

### Nomes de Testes
```typescript
// ✅ BOM
it('should render with primary variant', () => {})
it('handles click events correctly', () => {})
it('displays error message when validation fails', () => {})

// ❌ RUIM
it('works', () => {})
it('test 1', () => {})
it('renders', () => {})
```

### Organização
```typescript
describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {})
    it('renders with label', () => {})
  })

  describe('Interactions', () => {
    it('handles click events', () => {})
    it('disables on loading', () => {})
  })

  describe('Variants', () => {
    it('applies primary styles', () => {})
    it('applies secondary styles', () => {})
  })
})
```

---

## Padrões Comuns

### Testing User Interactions
```typescript
it('handles click events', async () => {
  const handleClick = vi.fn()
  const user = userEvent.setup()

  render(<Button onClick={handleClick}>Click</Button>)

  await user.click(screen.getByRole('button'))
  
  expect(handleClick).toHaveBeenCalledTimes(1)
})
```

### Testing Form Input
```typescript
it('updates value on input change', async () => {
  const user = userEvent.setup()
  const { container } = render(<Input />)
  const input = container.querySelector('input')!

  await user.type(input, 'test value')

  expect(input.value).toBe('test value')
})
```

### Testing Async Operations
```typescript
it('fetches data on mount', async () => {
  vi.mock('@services/api')
  const { result } = renderHook(() => useAnimals())

  expect(result.current.loading).toBe(true)

  await waitFor(() => {
    expect(result.current.loading).toBe(false)
  })

  expect(result.current.animals).toEqual(mockAnimals)
})
```

### Testing Error States
```typescript
it('displays error message', () => {
  render(<Input error="This field is required" />)

  const errorMsg = screen.getByText('This field is required')
  expect(errorMsg).toBeInTheDocument()
  expect(errorMsg).toHaveClass('text-red-600')
})
```

### Testing Accessibility
```typescript
it('is keyboard accessible', async () => {
  const user = userEvent.setup()
  render(<Card onClick={vi.fn()}>Content</Card>)

  const card = screen.getByRole('button')
  card.focus()

  await user.keyboard('{Enter}')
  // verifica se callback foi chamado
})
```

---

## Queries: Prioridade de Uso

### Preferir (mais acessíveis)
```typescript
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText(/username/i)
screen.getByPlaceholderText(/email/i)
screen.getByText(/welcome/i)
```

### Evitar (menos acessíveis)
```typescript
// ❌ Não use IDs de teste como primeiro recurso
screen.getByTestId('submit-button')

// ❌ Não consulte container/elemento direto
container.querySelector('button')
```

---

## Mocking Padrões

### Mock de Módulo
```typescript
vi.mock('@services/api')

import apiService from '@services/api'

apiService.getAnimals.mockResolvedValue(mockAnimals)
```

### Mock de Função
```typescript
const handleClick = vi.fn()
const handleSubmit = vi.fn().mockResolvedValue({ success: true })

render(<Button onClick={handleClick}>Click</Button>)
expect(handleClick).toHaveBeenCalled()
```

### Mock de localStorage
```typescript
// Já configurado em src/tests/setup.ts
localStorage.getItem('token') // mockado
localStorage.setItem('token', 'abc')
```

---

## Coverage

### Rodando Coverage
```bash
npm run test:coverage
```

### Targets
- **Lines**: 100%
- **Branches**: 100%
- **Functions**: 100%
- **Statements**: 100%

### Exemplo de Coverage Report
```
src/components/atoms/Button.tsx
  Lines       : 100% (45/45)
  Branches    : 100% (12/12)
  Functions   : 100% (1/1)
  Statements  : 100% (45/45)
```

---

## Best Practices

### ✅ DO
- Testar comportamento, não implementação
- Usar `userEvent` ao invés de `fireEvent`
- Testar acessibilidade
- Usar `waitFor` para operações async
- Manter testes pequenos e focados
- Usar `beforeEach` para setup

### ❌ DON'T
- Testar detalhes de implementação
- Snapshots (são frágeis)
- Testes muito longos (split em vários)
- Mock sem necessidade
- Ignorar warnings do Testing Library
- Testar bibliotecas externas

---

## Debug de Testes

### Print DOM
```typescript
import { render, screen } from '@testing-library/react'

render(<Component />)
screen.debug() // printa o DOM no console
```

### Usar Testing Library UI
```bash
npm run test:ui
```

Abre interface interativa com:
- Próximo teste a rodar
- Visualização do componente
- Coverage inline

---

## Exemplos Completos

### Componente: Button.tsx com Testes

```typescript
// Button.test.tsx
describe('Button Component', () => {
  const variants = ['primary', 'secondary', 'danger']
  const sizes = ['sm', 'md', 'lg']

  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<Button>Click</Button>)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('renders all variants', () => {
      variants.forEach(variant => {
        const { unmount } = render(
          <Button variant={variant as any}>Button</Button>
        )
        const button = screen.getByRole('button')
        expect(button).toHaveClass(`bg-${variant}-600`)
        unmount()
      })
    })

    it('renders all sizes', () => {
      sizes.forEach(size => {
        const { unmount } = render(
          <Button size={size as any}>Button</Button>
        )
        const button = screen.getByRole('button')
        expect(button).toHaveClass(`px-${size === 'sm' ? '3' : size === 'md' ? '4' : '6'}`)
        unmount()
      })
    })
  })

  describe('Interactions', () => {
    it('calls onClick when clicked', async () => {
      const onClick = vi.fn()
      const user = userEvent.setup()

      render(<Button onClick={onClick}>Click</Button>)
      await user.click(screen.getByRole('button'))

      expect(onClick).toHaveBeenCalledOnce()
    })

    it('disables button when loading', () => {
      render(<Button loading>Click</Button>)
      const button = screen.getByRole('button')

      expect(button).toBeDisabled()
      expect(button).toHaveTextContent('...')
    })
  })
})
```

---

## Rodando Testes

```bash
# Todos os testes
npm run test

# Modo watch (rerun ao salvar)
npm run test -- --watch

# Arquivo específico
npm run test Button.test.tsx

# Com pattern
npm run test -- --grep "Button"

# UI interativa
npm run test:ui

# Com coverage
npm run test:coverage

# Com reporter JSON
npm run test -- --reporter=json
```

---

## Troubleshooting

### Teste Falhando Aleatoriamente
- Use `waitFor` para async
- Aumentar timeout: `waitFor(..., { timeout: 5000 })`
- Verificar mocks

### "act" Warning
```typescript
// Sempre use `await user.click()` ou `waitFor()`
// Não faça fireEvent sem wrapper

// ✅ CERTO
await user.click(button)

// ❌ ERRADO
fireEvent.click(button)
```

### Component Not Found
- Verificar import path
- Verificar export no index.ts
- Limpar cache: `npm run test -- --clearCache`

---

## Recursos

- [Vitest Docs](https://vitest.dev)
- [RTL Best Practices](https://testing-library.com/best-practices)
- [TDD by Example - Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [Testing Trophy - Kent Dodds](https://kentcdodds.com/blog/the-testing-trophy-and-testing-javascript)

---

**Last Updated:** 16 de abril de 2026
