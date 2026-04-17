#!/bin/bash

# =============================================================================
# AgroVision Model Training Script
# =============================================================================
# Script para treinar os 4 modelos do AgroVision com diferentes opções
# 
# Uso:
#   chmod +x train_models.sh
#   ./train_models.sh              # Treinar todos (sintético)
#   ./train_models.sh behavior     # Treinar só comportamento
#   ./train_models.sh --real       # Treinar com dados reais
#   ./train_models.sh --finetune   # Fine-tuning com transfer learning
#   ./train_models.sh --all        # Todos os passos (recomendado)
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações padrão
MODELS=("behavior" "anomaly" "reid" "temporal")
EPOCHS=50
BATCH_SIZE=32
DEVICE="cpu"
USE_REAL_DATA=false
RESUME_CHECKPOINT=false
FINETUNE=false

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

show_help() {
    cat << EOF
${BLUE}==================================================================${NC}
${BLUE}AgroVision Model Training${NC}
${BLUE}==================================================================${NC}

${GREEN}USAGE:${NC}
  ./train_models.sh [OPTION] [MODELS]

${GREEN}OPTIONS:${NC}
  --quick           Treinar com dados sintéticos (padrão, ~30 min)
  --real            Treinar com dados reais do MongoDB (~2-3 horas)
  --finetune        Fine-tuning com transfer learning (~30 min)
  --resume          Retomar de checkpoint anterior
  --all             Executar pipeline completo (Quick + Real + Finetune)
  --device {cpu|cuda}
                    Dispositivo (padrão: cpu)
  --epochs N        Número de épocas (padrão: 50)
  --batch-size N    Tamanho do batch (padrão: 32)
  --help            Mostrar esta ajuda

${GREEN}MODELS:${NC}
  behavior          Classificação de comportamento
  anomaly           Detecção de anomalias
  reid              Re-identificação entre câmeras
  temporal          Análise temporal de séries
  all               Todos os modelos (padrão)

${GREEN}EXEMPLOS:${NC}
  # Treinar todos os modelos com dados sintéticos
  ./train_models.sh

  # Treinar só comportamento com GPU
  ./train_models.sh --device cuda behavior

  # Treinar todos com dados reais
  ./train_models.sh --real

  # Pipeline completo (recomendado para produção)
  ./train_models.sh --all

  # Fine-tuning com learning rate reduzido
  ./train_models.sh --finetune --device cuda --epochs 20

${BLUE}==================================================================${NC}
EOF
}

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}▶️  $1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# =============================================================================
# VALIDAÇÕES PRÉ-TREINAMENTO
# =============================================================================

validate_environment() {
    print_header "Validando Ambiente"
    
    # Verificar Python
    if ! command -v python &> /dev/null; then
        print_error "Python não encontrado"
        exit 1
    fi
    print_success "Python encontrado: $(python --version)"
    
    # Verificar virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_error "Virtual environment não ativado"
        print_info "Execute: source venv/bin/activate"
        exit 1
    fi
    print_success "Virtual environment: $VIRTUAL_ENV"
    
    # Verificar PyTorch
    if ! python -c "import torch" 2>/dev/null; then
        print_error "PyTorch não instalado"
        print_info "Execute: pip install torch torchvision"
        exit 1
    fi
    print_success "PyTorch: $(python -c 'import torch; print(torch.__version__)')"
    
    # Verificar GPU
    if [ "$DEVICE" = "cuda" ]; then
        if ! python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
            print_error "CUDA não disponível"
            print_info "Alterando para CPU..."
            DEVICE="cpu"
        else
            GPU_NAME=$(python -c "import torch; print(torch.cuda.get_device_name(0))")
            print_success "GPU disponível: $GPU_NAME"
        fi
    else
        print_info "Usando CPU para treinamento"
    fi
    
    # Verificar MongoDB (se dados reais)
    if [ "$USE_REAL_DATA" = true ]; then
        if ! python -c "import motor" 2>/dev/null; then
            print_error "Motor (MongoDB async driver) não instalado"
            print_info "Execute: pip install motor"
            exit 1
        fi
    fi
    
    echo ""
}

# =============================================================================
# TREINAMENTO
# =============================================================================

train_model() {
    local model=$1
    
    print_header "Treinando Modelo: $model"
    
    # Construir comando
    local cmd="python -m app.training.train_real_data"
    cmd="$cmd --model $model"
    cmd="$cmd --epochs $EPOCHS"
    cmd="$cmd --batch-size $BATCH_SIZE"
    cmd="$cmd --device $DEVICE"
    
    if [ "$USE_REAL_DATA" = true ]; then
        cmd="$cmd --use-real-data"
    fi
    
    if [ "$RESUME_CHECKPOINT" = true ]; then
        cmd="$cmd --resume-checkpoint"
    fi
    
    print_info "Comando: $cmd"
    echo ""
    
    # Executar
    if eval "$cmd"; then
        print_success "$model treinado com sucesso!"
    else
        print_error "Falha ao treinar $model"
        return 1
    fi
    echo ""
}

