# 📋 Frontend Roadmap - AgroVision

## ✅ FASE 1: Componentes Atômicos com TDD (Concluído)

### Atoms (Base Components)
- ✅ **Button** (12 testes)
  - Variantes: primary, secondary, danger
  - Tamanhos: sm, md, lg
  - Estados: loading, disabled
  - Acessibilidade total

- ✅ **Input** (11 testes)
  - Com label, helper text, error states
  - Type support: text, email, number, password
  - Validações HTML5
  - Full width option

- ✅ **Card** (9 testes)
  - Título dinâmico
  - Clicável com callback
  - Keyboard accessible
  - Hover effects

### Services
- ✅ **apiService** (integrações)
  - Animals: GET, POST, PUT, DELETE
  - Pesagens: GET, POST
  - Cotações: GET
  - Dashboard: GET single, GET all
  - Health check
  - JWT interceptor
  - 13 testes

### Hooks
- ✅ **useAnimals** (8 testes)
  - Fetch animals list
  - Refetch on demand
  - Error handling
  - Loading states

- ✅ **useAnimal** (7 testes)
  - Fetch single animal
  - ID change reactions
  - Null safety

### Tests
- ✅ **32 testes atômicos** (100% coverage target)

**Total FASE 1:** 60+ testes ✅

---

## ⏳ FASE 2: Componentes Moléculares

### Molecules (Composite Components)

**AnimalForm** (12 testes)
- Combina Input + Button
- Validação de campos
- Submit handler
- Reset functionality
```tsx
<AnimalForm onSubmit={handleSubmit} />
```

**AnimalCard** (10 testes)
- Extensão de Card com dados de Animal
- Actions (edit, delete)
- Status badge
```tsx
<AnimalCard animal={animal} onSelect={handleSelect} />
```

**SearchBar** (8 testes)
- Input com debounce
- Search icon
- Clear button
```tsx
<SearchBar onSearch={handleSearch} />
```

**NavBar** (10 testes)
- Logo + menu items
- Active route highlighting
- Mobile responsive
```tsx
<NavBar />
```

**Pagination** (12 testes)
- Previous/Next buttons
- Page indicators
- Jump to page
```tsx
<Pagination page={1} total={10} onPageChange={setPage} />
```

**Expected: 52 testes** 📊

---

## ⏳ FASE 3: Componentes Organismos

### Organisms (Page-level Components)

**AnimalsList** (15 testes)
- useAnimals hook integration
- Card grid layout
- Search + filter
- Pagination
- Empty state
- Error handling
```tsx
<AnimalsList />
```

**AnimalDetailPage** (18 testes)
- useAnimal hook
- Edit form
- Pesagens history
- Cotações info
- Delete confirmation
```tsx
<AnimalDetailPage animalId={id} />
```

**DashboardPage** (20 testes)
- Aggregated data from all services
- Key metrics (animals count, avg weight, market price)
- Charts (weight trend, price trend)
- Recent activity
```tsx
<DashboardPage />
```

**AnimalCreatePage** (12 testes)
- AnimalForm component
- API submission
- Success/error handling
- Redirect on success
```tsx
<AnimalCreatePage />
```

**LayoutPage** (10 testes)
- NavBar + content area
- Responsive sidebar
- Footer
- Context providers
```tsx
<LayoutPage>
  {children}
</LayoutPage>
```

**Expected: 75 testes** 📊

---

## ⏳ FASE 4: Páginas de Autenticação

**LoginPage** (15 testes)
- Email/password inputs
- Remember me checkbox
- Forgot password link
- JWT token storage
- Redirect on success

**RegisterPage** (15 testes)
- Registration form
- Password confirmation
- Terms acceptance
- Email validation
- Success page

**ProtectedRoute** (10 testes)
- Token verification
- Redirect to login if no token
- Role-based access

**Expected: 40 testes** 📊

---

## ⏳ FASE 5: Gráficos e Visualizações

**WeightChart** (12 testes)
- Linha chart com Chart.js
- Data points por animal
- Trend analysis
- Filtros por período

**PriceChart** (10 testes)
- Histórico de cotações
- Comparações
- Indicadores

**Expected: 22 testes** 📊

---

## ⏳ FASE 6: Integração Avançada

**Filtros Avançados**
- Múltiplos critérios
- Save/load filters
- Predefined filters

**Export/Import**
- CSV export
- PDF reports
- Excel integration

**Notificações**
- Toast messages
- Real-time alerts
- History

**Expected: 30+ testes** 📊

---

## 📈 Resumo de Cobertura por Fase

```
FASE 1: Atoms         ████████████████████ 60 testes
FASE 2: Molecules     ░░░░░░░░░░░░░░░░░░░░ 52 testes (próximo)
FASE 3: Organisms     ░░░░░░░░░░░░░░░░░░░░ 75 testes
FASE 4: Auth          ░░░░░░░░░░░░░░░░░░░░ 40 testes
FASE 5: Charts        ░░░░░░░░░░░░░░░░░░░░ 22 testes
FASE 6: Advanced      ░░░░░░░░░░░░░░░░░░░░ 30 testes

TOTAL ESTIMADO: 279 testes ✅
```

---

## 🎯 Próximos Passos

### Imediato (Esta semana)
1. Criar FASE 2: AnimalForm, AnimalCard, NavBar
2. Implementar routing com React Router
3. Documentação de componentes com Storybook

### Curto prazo (Próximas 2 semanas)
1. FASE 3: Páginas completas
2. Integração com backend 100%
3. Tests coverage 100%

### Médio prazo (Mês)
1. FASE 4: Autenticação JWT
2. FASE 5: Gráficos
3. Performance optimization

---

## 📚 Documentação de Componentes

### Storybook Setup
```bash
npm run storybook
```

Cada componente terá stories para:
- Default state
- All variants
- Loading state
- Error state
- Edge cases

### API Documentation
Todos os hooks e services têm:
- JSDoc completo
- Type definitions
- Usage examples
- Error handling patterns

---

## ✅ Checklist de Qualidade

- [x] TypeScript strict mode
- [x] 100% coverage target
- [x] TDD methodology
- [x] Accessible components (a11y)
- [x] Mobile responsive
- [ ] Performance optimized
- [ ] Error boundaries
- [ ] Loading skeletons
- [ ] Storybook docs
- [ ] E2E tests (Cypress)

---

## 📊 Métricas

### Coverage Goal: 100%
- Lines: 100%
- Branches: 100%
- Functions: 100%
- Statements: 100%

### Performance Target
- LCP: < 2.5s
- FID: < 100ms
- CLS: < 0.1

---

## 🤝 Contribuindo

Todas as novas features devem:
1. Ter testes escritos PRIMEIRO (TDD)
2. Atingir 100% coverage
3. Seguir Atomic Design
4. Estar documentadas
5. Ser acessíveis (WCAG 2.1)

---

## 🚀 Deploy

```bash
# Build for production
npm run build

# Preview
npm run preview

# Deploy (configurar CI/CD)
```

---

**Atualizado:** 16 de abril de 2026  
**Status:** ✅ FASE 1 Concluída | ⏳ FASE 2 Próximo
