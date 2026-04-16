#!/usr/bin/env python
"""Script para testar migrations com Alembic"""
import os
import sys
import subprocess
from pathlib import Path

# Configurações
INFRA_PATH = Path(__file__).parent
ALEMBIC_PATH = INFRA_PATH / "alembic"
ALEMBIC_INI = INFRA_PATH / "alembic.ini"

# Fake DATABASE_URL for testing
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/agrovision_test"
)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

def run_alembic_command(cmd: str) -> bool:
    """Executar comando alembic"""
    try:
        result = subprocess.run(
            f"alembic -c {ALEMBIC_INI} {cmd}",
            shell=True,
            cwd=INFRA_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Erro: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"❌ Erro ao rodar alembic: {e}")
        return False


def test_migrations():
    """Testar upgrade e downgrade de migrations"""
    print("🔄 Testando migrations...")
    
    # Test upgrade
    print("\n📤 Testando upgrade...")
    if not run_alembic_command("upgrade head"):
        return False
    
    print("\n✅ Upgrade bem-sucedido!")
    
    # Test downgrade
    print("\n📥 Testando downgrade...")
    if not run_alembic_command("downgrade -1"):
        return False
    
    print("\n✅ Downgrade bem-sucedido!")
    
    # Test upgrade again
    print("\n📤 Testando upgrade novamente...")
    if not run_alembic_command("upgrade head"):
        return False
    
    print("\n✅ Todas as migrations funcionam corretamente!")
    
    # Show migration history
    print("\n📋 Histórico de migrations:")
    run_alembic_command("history")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE MIGRATIONS COM ALEMBIC")
    print("=" * 60)
    print(f"\n📦 Database: {TEST_DATABASE_URL}\n")
    
    if test_migrations():
        print("\n" + "=" * 60)
        print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTES FALHARAM!")
        print("=" * 60)
        sys.exit(1)
