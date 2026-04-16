"""Service de Agregação - FASE 10

Agrega dados de múltiplos serviços backend em um único ponto de acesso
"""
import asyncio
import logging
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("agrovision.aggregation")


class AggregationService:
    """Serviço para agregação de dados de múltiplos backends"""
    
    def __init__(self, base_urls: Optional[Dict[str, str]] = None) -> None:
        """
        Inicializar serviço de agregação
        
        Args:
            base_urls: Dicionário com URLs dos serviços
                {
                    "animal": "http://animal-service:8000",
                    "pesagem": "http://pesagem-service:8001",
                    "cotacao": "http://cotacao-service:8002"
                }
        """
        self.base_urls = base_urls or {
            "animal": "http://animal-service:8000",
            "pesagem": "http://pesagem-service:8001",
            "cotacao": "http://cotacao-service:8002"
        }
        
        self.timeout = 5.0  # 5 segundos de timeout por serviço
        self._cache: Dict[str, Any] = {}  # Cache simples em memória
    
    async def get_animal_dashboard(
        self,
        animal_id: int,
        include_fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Obter dashboard consolidado de um animal
        
        Agrupa dados de:
        - animal-service: dados do animal
        - pesagem-service: histórico de pesagens
        - cotacao-service: cotações do animal
        
        Args:
            animal_id: ID do animal
            include_fields: Campos a incluir (animal, pesagens, cotacoes)
            filters: Filtros adicionais (data, tipo, etc)
        
        Returns:
            Dict com dados agregados
        """
        try:
            # Configurar campos a incluir (padrão: todos)
            if include_fields is None:
                include_fields = ["animal", "pesagens", "cotacoes"]
            
            # Buscar dados em paralelo de todos os serviços
            tasks = []
            
            if "animal" in include_fields:
                tasks.append(("animal", self._get_animal_data(animal_id)))
            
            if "pesagens" in include_fields:
                tasks.append(("pesagens", self._get_animal_weighings(animal_id, filters)))
            
            if "cotacoes" in include_fields:
                tasks.append(("cotacoes", self._get_animal_quotes(animal_id, filters)))
            
            # Executar todas as tarefas em paralelo
            results = await asyncio.gather(
                *[task[1] for task in tasks],
                return_exceptions=True
            )
            
            # Agregar resultados
            aggregated: Dict[str, Any] = {
                "animal_id": animal_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success"
            }
            
            for (field_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.warning(f"Erro ao buscar {field_name}: {str(result)}")
                    aggregated[field_name] = None
                else:
                    aggregated[field_name] = result
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Erro em aggregation.get_animal_dashboard: {str(e)}")
            raise
    
    async def get_animals_dashboard(
        self,
        animal_ids: List[int],
        max_ids: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obter dashboards de múltiplos animais
        
        Args:
            animal_ids: Lista de IDs de animais
            max_ids: Limite máximo de animais (padrão 100)
        
        Returns:
            Lista com dashboards agregados
        """
        # Limitar quantidade de animais
        if len(animal_ids) > max_ids:
            logger.warning(
                f"Limitando {len(animal_ids)} animais para {max_ids}"
            )
            animal_ids = animal_ids[:max_ids]
        
        # Buscar dashboards em paralelo
        tasks = [
            self.get_animal_dashboard(animal_id)
            for animal_id in animal_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar erros e retornar resultados
        return [
            result for result in results
            if not isinstance(result, Exception)
        ]
    
    async def _get_animal_data(self, animal_id: int) -> Dict[str, Any]:
        """Buscar dados do animal no animal-service"""
        return await self._call_service(
            "animal",
            f"/animais/{animal_id}"
        )
    
    async def _get_animal_weighings(
        self,
        animal_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Buscar pesagens do animal no pesagem-service"""
        params = {"animal_id": animal_id}
        
        if filters:
            if "start_date" in filters:
                params["start_date"] = filters["start_date"]
            if "end_date" in filters:
                params["end_date"] = filters["end_date"]
            if "measurement_type" in filters:
                params["type"] = filters["measurement_type"]
        
        return await self._call_service(
            "pesagem",
            f"/pesagens",
            params=params
        )
    
    async def _get_animal_quotes(
        self,
        animal_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Buscar cotações do animal no cotacao-service"""
        params = {"animal_id": animal_id}
        
        if filters:
            if "start_date" in filters:
                params["start_date"] = filters["start_date"]
            if "end_date" in filters:
                params["end_date"] = filters["end_date"]
        
        return await self._call_service(
            "cotacao",
            f"/cotacoes",
            params=params
        )
    
    async def _call_service(
        self,
        service_name: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Fazer chamada para um serviço backend
        
        Args:
            service_name: Nome do serviço (animal, pesagem, cotacao)
            endpoint: Endpoint a chamar (sem /)
            params: Query parameters
            method: HTTP method
            data: Request body
        
        Returns:
            Response JSON do serviço
        """
        try:
            url = f"{self.base_urls[service_name]}{endpoint}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, params=params)
                elif method == "POST":
                    response = await client.post(url, json=data, params=params)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.ConnectError as e:
            logger.error(f"Erro de conexão com {service_name}: {str(e)}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"Timeout ao chamar {service_name}: {str(e)}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Erro HTTP {e.response.status_code} em {service_name}: {str(e)}"
            )
            return None
        except Exception as e:
            logger.error(f"Erro ao chamar {service_name}: {str(e)}")
            return None
    
    def cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        """Obter valor do cache"""
        return self._cache.get(key)
    
    def cache_set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: int = 60
    ) -> None:
        """
        Armazenar valor em cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: Tempo de vida em segundos (padrão 60s)
        """
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now(timezone.utc).timestamp() + ttl
        }
    
    def cache_clear(self) -> None:
        """Limpar cache"""
        self._cache.clear()
    
    def cache_is_valid(self, key: str) -> bool:
        """Verificar se cache é válido (não expirou)"""
        if key not in self._cache:
            return False
        
        cache_entry = self._cache[key]
        if datetime.now(timezone.utc).timestamp() > cache_entry["expires_at"]:
            del self._cache[key]
            return False
        
        return True
    
    def get_cache_size(self) -> int:
        """Obter quantidade de entradas no cache"""
        return len(self._cache)


# Instância global
aggregation_service = AggregationService()
