# 🛣️ Roadmap: Implementação Frontend Completo

## Status Atual: 28% de Cobertura

### Semana 1: Correções Críticas (Animal Service)

#### Day 1-2: Corrigir API Service
**Arquivo:** `frontend/src/services/api.ts`

```typescript
// ANTES (❌ Errado)
async getAnimals(): Promise<PaginatedResponse<Animal>> {
  const response = await this.client.get('/animais')
  return response.data
}

// DEPOIS (✅ Correto)
async getAnimals(): Promise<PaginatedResponse<Animal>> {
  const response = await this.client.get('/api/v1/animals')
  return response.data
}
```

**Mudanças necessárias:**
- Corrigir `/animais` → `/api/v1/animals`
- Corrigir `/pesagens` → `/api/v1/pesagens`
- Corrigir `/cotacoes` → `/api/v1/cotacoes`
- Adicionar novos endpoints: `getAnimalByRfid()`, `getPesagemHistorico()`, `getCotacaoAtual()`

#### Day 3: Implementar CRUD Animal Completo
**Criar:** `frontend/src/hooks/useAnimalDetail.ts`
```typescript
export function useAnimalDetail(animalId: number) {
  const [animal, setAnimal] = useState<Animal | null>(null)
  const [pesagens, setPesagens] = useState<Pesagem[]>([])
  const [loading, setLoading] = useState(false)
  
  const fetchAnimal = async () => {
    setLoading(true)
    try {
      const data = await apiService.getAnimal(animalId)
      setAnimal(data)
      
      const pesagensData = await apiService.getPesagens(animalId)
      setPesagens(pesagensData)
    } finally {
      setLoading(false)
    }
  }
  
  // ... retornar data, update, delete, etc
}
```

**Criar:** `frontend/src/pages/AnimalDetailPage.tsx`
```typescript
function AnimalDetailPage() {
  const { animalId } = useParams()
  const { animal, pesagens, updateAnimal, deleteAnimal } = useAnimalDetail(parseInt(animalId))
  
  return (
    <div>
      <AnimalForm animal={animal} onSubmit={updateAnimal} />
      <PesagemList pesagens={pesagens} />
      <Button onClick={deleteAnimal}>Deletar Animal</Button>
    </div>
  )
}
```

#### Day 4-5: Melhorar Dashboard
**Atualizar:** `frontend/src/pages/Dashboard.tsx`
- ✅ Adicionar botão "Novo Animal" funcional
- ✅ Adicionar ícones de ação (editar, deletar, detalhes)
- ✅ Integrar com AnimalDetailPage
- ✅ Adicionar filtros e busca

---

### Semana 2: Implementar Pesagem Service

#### Day 1-2: Criar Hook de Pesagem
**Criar:** `frontend/src/hooks/usePesagem.ts`
```typescript
export function usePesagem() {
  const [pesagens, setPesagens] = useState<Pesagem[]>([])
  const [loading, setLoading] = useState(false)
  
  const createPesagem = async (animalId: number, peso: number) => {
    const data = await apiService.createPesagem({
      animal_id: animalId,
      peso_kg: peso,
      data: new Date().toISOString().split('T')[0]
    })
    setPesagens([...pesagens, data])
    return data
  }
  
  const getHistorico = async (animalId: number) => {
    const data = await apiService.getPesagemHistorico(animalId)
    setPesagens(data)
  }
  
  const getGanho = async (animalId: number) => {
    // Calcular ganho de peso
    return apiService.getPesagemGanho(animalId)
  }
  
  return { pesagens, loading, createPesagem, getHistorico, getGanho }
}
```

#### Day 3: Criar Componentes de Pesagem
**Criar:** `frontend/src/components/organisms/PesagemForm.tsx`
```typescript
function PesagemForm({ animalId, onSubmit }) {
  const [peso, setPeso] = useState('')
  const [data, setData] = useState(new Date().toISOString().split('T')[0])
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    await onSubmit({ animal_id: animalId, peso_kg: parseFloat(peso), data })
    setPeso('')
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <Input label="Peso (kg)" value={peso} onChange={e => setPeso(e.target.value)} />
      <Input label="Data" type="date" value={data} onChange={e => setData(e.target.value)} />
      <Button type="submit">Registrar Pesagem</Button>
    </form>
  )
}
```

**Criar:** `frontend/src/components/organisms/PesagemChart.tsx`
```typescript
function PesagemChart({ pesagens }) {
  // Integrar com Chart.js ou Recharts
  return <LineChart data={pesagens} />
}
```

#### Day 4-5: Integrar Pesagem nas Páginas
- Adicionar PesagemForm no AnimalDetailPage
- Mostrar gráfico de histórico
- Calcular e exibir ganho de peso
- Mostrar última pesagem na dashboard

---

### Semana 3: Implementar Cotacao Service

#### Day 1-2: Criar Hook e Página de Cotação
**Criar:** `frontend/src/hooks/useCotacao.ts`
**Criar:** `frontend/src/pages/CotacaoPage.tsx`
- Listar cotações
- Mostrar cotação atual
- Exibir média
- Gráfico de histórico

#### Day 3-4: Integrar Cotação na Dashboard
- Widget mostrando cotação atual
- Mini gráfico de tendência
- Link para página completa

---

### Semana 4: Implementar Vision Service

#### Day 1-2: Criar Página de Upload
**Criar:** `frontend/src/pages/VisionPage.tsx`
- Upload de imagem
- Preview
- Botão processar

#### Day 3-4: Integrar Resultados
- Exibir animais detectados
- Análise de saúde
- Salvar resultados

#### Day 5: Integrar Câmera (opcional)
- React-webcam para captura ao vivo

---

## 📊 Métricas de Progresso

| Semana | Funcionalidade | Estimativa | Status |
|--------|---|---|---|
| 1 | Animal Service Completo | 5 dias | Not Started |
| 2 | Pesagem Service | 5 dias | Not Started |
| 3 | Cotacao Service | 4 dias | Not Started |
| 4 | Vision Service | 5 dias | Not Started |
| **TOTAL** | **Cobertura 100%** | **~19 dias** | **0%** |

---

## 🎯 Quick Wins (Fáceis de implementar)

1. **Corrigir endpoints** (1 hora)
   - Arquivos: api.ts
   - Impacto: Alta
   
2. **Adicionar botão de novo animal funcional** (2 horas)
   - Arquivos: Dashboard.tsx, AnimalForm.tsx
   - Impacto: Alta

3. **Implementar deletar animal** (1 hora)
   - Arquivos: Dashboard.tsx
   - Impacto: Alta

4. **Busca por RFID** (2 horas)
   - Arquivos: Dashboard.tsx, api.ts
   - Impacto: Média

---

## 🚀 Próximos Passos Imediatos

1. **Hoje:** Corrigir endpoints (1 hora)
2. **Amanhã:** Implementar CRUD completo do Animal (4 horas)
3. **Esta semana:** Adicionar Pesagem básico (5 horas)
4. **Semana que vem:** Cotação e Vision

---

## 📝 Commits Sugeridos

```bash
# Commit 1
git commit -m "fix: corrigir endpoints da API em api.ts"

# Commit 2
git commit -m "feat: implementar CRUD completo de animais"

# Commit 3
git commit -m "feat: adicionar serviço e página de pesagens"

# Commit 4
git commit -m "feat: adicionar serviço e página de cotações"

# Commit 5
git commit -m "feat: adicionar upload e processamento de imagens (Vision)"
```

---

**Tempo total estimado: 3-4 semanas para 100% de cobertura**

Começar pelos Quick Wins para máximo impacto com mínimo esforço!

