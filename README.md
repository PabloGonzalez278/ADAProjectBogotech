# Sistema de Optimización de Rutas TSP - Red Vial de Bogotá

**Proyecto Final - Análisis de Algoritmos**

Sistema web que resuelve el **Problema del Viajante (TSP)** sobre redes viales reales, optimizando rutas de visita a múltiples ubicaciones minimizando tiempo y distancia.

---

## 🎯 Descripción

Aplicación completa que permite:
- ✅ Cargar redes viales reales (GeoJSON) con +145k nodos
- ✅ Integrar automáticamente puntos de interés a las calles
- ✅ Calcular distancias reales usando caminos mínimos (Dijkstra)
- ✅ Resolver TSP con **3 algoritmos** (exactos y heurísticos)
- ✅ Visualizar resultados en mapa interactivo (Leaflet)
- ✅ Exportar rutas en GeoJSON para análisis GIS

---

## 🏗️ Arquitectura

```
┌────────────────────────────────────────────┐
│  FRONTEND (Vite + TypeScript + Leaflet)     │
│  • Interfaz visual interactiva              │
│  • Mapa Leaflet                             │
│  • Cliente API REST                         │
└──────────────┬─────────────────────────────┘
               │ HTTP/REST (JSON)
┌──────────────▼─────────────────────────────┐
│  BACKEND (FastAPI + Python)                 │
│  ┌──────────────────────────────────────┐  │
│  │ API REST (servidor.py)               │  │
│  │ • /api/cargar-red                    │  │
│  │ • /api/cargar-puntos                 │  │
│  │ • /api/evaluar-algoritmos            │  │
│  │ • /api/exportar                      │  │
│  │ • /api/estado                        │  │
│  └──────────┬───────────────────────────┘  │
│             │                               │
│  ┌──────────▼───────────────────────────┐  │
│  │ CAPA DE DOMINIO                      │  │
│  │                                      │  │
│  │ • modelos.py         (Pydantic)      │  │
│  │ • cargador_red.py    (GeoJSON→Grafo) │  │
│  │ • ajustar_puntos.py  (Integración)   │  │
│  │ • rutas_mas_cortas.py(Dijkstra)      │  │
│  │ • tsp_fuerza_bruta.py (O(n!))        │  │
│  │ • tsp_held_karp.py   (O(n²·2ⁿ))     │  │
│  │ • tsp_vecino_2opt.py (O(n²))         │  │
│  │ • exportar_geo.py    (GeoJSON/WKT)   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 🔧 Tecnologías

### Backend
- **Python 3.13** + **FastAPI 0.104** + **Uvicorn**
- **NetworkX** (grafos y Dijkstra)
- **Shapely** (geometría computacional)
- **Pydantic** (validación de datos)
- **Pytest** (testing unitario)

### Frontend
- **Vite 5** + **TypeScript 5**
- **Leaflet** (mapas interactivos)

### Datos
- **GeoJSON** (red vial de Bogotá ~145k nodos)
- **CSV** (puntos: id, latitud, longitud)

---

## 🧮 Algoritmos Implementados

### 1. Fuerza Bruta (`tsp_fuerza_bruta.py`)
**Tipo**: Exacto (solución óptima garantizada)
**Complejidad**: O(n!)
**Uso**: ≤ 10 puntos

### 2. Held-Karp (`tsp_held_karp.py`)
**Tipo**: Exacto (programación dinámica)
**Complejidad**: O(n² · 2ⁿ)
**Uso**: 11-18 puntos

### 3. 2-Opt (`tsp_vecino_2opt.py`)
**Tipo**: Heurístico (aproximación)
**Complejidad**: O(n²) por iteración
**Uso**: Cualquier tamaño (escalable)

---

## ✅ Óptimo vs. No Óptimo: ¿Qué significa?

En el contexto del Problema del Viajante (TSP), una solución se considera **óptima** si es la mejor posible, es decir, no existe ninguna otra ruta que tenga una distancia total menor.

### Algoritmos Exactos (Solución Óptima)
-   **Fuerza Bruta** y **Held-Karp** son algoritmos **exactos**. Esto significa que **garantizan** encontrar la ruta óptima.
-   **¿Por qué no usarlos siempre?** Porque su coste computacional es muy alto. Fuerza Bruta se vuelve inviable muy rápidamente (más de 10-11 puntos), y Held-Karp, aunque mucho mejor, también tiene un límite práctico (alrededor de 20 puntos).

### Algoritmos Heurísticos (Solución Aproximada)
-   **2-Opt** es un algoritmo **heurístico**. Esto significa que busca una "buena" solución en un tiempo razonable, pero **no garantiza** que sea la mejor posible.
-   La solución que encuentra puede ser muy cercana a la óptima (a menudo con una diferencia del 5-15%), pero no hay forma de saberlo con certeza sin compararla con la solución de un algoritmo exacto.
-   **¿Por qué usarlos?** Porque son muy rápidos y escalables, lo que los hace ideales para problemas con un gran número de puntos donde los algoritmos exactos tardarían demasiado tiempo.

---

## 🚀 Cómo Ejecutar

### Opción 1: Inicio Automático (Recomendado)

#### En Windows
Doble clic en el archivo: `INICIAR_SISTEMA.bat`

#### En Linux / macOS
Abre una terminal y ejecuta:
```bash
# Primero, da permisos de ejecución al script (solo la primera vez)
chmod +x INICIAR_SISTEMA.sh