train_all_models() {
    print_header "Iniciando Treinamento de Todos os Modelos"
    
    echo -e "${YELLOW}Configuração:${NC}"
    echo "  Modelos: ${MODELS[@]}"
    echo "  Épocas: $EPOCHS"
    echo "  Batch Size: $BATCH_SIZE"
    echo "  Dispositivo: $DEVICE"
    echo "  Dados Reais: $USE_REAL_DATA"
    echo ""
    
    for model in "${MODELS[@]}"; do
        if ! train_model "$model"; then
            print_error "Falha no treinamento"
            exit 1
        fi
    done
    
    print_success "Todos os modelos treinados!"
}

# =============================================================================
# VALIDAÇÃO PÓS-TREINAMENTO
# =============================================================================

validate_models() {
    print_header "Validando Modelos Treinados"
    
    for model in "${MODELS[@]}"; do
        local checkpoint="models/${model}_model.pt"
        
        if [ -f "$checkpoint" ]; then
            print_success "$model: Checkpoint encontrado"
        else
            print_error "$model: Checkpoint não encontrado em $checkpoint"
        fi
    done
    
    echo ""
}

# =============================================================================
# MENU INTERATIVO
# =============================================================================

show_menu() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   AgroVision - Seleção de Treinamento   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "1) Treinar com Dados Sintéticos (Rápido, ~30 min)"
    echo "2) Treinar com Dados Reais (Longo, ~2-3 horas)"
    echo "3) Fine-tuning com Transfer Learning (~30 min)"
    echo "4) Pipeline Completo Recomendado (~3-4 horas)"
    echo "5) Sair"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    # Se sem argumentos, mostrar menu
    if [ $# -eq 0 ]; then
        validate_environment
        
        while true; do
            show_menu
            read -p "Escolha uma opção (1-5): " choice
            
            case $choice in
                1)
                    echo ""
                    MODELS=("behavior" "anomaly" "reid" "temporal")
                    EPOCHS=50
                    USE_REAL_DATA=false
                    DEVICE="cpu"
                    train_all_models
                    validate_models
                    break
                    ;;
                2)
                    echo ""
                    read -p "Usar GPU? (s/n) [s]: " use_gpu
                    if [ "$use_gpu" != "n" ]; then
                        DEVICE="cuda"
                    fi
                    MODELS=("behavior" "anomaly" "reid" "temporal")
                    EPOCHS=100
                    USE_REAL_DATA=true
                    train_all_models
                    validate_models
                    break
                    ;;
                3)
                    echo ""
                    MODELS=("behavior" "anomaly" "reid" "temporal")
                    EPOCHS=20
                    USE_REAL_DATA=true
                    DEVICE="cuda"
                    FINETUNE=true
                    train_all_models
                    validate_models
                    break
                    ;;
                4)
                    echo ""
                    print_header "Pipeline Completo (Recomendado)"
                    
                    # Fase 1: Quick
                    print_info "Fase 1: Treinamento Rápido (Dados Sintéticos)"
                    EPOCHS=10
                    USE_REAL_DATA=false
                    DEVICE="cpu"
                    train_all_models
                    
                    # Fase 2: Real
                    print_info "Fase 2: Treinamento com Dados Reais"
                    EPOCHS=20
                    USE_REAL_DATA=true
                    DEVICE="cuda"
                    train_all_models
                    
                    # Fase 3: Finetune
                    print_info "Fase 3: Fine-tuning"
                    EPOCHS=10
                    FINETUNE=true
                    train_all_models
                    
                    validate_models
                    break
                    ;;
                5)
                    echo "Saindo..."
                    exit 0
                    ;;
                *)
                    echo "Opção inválida"
                    ;;
            esac
        done
        
        print_success "Treinamento concluído!"
        echo -e "${GREEN}Próximos passos:${NC}"
        echo "  1. Verificar modelos em: services/ml_service/models/"
        echo "  2. Testar com: pytest tests/test_phase34_prediction_api.py -v"
        echo "  3. Fazer deploy: make up && make health"
        
    else
        # Processar argumentos
        while [[ $# -gt 0 ]]; do
            case $1 in
                --help)
                    show_help
                    exit 0
                    ;;
                --quick)
                    USE_REAL_DATA=false
                    DEVICE="cpu"
                    shift
                    ;;
                --real)
                    USE_REAL_DATA=true
                    DEVICE="cuda"
                    shift
                    ;;
                --finetune)
                    FINETUNE=true
                    USE_REAL_DATA=true
                    EPOCHS=20
                    DEVICE="cuda"
                    shift
                    ;;
                --resume)
                    RESUME_CHECKPOINT=true
                    shift
                    ;;
                --all)
                    print_header "Pipeline Completo"
                    EPOCHS=10
                    USE_REAL_DATA=false
                    train_all_models
                    EPOCHS=20
                    USE_REAL_DATA=true
                    DEVICE="cuda"
                    train_all_models
                    EPOCHS=10
                    FINETUNE=true
                    train_all_models
                    validate_models
                    exit 0
                    ;;
                --device)
                    DEVICE="$2"
                    shift 2
                    ;;
                --epochs)
                    EPOCHS="$2"
                    shift 2
                    ;;
                --batch-size)
                    BATCH_SIZE="$2"
                    shift 2
                    ;;
                behavior|anomaly|reid|temporal)
                    MODELS=("$1")
                    shift
                    ;;
                *)
                    print_error "Opção desconhecida: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
        
        validate_environment
        train_all_models
        validate_models
    fi
}

# Executar
cd "$(dirname "$0")/services/ml_service" 2>/dev/null || cd services/ml_service
main "$@"
