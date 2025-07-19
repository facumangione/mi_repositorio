# Autor
Facundo Jesús Mangione — Facultad de Ingeniería en Informática — Universidad de Mendoza

## Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local

## Objetivo

Este sistema simula un entorno concurrente y distribuido para monitorear señales biométricas como frecuencia cardíaca, presión arterial y saturación de oxígeno. Los datos son analizados en paralelo y almacenados de forma segura en una cadena de bloques local (`blockchain.json`) para garantizar **integridad, trazabilidad y resistencia a manipulaciones**.

---

## Componentes del Sistema

### `sistema_biometrico.py`

Archivo principal que implementa los siguientes módulos:

#### 🔸 Generador
- Simula 60 muestras (por defecto: 5) de datos por segundo.
- Cada muestra contiene: `timestamp`, `frecuencia`, `presion`, `oxigeno`.
- Envía los datos mediante `Pipe` a los analizadores.
- Finaliza la transmisión con un mensaje `"FIN"` a cada canal.

#### 🔸 Analizadores (3 procesos concurrentes)
- Reciben muestras por `Pipe`.
- Extraen el dato correspondiente (frecuencia, presión, oxígeno).
- Mantienen una **ventana móvil de 30 muestras** con `collections.deque`.
- Calculan:
  - **Media**
  - **Desviación estándar (si hay al menos 2 valores)**
- Devuelven los resultados mediante `Queue` al proceso verificador.

#### 🔸 Verificador
- Recolecta datos analizados de los 3 `Queue`.
- Verifica si los valores están dentro de parámetros normales.
- Crea un **bloque** con:
  - `timestamp`
  - resultados (media y desviación estándar)
  - flag de alerta
  - `prev_hash` y `hash` del bloque actual.
- Guarda cada bloque en `blockchain.json`.
- Imprime resumen con hash y estado de alerta.

---

### `verificar_cadena.py`

- Verifica la integridad de la cadena de bloques leyendo `blockchain.json`.
- Comprueba si:
  - Todos los hashes encadenan correctamente.
  - Se detectan alertas.
- Genera `reporte.txt` con:
  - Total de bloques.
  - Cantidad de alertas.
  - Bloques corruptos (si los hubiera).
  - Promedios globales de cada parámetro.

---

## Requisitos Técnicos

- Python 
- Solo librerías estándar:
  - `multiprocessing`
  - `hashlib`
  - `queue`
  - `json`
  - `collections`
  - `datetime`
  - `statistics`
  - `os`

---

## Ejecución

### 1. Ejecutar el sistema principal:

```bash
python sistema_biometrico.py
