#!/usr/bin/env python
"""Script para validar Docker Compose setup"""
import subprocess
import time
import requests
import sys
from typing import Tuple, Optional

# Configuração de services
SERVICES = {
    "animal-service": ("http://localhost:8000/health", "Animal Service"),
    "pesagem-service": ("http://localhost:8001/health", "Pesagem Service"),
    "cotacao-service": ("http://localhost:8002/health", "Cotacao Service"),
}

CONTAINERS = {
    "agrovision-db": "PostgreSQL Database",
    "agrovision-redis": "Redis Cache",
    "agrovision-animal-service": "Animal Service",
    "agrovision-pesagem-service": "Pesagem Service",
    "agrovision-cotacao-service": "Cotacao Service",
}


def run_cmd(cmd: str) -> Tuple[int, str, str]:
    """Executar comando shell"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def check_containers() -> bool:
    """Verificar se todos os containers estão rodando"""
    print("\n🐳 Verificando containers...")
    all_running = True
    
    for container, description in CONTAINERS.items():
        cmd = f"docker ps --filter name={container} --format '{{{{.State}}}}'"
        code, out, err = run_cmd(cmd)
        
        if code == 0 and "running" in out:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NÃO RODANDO")
            all_running = False
    
    return all_running


def check_services() -> bool:
    """Verificar se os serviços estão respondendo"""
    print("\n🌐 Verificando serviços...")
    all_healthy = True
    
    for service, (url, name) in SERVICES.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {name} - {url}")
            else:
                print(f"  ⚠️  {name} - Status {response.status_code}")
                all_healthy = False
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {name} - Conexão recusada")
            all_healthy = False
        except requests.exceptions.Timeout:
            print(f"  ⏱️  {name} - Timeout")
            all_healthy = False
        except Exception as e:
            print(f"  ❌ {name} - Erro: {str(e)}")
            all_healthy = False
    
    return all_healthy


def check_database() -> bool:
    """Verificar conexão com banco de dados"""
    print("\n🗄️  Verificando banco de dados...")
    
    cmd = 'docker-compose exec -T db psql -U agrovision -d agrovision -c "SELECT version();"'
    code, out, err = run_cmd(cmd)
    
    if code == 0 and "PostgreSQL" in out:
        print(f"  ✅ PostgreSQL - Conectado")
        return True
    else:
        print(f"  ❌ PostgreSQL - Erro: {err}")
        return False


def check_redis() -> bool:
    """Verificar conexão com Redis"""
    print("\n💾 Verificando Redis...")
    
    cmd = 'docker-compose exec -T redis redis-cli ping'
    code, out, err = run_cmd(cmd)
    
    if code == 0 and "PONG" in out:
        print(f"  ✅ Redis - Conectado")
        return True
    else:
        print(f"  ❌ Redis - Erro: {err}")
        return False


def check_docker_compose() -> bool:
    """Verificar se docker-compose está instalado"""
    print("\n🔧 Verificando dependências...")
    
    cmd = "docker-compose --version"
    code, out, err = run_cmd(cmd)
    
    if code == 0:
        print(f"  ✅ {out.strip()}")
        return True
    else:
        print(f"  ❌ Docker Compose não encontrado")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 VALIDAÇÃO DO DOCKER COMPOSE - AgroVision")
    print("=" * 60)
    
    # Verificar docker-compose
    if not check_docker_compose():
        print("\n❌ Docker Compose não está instalado!")
        sys.exit(1)
    
    # Aguardar um pouco para containers iniciarem
    time.sleep(2)
    
    # Executar verificações
    checks = {
        "Containers": check_containers(),
        "Database": check_database(),
        "Redis": check_redis(),
        "Services": check_services(),
    }
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO")
    print("=" * 60)
    
    for check_name, result in checks.items():
        status = "✅ OK" if result else "❌ FALHA"
        print(f"  {check_name}: {status}")
    
    all_ok = all(checks.values())
    
    print("=" * 60)
    if all_ok:
        print("✅ TUDO FUNCIONANDO PERFEITAMENTE!")
        print("\n📍 Acesse os serviços em:")
        print("  - Animal Service: http://localhost:8000/docs")
        print("  - Pesagem Service: http://localhost:8001/docs")
        print("  - Cotacao Service: http://localhost:8002/docs")
        print("=" * 60)
        return 0
    else:
        print("❌ ALGUNS COMPONENTES FALHARAM!")
        print("\n🔧 Dicas:")
        print("  1. Verificar logs: make logs")
        print("  2. Reiniciar stack: make restart")
        print("  3. Resetar banco: make db-reset")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro: {str(e)}")
        sys.exit(1)
