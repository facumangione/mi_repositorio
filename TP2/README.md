# TP2 - Sistema de Scraping y Análisis Web Distribuido

## Descripción
Sistema distribuido de scraping web con dos servidores:
- **Servidor A (Asyncio)**: Maneja scraping asíncrono de páginas web
- **Servidor B (Multiprocessing)**: Procesa tareas CPU-bound en paralelo

## Instalación

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Servidor de Procesamiento (Parte B)
```bash
python server_processing.py -i localhost -p 8001 -n 4
```

### Servidor de Scraping (Parte A)
```bash
python server_scraping.py -i localhost -p 8000 --processing-host localhost --processing-port 8001
```

### Cliente de Prueba
```bash
python client.py http://localhost:8000/scrape?url=https://example.com
```

## Estructura del Proyecto

```
TP2/
├── common/              # Protocolo y utilidades compartidas
├── scraper/             # Módulos de scraping
├── processor/           # Workers de procesamiento
├── api/                 # Handlers HTTP
├── tests/               # Tests unitarios e integración
├── server_scraping.py   # Servidor asyncio (Parte A)
├── server_processing.py # Servidor multiprocessing (Parte B)
└── client.py            # Cliente de prueba
```

## Progreso de Implementación

- [x] Fase 1: Fundamentos de Networking
- [ ] Fase 2: Servidor de Procesamiento
- [ ] Fase 3: Scraping Asíncrono
- [ ] Fase 4: Servidor Asyncio
- [ ] Fase 5: Integración y Transparencia
- [ ] Fase 6: Bonus Track

## Autor
[Mangione Facundo]

## Fecha de Entrega
14/11/2025