# Luego, ejecútalo
./INICIAR_SISTEMA.sh
```
Esto abrirá dos nuevas ventanas de terminal, una para el backend y otra para el frontend, y configurará todo automáticamente.

---

### Opción 2: Inicio Manual

#### Backend (Terminal 1)

**En Windows:**
```cmd
# Navega al directorio del backend
cd tsp-red-vial\backend

# Activa el entorno virtual
venv\Scripts\activate.bat

# Instala las dependencias (si es la primera vez)
pip install -r requerimientos.txt

# Inicia el servidor
python servidor.py
```

**En Linux / macOS:**
```bash
# Navega al directorio del backend
cd tsp-red-vial/backend

# Crea y activa el entorno virtual (si no existe)
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Instala las dependencias (si es la primera vez)
pip install -r requerimientos.txt

# Inicia el servidor
python3 servidor.py
```
Verifica que el backend esté funcionando abriendo [http://localhost:8000/docs](http://localhost:8000/docs) en tu navegador.

#### Frontend (Terminal 2)

**En Windows, Linux y macOS (los comandos son los mismos):**
```bash
# Navega al directorio del frontend
cd tsp-red-vial/frontend

# Instala las dependencias (si es la primera vez)
npm install

# Inicia el servidor de desarrollo
npm run dev
```
Abre [http://localhost:5173](http://localhost:5173) en tu navegador.

---

## 🧪 Testing

Para ejecutar las pruebas unitarias, navega al directorio del backend y usa los siguientes comandos:

**En Windows:**
```cmd
cd tsp-red-vial\backend
venv\Scripts\activate.bat
pytest -v
```

**En Linux / macOS:**
```bash
cd tsp-red-vial/backend
source venv/bin/activate
pytest -v
```

**Tests incluidos**:
- ✅ Integración de puntos a la red
- ✅ Cálculo de caminos mínimos (Dijkstra)
- ✅ Correctitud de algoritmos TSP
- ✅ Validación de modelos Pydantic

---
## 🐛 Solución de Problemas

### Error: Puerto 8000 en uso (Windows)
```cmd
cd tsp-red-vial\backend
reiniciar_servidor.bat
```

### Frontend muestra "Servidor desconectado"
1.  Verificar que el backend esté corriendo en [http://localhost:8000/docs](http://localhost:8000/docs).
2.  Revisar que el archivo `frontend/.env` contenga `VITE_API_URL=http://localhost:8000`.
3.  Reiniciar ambos servidores.

### Algoritmos muy lentos
-   Con 15 puntos, **Fuerza Bruta** puede tomar varios minutos.
-   **Recomendación**: Usa **Held-Karp** para hasta 18-20 puntos y **2-Opt** para cualquier cantidad.

---

**Desarrollado para Análisis de Algoritmos**
**noviembre 2025**
