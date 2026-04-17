# 🐄 AgroVision Frontend

React 18 + TypeScript + Vitest frontend para Sistema de Gestão de Rebanho, seguindo **TDD (Test-Driven Development)** rigorosamente.

## 🎯 Visão Geral

- **Framework**: React 18
- **Linguagem**: TypeScript
- **Testes**: Vitest + React Testing Library
- **Build**: Vite
- **Estilo**: Tailwind CSS (inline)
- **Design Pattern**: Atomic Design (Atoms → Molecules → Organisms)

## 📊 Estrutura Atomic Design

```
src/
├── components/
│   ├── atoms/           # Botões, Inputs, Cards (componentes base)
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   ├── Input.tsx
│   │   ├── Input.test.tsx
│   │   └── Card.tsx
│   │       Card.test.tsx
│   ├── molecules/       # Combinações de atoms (Form, NavBar)
│   └── organisms/       # Componentes complexos (Dashboard, Layout)
├── hooks/               # Hooks customizados (useAnimals, usePesagens)
├── services/            # Integração com API (apiService)
├── types/               # Types TypeScript (Animal, Pesagem, etc)
├── utils/               # Funções utilitárias
├── styles/              # CSS global
└── tests/               # Testes e fixtures
```

## 🚀 Quick Start

### 1. Instalação

```bash
# Instalar dependências
npm install

# Copiar .env.example para .env
cp .env.example .env
```

### 2. Desenvolvimento

```bash
# Start dev server (http://localhost:5173)
npm run dev

# Rodar testes em watch mode
npm run test

# UI dos testes
npm run test:ui

# Coverage
npm run test:coverage
```

### 3. Build

```bash
# Build para produção
npm run build

# Preview do build
npm run preview
```

## 🧪 Testes com TDD

Todos os componentes seguem **Test-Driven Development**:

1. **Escrever teste primeiro** (teste falha)
2. **Implementar componente** (teste passa)
3. **Refatorar** se necessário

### Rodando Testes

```bash
# Todos os testes
npm run test

# Modo watch
npm run test -- --watch

# UI interativa
npm run test:ui

# Com coverage
npm run test:coverage
```

### Exemplo de Teste

```typescript
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
    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

## 📦 Componentes Implementados

### ✅ Atoms (Base)

- **Button** - 12 testes
  - Variantes: primary, secondary, danger
  - Tamanhos: sm, md, lg
  - Estados: loading, disabled

- **Input** - 11 testes
  - Com label e helper text
  - Validação de erros
  - Full width support

- **Card** - 9 testes
  - Com título
  - Clicável/não-clicável
  - Acessibilidade (keyboard)

### 🎣 Hooks

- **useAnimals** - 8 testes
  - Busca lista de animais
  - Refetch on demand
  - Error handling

- **useAnimal** - 7 testes
  - Busca um animal específico
  - Reage a mudanças de ID

### 🔌 Services

- **apiService** - Integração com API Gateway
  - Todos os endpoints mapeados
  - Interceptor de JWT
  - Error handling

## 🎨 Styling

Usando **Tailwind CSS inline** sem import de arquivo CSS. Todos os estilos são aplicados como classes:

```tsx
<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
  Click me
</button>
```

## 🔐 Integração com API

A API Gateway está em `http://localhost:8080/api/v1`. Proxy automaticamente configurado em `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8080',
    changeOrigin: true,
  }
}
```

## 📈 Roadmap Frontend

### ✅ FASE 1: Componentes Atômicos (Concluído)
- [x] Button (12 testes)
- [x] Input (11 testes)
- [x] Card (9 testes)

### ⏳ FASE 2: Moléculas (Próximo)
- [ ] Form (combina Input + Button)
- [ ] AnimalCard (Card + dados específicos)
- [ ] NavBar (navegação)

### ⏳ FASE 3: Organismos
- [ ] AnimalList (lista de animais)
- [ ] DashboardPage (painel principal)
- [ ] AnimalDetailPage (detalhes do animal)

### ⏳ FASE 4: Integração Completa
- [ ] Login/Autenticação JWT
- [ ] Gráficos com Chart.js
- [ ] Paginação
- [ ] Filtros avançados

## 📝 Convenções

- **Testes**: Um arquivo `.test.tsx` para cada componente
- **Cobertura**: Mínimo 100%
- **Nomes**: Descriptivos e em português quando apropriado
- **Imports**: Usar path aliases (`@components/`, `@hooks/`, etc)

## 🚨 Troubleshooting

### Erro: "Cannot find module '@'"
Verifique o `vite.config.ts` e `tsconfig.json`. Os aliases devem estar em ambos.

### Testes não encontram componentes
Certifique-se que `setupFiles` está configurado em `vitest.config.ts`.

## 📚 Referências

- [React 18 Docs](https://react.dev)
- [Vitest Docs](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [Atomic Design](https://atomicdesign.bradfrost.com)
- [Tailwind CSS](https://tailwindcss.com)

## 📄 Licença

MIT
