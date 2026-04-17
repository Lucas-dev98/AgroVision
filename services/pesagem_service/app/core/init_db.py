"""Database initialization with retry logic"""
import time
import logging
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.core.database import engine
from app.models import Base

logger = logging.getLogger(__name__)


def init_db(max_retries: int = 5, retry_interval: int = 2):
    """
    Inicializar banco de dados com retry logic
    
    Args:
        max_retries: Número máximo de tentativas
        retry_interval: Intervalo entre tentativas em segundos
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentando conectar ao banco de dados (tentativa {attempt + 1}/{max_retries})...")
            
            # Verificar conexão
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("✅ Conexão com banco de dados estabelecida!")
            
            # Criar tabelas
            logger.info("Criando tabelas...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Tabelas criadas com sucesso!")
            return True
            
        except OperationalError as e:
            logger.warning(f"❌ Erro de conexão: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Aguardando {retry_interval}s antes de tentar novamente...")
                time.sleep(retry_interval)
            else:
                logger.error(f"Falha ao conectar ao banco após {max_retries} tentativas!")
                raise
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise
