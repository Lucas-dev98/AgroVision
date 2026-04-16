# 🔌 Integrações Externas

## 🔌 Balança (Serial)

### Arquitetura

```
Balança Eletrônica
    ↓ (Serial RS-232)
Raspberry Pi / Industrial PC
    ↓ (pyserial)
ingestion-service
    ↓ (HTTP POST)
pesagem-service
    ↓ (SQL INSERT)
PostgreSQL
```

### Implementação com pyserial

```python
import serial
import json

class BalancaReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
    
    def read_weight(self) -> float:
        """Lê peso em kg da balança"""
        try:
            # Formato esperado: "000450\r\n" (450 kg)
            data = self.ser.readline().decode().strip()
            return float(data) / 1000  # Converte para kg
        except Exception as e:
            print(f"Erro ao ler balança: {e}")
            return None
    
    def close(self):
        self.ser.close()

# Uso
balanca = BalancaReader()
while True:
    peso = balanca.read_weight()
    if peso:
        print(f"Peso lido: {peso} kg")
```

### Eventos

```json
{
  "tipo": "pesagem",
  "animal_id": 10,
  "rfid": "BOI_001",
  "peso_kg": 450.5,
  "timestamp": "2026-04-15T10:30:00Z"
}
```

---

## 📸 Câmera IP (RTSP + YOLO)

### Arquitetura

```
Câmera IP (RTSP)
    ↓ (streaming)
vision-service
    ↓ (YOLO v8)
Detecções (JSON)
    ↓ (HTTP POST)
alimentacao-service
    ↓ (SQL INSERT)
PostgreSQL
```

### Implementação com OpenCV + YOLO

```python
import cv2
from ultralytics import YOLO

class VisionService:
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.model = YOLO("yolov8n.pt")  # Nano model
        self.cap = None
    
    def connect(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise Exception("Falha ao conectar na câmera")
    
    def detect_animals(self) -> dict:
        """Detecta vacas no frame"""
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        results = self.model(frame)
        detections = []
        
        for result in results:
            for box in result.boxes:
                if result.names[int(box.cls)] == 'cow':
                    detections.append({
                        'x': float(box.xywh[0][0]),
                        'y': float(box.xywh[0][1]),
                        'w': float(box.xywh[0][2]),
                        'h': float(box.xywh[0][3]),
                        'confidence': float(box.conf[0])
                    })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "detections": detections,
            "num_cows": len(detections)
        }
    
    def close(self):
        self.cap.release()

# Uso
vision = VisionService("rtsp://192.168.1.100:554/stream")
vision.connect()
result = vision.detect_animals()
print(result)
```

### Eventos

```json
{
  "tipo": "visao",
  "camera_id": "CAM_COCHO_01",
  "timestamp": "2026-04-15T10:30:00Z",
  "detections": [
    {
      "animal_id": 10,
      "comportamento": "comendo",
      "confianca": 0.95
    },
    {
      "animal_id": 12,
      "comportamento": "bebendo",
      "confianca": 0.87
    }
  ]
}
```

---

## 💰 CEPEA (Cotação de Boi Gordo)

### Arquitetura

```
CEPEA (Web)
    ↓ (BeautifulSoup scraping)
cotacao-service
    ↓ (Agendado diariamente)
PostgreSQL (cotacao_arroba)
    ↓ (cálculo de valor)
pesagem-service / analytics-service
```

### Implementação com BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

class CEPEAScraper:
    def __init__(self):
        self.url = "https://www.cepea.esalq.usp.br/br/indicador/boi.aspx"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
    
    def get_price(self) -> dict:
        """Scrapa preço atual da arroba"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Adaptar seletor conforme HTML do CEPEA
            price_element = soup.find('span', {'class': 'preco'})
            
            if price_element:
                price_text = price_element.text.strip()
                price = float(price_text.replace('R$', '').replace(',', '.'))
                
                return {
                    "preco": price,
                    "data_referencia": date.today().isoformat(),
                    "fonte": "CEPEA",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Erro ao scrapear CEPEA: {e}")
        
        return None

# Uso
scraper = CEPEAScraper()
preco = scraper.get_price()
print(preco)
```

### Integração com Celery (Job Diário)

```python
from celery import shared_task
from celery.schedules import crontab

# tasks.py
@shared_task
def atualizar_cotacao_diaria():
    scraper = CEPEAScraper()
    preco_data = scraper.get_price()
    
    if preco_data:
        # Salvar no banco
        cotacao = CotacaoArroba(**preco_data)
        db.session.add(cotacao)
        db.session.commit()
        return f"Cotação atualizada: R$ {preco_data['preco']}"
    
    return "Falha ao atualizar cotação"

# Celery Beat config
app.conf.beat_schedule = {
    'atualizar-cotacao-diaria': {
        'task': 'app.tasks.atualizar_cotacao_diaria',
        'schedule': crontab(hour=17, minute=0),  # 17:00 (fechamento de pregão)
    },
}
```

---

## 🌐 RFID (Identificação de Animais)

### Arquitetura

```
Leitor RFID (Serial/USB)
    ↓
ingestion-service
    ↓ (lookup animal_id)
animal-service
    ↓
pesagem-service (atualiza referência)
```

### Implementação

```python
import serial

class RFIDReader:
    def __init__(self, port='/dev/ttyUSB1', baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
    
    def read_rfid(self) -> str:
        """Lê RFID da tag"""
        try:
            data = self.ser.readline().decode().strip()
            # Formato esperado: "BOI_001\r\n"
            return data
        except Exception as e:
            print(f"Erro ao ler RFID: {e}")
            return None
    
    def close(self):
        self.ser.close()

# Uso no ingestion-service
rfid_reader = RFIDReader()
rfid = rfid_reader.read_rfid()
if rfid:
    # Buscar animal por RFID
    animal = db.query(Animal).filter_by(rfid=rfid).first()
    if animal:
        print(f"Animal identificado: {animal.nome}")
```

---

## 📊 Webhooks Internos

Serviços se comunicam via HTTP:

```python
# Em pesagem-service
def registrar_pesagem(animal_id: int, peso: float):
    # Salvar pesagem
    pesagem = Pesagem(animal_id=animal_id, peso_kg=peso)
    db.add(pesagem)
    db.commit()
    
    # Notificar analytics-service
    requests.post(
        "http://analytics-service:8000/eventos/pesagem",
        json={
            "animal_id": animal_id,
            "peso_kg": peso,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # Notificar api-gateway
    requests.post(
        "http://api-gateway:8000/eventos/pesagem",
        json={"animal_id": animal_id}
    )
```

---

## ✅ Checklist de Integrações

- [ ] Balança (serial) testada com mock
- [ ] RFID integrado
- [ ] Câmera IP (RTSP) testada
- [ ] YOLO treinado para vacas
- [ ] CEPEA scraper funcional
- [ ] Celery/APScheduler configurado
- [ ] Webhooks internos testados
- [ ] Redis como cache
- [ ] Fila de eventos (futuro)
