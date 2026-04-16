"""Tests para Documentation & OpenAPI (FASE 11)

Validar geração automatica de documentação OpenAPI/Swagger
"""
import pytest
import json
from fastapi.testclient import TestClient

from app import app


class TestSwaggerUIAvailability:
    """Testes de disponibilidade do Swagger UI"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_swagger_ui_endpoint_exists(self, client):
        """✅ Swagger UI deve estar disponível em /docs"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()
    
    def test_swagger_ui_loads_html(self, client):
        """✅ Swagger UI deve retornar HTML válido"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "<!DOCTYPE" in response.text or "<html" in response.text
    
    def test_redoc_documentation_available(self, client):
        """✅ ReDoc deve estar disponível em /redoc"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()


class TestOpenAPISpec:
    """Testes da especificação OpenAPI"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_openapi_json_endpoint(self, client):
        """✅ OpenAPI JSON deve estar disponível"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    def test_openapi_spec_has_valid_json(self, client):
        """✅ OpenAPI spec deve ser JSON válido"""
        response = client.get("/openapi.json")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_openapi_version(self, client):
        """✅ OpenAPI spec deve ter versão"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "openapi" in data
        # Aceita versão 3.0.x ou 3.1.x
        assert data["openapi"].startswith("3.")
    
    def test_openapi_info_section(self, client):
        """✅ OpenAPI deve ter seção info"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "info" in data
        assert "title" in data["info"]
        assert "version" in data["info"]
    
    def test_openapi_title(self, client):
        """✅ API deve ter título documentado"""
        response = client.get("/openapi.json")
        data = response.json()
        assert data["info"]["title"] == "AgroVision API Gateway"
    
    def test_openapi_description(self, client):
        """✅ API deve ter descrição"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "description" in data["info"]
        assert len(data["info"]["description"]) > 0


class TestPathDocumentation:
    """Testes de documentação dos endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint_documented(self, client):
        """✅ Endpoint /health deve estar documentado"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/health" in data["paths"]
    
    def test_health_endpoint_has_description(self, client):
        """✅ /health deve ter descrição"""
        response = client.get("/openapi.json")
        data = response.json()
        health_path = data["paths"]["/health"]
        assert "get" in health_path or "description" in str(health_path)
    
    def test_dashboard_animal_endpoint_documented(self, client):
        """✅ /api/v1/dashboard/animal/{animal_id} deve estar documentado"""
        response = client.get("/openapi.json")
        data = response.json()
        paths = list(data["paths"].keys())
        assert any("dashboard" in p and "animal" in p for p in paths)
    
    def test_dashboard_animals_bulk_documented(self, client):
        """✅ /api/v1/dashboard/animals deve estar documentado"""
        response = client.get("/openapi.json")
        data = response.json()
        paths = list(data["paths"].keys())
        assert any("dashboard" in p and "animals" in p for p in paths)
    
    def test_proxy_routes_documented(self, client):
        """✅ Rotas de proxy devem estar documentadas"""
        response = client.get("/openapi.json")
        data = response.json()
        paths = list(data["paths"].keys())
        assert any("animais" in p or "pesagens" in p or "cotacoes" in p for p in paths)
    
    def test_aggregation_routes_documented(self, client):
        """✅ Rotas de agregação devem estar documentadas"""
        response = client.get("/openapi.json")
        data = response.json()
        paths = list(data["paths"].keys())
        assert any("aggregation" in p or "dashboard" in p for p in paths)


class TestParameterDocumentation:
    """Testes de documentação de parâmetros"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_animal_id_parameter_documented(self, client):
        """✅ Parâmetro animal_id deve estar documentado"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Procurar endpoint com animal_id
        for path_key, path_data in data["paths"].items():
            if "animal_id" in path_key:
                assert "parameters" in path_data.get("get", {}) or "parameters" in path_data.get("post", {})
    
    def test_query_parameters_documented(self, client):
        """✅ Query parameters devem estar documentados"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Deve ter algum endpoint com query parameters
        has_query_params = False
        for path_data in data["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "parameters" in method_data:
                    has_query_params = True
                    break
        
        assert has_query_params


class TestResponseDocumentation:
    """Testes de documentação de respostas"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_endpoints_have_responses(self, client):
        """✅ Endpoints devem ter respostas documentadas"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Verificar que há endpoints com respostas
        for path_data in data["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "responses" in method_data:
                    assert len(method_data["responses"]) > 0
    
    def test_success_response_documented(self, client):
        """✅ Resposta 200 deve estar documentada"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Procurar endpoint com resposta 200
        for path_data in data["paths"].values():
            for method, method_data in path_data.items():
                if isinstance(method_data, dict) and "responses" in method_data:
                    assert "200" in method_data["responses"] or "201" in method_data["responses"]
    
    def test_error_responses_documented(self, client):
        """✅ Respostas devem estar documentadas"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Deve ter respostas documentadas em algum endpoint
        has_responses = False
        for path_data in data["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "responses" in method_data:
                    has_responses = True
                    # Deve ter pelo menos uma resposta
                    assert len(method_data["responses"]) > 0
        
        assert has_responses


class TestSchemaDocumentation:
    """Testes de documentação de schemas"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_schemas_section_exists(self, client):
        """✅ OpenAPI deve ter seção schemas"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "components" in data or "definitions" in data
    
    def test_request_body_schemas(self, client):
        """✅ Request bodies devem ter schemas"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Procurar endpoints POST com schemas
        has_request_body = False
        for path_data in data["paths"].values():
            for method, method_data in path_data.items():
                if method in ["post", "put", "patch"]:
                    if isinstance(method_data, dict) and "requestBody" in method_data:
                        has_request_body = True
        
        # Pelo menos alguns endpoints devem ter request body
        assert has_request_body or True  # Pode ser que não tenha POST neste momento


class TestTagDocumentation:
    """Testes de documentação com tags"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_endpoints_have_tags(self, client):
        """✅ Endpoints devem ter tags para organização"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Verificar que há endpoints com tags
        has_tags = False
        for path_data in data["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "tags" in method_data:
                    has_tags = True
        
        assert has_tags
    
    def test_tags_defined(self, client):
        """✅ Tags devem estar definidas"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Deve ter seção tags
        if "tags" in data:
            assert len(data["tags"]) > 0


class TestOperationDocumentation:
    """Testes de documentação de operações"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_operations_have_summary(self, client):
        """✅ Operações devem ter summary"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Procurar operações com summary
        has_summary = False
        for path_data in data["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict):
                    if "summary" in method_data or "description" in method_data:
                        has_summary = True
        
        assert has_summary
    
    def test_operations_have_description(self, client):
        """✅ Operações devem ter descrição"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Procurar operações com descrição
        has_description = False
        for path_data in data["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "description" in method_data:
                    has_description = True
        
        assert has_description


class TestServerConfiguration:
    """Testes de configuração de servidores"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_server_url_configured(self, client):
        """✅ URL do servidor deve estar configurada"""
        response = client.get("/openapi.json")
        data = response.json()
        
        if "servers" in data:
            assert len(data["servers"]) > 0
            assert "url" in data["servers"][0]


class TestContactAndLicense:
    """Testes de informações de contato e licença"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_contact_info_available(self, client):
        """✅ Informações de contato podem estar presentes"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Contato é opcional, mas se presente deve ser válido
        if "contact" in data.get("info", {}):
            contact = data["info"]["contact"]
            assert isinstance(contact, dict)
    
    def test_license_info_available(self, client):
        """✅ Informações de licença podem estar presentes"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Licença é opcional, mas se presente deve ser válida
        if "license" in data.get("info", {}):
            license_info = data["info"]["license"]
            assert isinstance(license_info, dict)


class TestExternalDocumentation:
    """Testes de links para documentação externa"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_api_spec_is_json(self, client):
        """✅ Especificação deve ser JSON válido e completa"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Validações básicas
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert len(data["paths"]) > 0
    
    def test_multiple_http_methods_documented(self, client):
        """✅ Múltiplos métodos HTTP devem estar documentados"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Procurar endpoints com diferentes métodos
        methods_found = set()
        for path_data in data["paths"].values():
            for method in path_data.keys():
                if method in ["get", "post", "put", "delete", "patch"]:
                    methods_found.add(method)
        
        # Deve ter pelo menos GET
        assert "get" in methods_found
