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

**Pseudocódigo**:
```python
función tsp_fuerza_bruta(matriz_distancias, inicio):
    ciudades = {todas excepto inicio}
    mejor_distancia = ∞
    mejor_ruta = None
    
    para cada permutación P de ciudades:
        ruta = [inicio] + P + [inicio]
        distancia = sumar_distancias(ruta, matriz)
        
        si distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_ruta = ruta
    
    retornar mejor_ruta, mejor_distancia
```

**Ventajas**: Solución óptima garantizada  
**Desventajas**: Intratable para n > 15 (15! = 1.3 billones)

---

### 2. Held-Karp (`tsp_held_karp.py`)

**Tipo**: Exacto (programación dinámica)  
**Complejidad**: O(n² · 2ⁿ)  
**Uso**: 11-18 puntos

**Pseudocódigo**:
```python
función held_karp(matriz_distancias):
    n = número de ciudades
    memo = {}  # (ciudad, subconjunto) → distancia mínima
    
    # Caso base: un solo salto desde inicio
    para cada ciudad i ≠ inicio:
        memo[(i, {i})] = distancia[inicio][i]
    
    # Construir para subconjuntos crecientes
    para tamaño = 2 hasta n-1:
        para cada subconjunto S de tamaño dado:
            para cada ciudad k en S:
                S_sin_k = S \ {k}
                memo[(k, S)] = mín{
                    memo[(j, S_sin_k)] + distancia[j][k]
                    para toda j en S_sin_k
                }
    
    # Cerrar ciclo al inicio
    todas = {todas las ciudades}
    distancia_final = mín{
        memo[(k, todas\{k})] + distancia[k][inicio]
        para toda k
    }
    
    retornar reconstruir_camino(memo), distancia_final
```

**Ventajas**: Óptimo y más rápido que fuerza bruta  
**Desventajas**: Requiere O(n·2ⁿ) memoria

---

### 3. 2-Opt (`tsp_vecino_2opt.py`)

**Tipo**: Heurístico (aproximación)  
**Complejidad**: O(n²) por iteración  
**Uso**: Cualquier tamaño (escalable)

**Pseudocódigo**:
```python
función tsp_2opt(matriz_distancias):
    # Fase 1: Construcción greedy
    ruta = vecino_mas_cercano(matriz)
    
    # Fase 2: Mejora local
    mejorado = True
    mientras mejorado:
        mejorado = False
        para i = 1 hasta n-2:
            para j = i+1 hasta n-1:
                # Invertir segmento [i..j]
                nueva_ruta = ruta[0:i] + invertir(ruta[i:j+1]) + ruta[j+1:n]
                
                si calcular_distancia(nueva_ruta) < calcular_distancia(ruta):
                    ruta = nueva_ruta
                    mejorado = True
    
    retornar ruta

función vecino_mas_cercano(matriz):
    ruta = [inicio]
    no_visitados = {todas} \ {inicio}
    actual = inicio
    
    mientras no_visitados:
        siguiente = mín{distancia[actual][c] para c en no_visitados}
        ruta.append(siguiente)
        no_visitados.remove(siguiente)
        actual = siguiente
    
    ruta.append(inicio)  # Cerrar ciclo
    retornar ruta
```

**Ventajas**: Rápido, escalable, buena aproximación (5-15% sobre óptimo)  
**Desventajas**: No garantiza solución óptima

---

## 📁 Estructura del Proyecto

```
ADAProjectBogotech/
│
├── INICIAR_SISTEMA.bat          # ⭐ Iniciar todo el sistema
├── README.md                     # Este archivo
├── PRUEBAS_COMPLETAS.md         # Guía de pruebas detallada
│
├── tsp-red-vial/
│   ├── backend/                  # Servidor Python
│   │   ├── servidor.py           # ⭐ Punto de entrada backend
│   │   ├── configuracion.py      # Configuración
│   │   ├── requerimientos.txt    # Dependencias Python
│   │   ├── reiniciar_servidor.bat# Iniciar backend
│   │   │
│   │   ├── dominio/              # Lógica de negocio
│   │   │   ├── modelos.py        # Modelos Pydantic
│   │   │   ├── cargador_red.py   # GeoJSON → NetworkX
│   │   │   ├── ajustar_puntos.py # Integración geométrica
│   │   │   ├── rutas_mas_cortas.py# Dijkstra + matriz
│   │   │   ├── tsp_fuerza_bruta.py# Algoritmo 1
│   │   │   ├── tsp_held_karp.py  # Algoritmo 2
│   │   │   ├── tsp_vecino_2opt.py# Algoritmo 3
│   │   │   └── exportar_geo.py   # GeoJSON/WKT
│   │   │
│   │   └── pruebas/              # Tests unitarios
│   │       ├── test_ajustar_puntos.py
│   │       ├── test_rutas_mas_cortas.py
│   │       └── test_tsp.py
│   │
│   ├── frontend/                 # Cliente web
│   │   ├── index.html            # ⭐ Página principal
│   │   ├── iniciar_frontend.bat  # Iniciar frontend
│   │   ├── .env                  # Config API URL
│   │   └── src/
│   │       ├── principal.ts      # Controlador principal
│   │       ├── api_cliente.ts    # Cliente HTTP
│   │       ├── mapa.ts           # Gestión Leaflet
│   │       ├── tipos.ts          # Tipos TypeScript
│   │       └── estilos.css       # Estilos
│   │
│   └── datos/                    # Datasets
│       ├── bogota_completa.geojson  # Red completa (~145k nodos)
│       ├── puntos_ejemplo.csv       # 5 puntos (rápido)
│       ├── puntos_10.csv            # ⭐ 10 puntos (recomendado)
│       └── puntos_15.csv            # 15 puntos (desafío)
│
└── scripts/                      # Utilidades
    ├── descargar_red_bogota.py   # Descarga de OSM
    ├── generar_datos_sinteticos.py
    └── medir_tiempos.py          # Benchmarking
```

---

## 🔄 Flujo de Funcionamiento

### 1. Carga de Red Vial
```
Usuario → GeoJSON → POST /api/cargar-red
                ↓
        cargador_red.py procesa
                ↓
    Extrae LineStrings → Nodos + Aristas
                ↓
    Construye grafo NetworkX (peso = longitud)
                ↓
    Guarda en caché (hash del archivo)
                ↓
    Retorna: num_nodos, num_aristas, bbox
                ↓
        Frontend visualiza red
```

### 2. Carga e Integración de Puntos
```
Usuario → CSV → POST /api/cargar-puntos
                ↓
    Para cada punto (lat, lon):
                ↓
    ajustar_puntos.py:
    1. Buscar arista más cercana (perpendicular)
    2. Calcular proyección en arista
    3. Insertar nuevo nodo
    4. Dividir arista en dos
                ↓
    Puntos ahora son nodos del grafo
                ↓
    Frontend visualiza puntos integrados
```

### 3. Cálculo de Matriz de Distancias
```
Antes de ejecutar TSP:
                ↓
    rutas_mas_cortas.py:
                ↓
    Para cada par (i, j):
        Dijkstra(i → j)
        matriz[i][j] = distancia_camino
                ↓
    Resultado: Matriz NxN con distancias reales
```

### 4. Ejecución de Algoritmos
```
Usuario → "Evaluar" → POST /api/evaluar-algoritmos
                ↓
    Para cada algoritmo seleccionado:
                ↓
        Cronómetro.inicio()
        ruta = algoritmo(matriz_distancias)
        tiempo = Cronómetro.fin()
        distancia = calcular_total(ruta)
                ↓
    Retorna ComparacionAlgoritmos:
    - Fuerza Bruta: {ruta, distancia, tiempo}
    - Held-Karp: {ruta, distancia, tiempo}
    - 2-Opt: {ruta, distancia, tiempo}
                ↓
    Frontend visualiza 3 rutas en colores
```

### 5. Exportación
```
Usuario → "Descargar" → GET /api/exportar
                ↓
    exportar_geo.py genera GeoJSON:
    - Red vial (LineString)
    - Puntos (Point)
    - Ruta Fuerza Bruta (verde)
    - Ruta Held-Karp (azul)
    - Ruta 2-Opt (naranja)
                ↓
    Descarga: resultados_tsp_YYYYMMDD_HHMMSS.geojson
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Inicio Automático ⭐ RECOMENDADO

**Doble clic en**: `INICIAR_SISTEMA.bat`

Esto:
1. Inicia backend en http://localhost:8000
2. Inicia frontend en http://localhost:5173
3. Abre el navegador automáticamente

---

### Opción 2: Inicio Manual

#### Backend (Terminal 1)
```cmd
cd "C:\Users\mesas\PycharmProjects\algoritmos proyecto\ADAProjectBogotech\tsp-red-vial\backend"
venv\Scripts\activate.bat
python servidor.py
```

Verificar en: http://localhost:8000/docs (Swagger UI)

#### Frontend (Terminal 2)
```cmd
cd "C:\Users\mesas\PycharmProjects\algoritmos proyecto\ADAProjectBogotech\tsp-red-vial\frontend"
npm install
npm run dev
```

Abrir: http://localhost:5173

---

## 🌐 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/api/estado` | Estado del sistema |
| POST | `/api/cargar-red` | Cargar GeoJSON (red vial) |
| POST | `/api/cargar-puntos` | Cargar CSV (puntos) |
| POST | `/api/evaluar-algoritmos` | Ejecutar algoritmos TSP |
| GET | `/api/exportar` | Descargar resultados (GeoJSON) |

### Ejemplo: Evaluar Algoritmos

**Request**:
```json
POST /api/evaluar-algoritmos
{
  "algoritmos": ["fuerza_bruta", "held_karp", "2opt"],
  "nodo_inicio": 0
}
```

**Response**:
```json
{
  "fuerza_bruta": {
    "ruta": [0, 3, 1, 4, 2, 0],
    "distancia_total": 45234.56,
    "tiempo_ejecucion": 3.245
  },
  "held_karp": {
    "ruta": [0, 3, 1, 4, 2, 0],
    "distancia_total": 45234.56,
    "tiempo_ejecucion": 1.123
  },
  "2opt": {
    "ruta": [0, 2, 1, 3, 4, 0],
    "distancia_total": 47891.23,
    "tiempo_ejecucion": 0.234
  }
}
```

---

## 📊 Análisis de Complejidad

| Algoritmo | Tiempo | Espacio | Tipo | Puntos Recomendados |
|-----------|--------|---------|------|---------------------|
| **Fuerza Bruta** | O(n!) | O(n) | Exacto | ≤ 10 |
| **Held-Karp** | O(n²·2ⁿ) | O(n·2ⁿ) | Exacto | 11-18 |
| **2-Opt** | O(n²) | O(n) | Heurístico | Cualquiera |

### Comparación Práctica (10 puntos)

| Algoritmo | Tiempo | Distancia | Calidad |
|-----------|--------|-----------|---------|
| Fuerza Bruta | 3-5 seg | 45,234 m | 100% óptimo |
| Held-Karp | 1-2 seg | 45,234 m | 100% óptimo |
| 2-Opt | < 1 seg | 48,123 m | ~94% (aproximación) |

---

## 🧪 Testing

Ejecutar pruebas unitarias:

```cmd
cd backend
venv\Scripts\activate.bat
pytest -v
```

**Tests incluidos**:
- ✅ Integración de puntos a la red
- ✅ Cálculo de caminos mínimos (Dijkstra)
- ✅ Correctitud de algoritmos TSP
- ✅ Validación de modelos Pydantic
- ✅ Exportación GeoJSON/WKT

---

## 🐛 Solución de Problemas

### Error: Puerto 8000 en uso

```cmd
cd backend
reiniciar_servidor.bat
```

O manualmente:
```cmd
netstat -ano | findstr :8000
taskkill /F /PID <PID_encontrado>
```

Ver `SOLUCION_PUERTO_8000.md` para más detalles.

### Frontend muestra "Servidor desconectado"

1. Verificar backend en http://localhost:8000/docs
2. Revisar `frontend/.env`:
   ```
   VITE_API_URL=http://localhost:8000
   ```
3. Reiniciar ambos servidores

### Algoritmos muy lentos

Con 15 puntos:
- Fuerza Bruta: puede tomar **varios minutos** (15! = 1.3 billones)
- Usa **Held-Karp** o **2-Opt** para conjuntos grandes

**Recomendación**:
- ≤ 10 puntos: Todos los algoritmos
- 11-14 puntos: Held-Karp + 2-Opt
- ≥ 15 puntos: Solo 2-Opt

---

## 📚 Propósito de Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `servidor.py` | Punto de entrada, endpoints FastAPI, CORS |
| `modelos.py` | Clases Pydantic (Punto, RedVial, ResultadoTSP, etc.) |
| `cargador_red.py` | Parsea GeoJSON → NetworkX, sistema de caché |
| `ajustar_puntos.py` | Proyección geométrica, inserción de nodos |
| `rutas_mas_cortas.py` | Dijkstra, matriz de distancias NxN |
| `tsp_fuerza_bruta.py` | Todas las permutaciones, O(n!) |
| `tsp_held_karp.py` | Programación dinámica, O(n²·2ⁿ) |
| `tsp_vecino_2opt.py` | Greedy + mejora local, O(n²) |
| `exportar_geo.py` | Genera GeoJSON/WKT para GIS |
| `principal.ts` | Controlador frontend, eventos UI |
| `api_cliente.ts` | Cliente HTTP (fetch API) |
| `mapa.ts` | Gestión Leaflet, visualización de rutas |

---

## 📖 Documentación Adicional

- **`PRUEBAS_COMPLETAS.md`**: Guía paso a paso para probar el sistema
- **`INICIO_RAPIDO.md`**: Quick start guide
- **`RESUMEN_FINAL.md`**: Resumen ejecutivo
- **`SOLUCION_PUERTO_8000.md`**: Troubleshooting de puertos

---

## 📝 Referencias

- [Held-Karp Algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [2-opt Local Search (Wikipedia)](https://en.wikipedia.org/wiki/2-opt)
- [NetworkX Shortest Paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
- [GeoJSON Specification (RFC 7946)](https://datatracker.ietf.org/doc/html/rfc7946)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Leaflet Documentation](https://leafletjs.com/)

---

## ✅ Checklist de Funcionalidades

- [x] Carga de red vial GeoJSON
- [x] Integración automática de puntos
- [x] Cálculo de caminos mínimos (Dijkstra)
- [x] Algoritmo Fuerza Bruta (exacto)
- [x] Algoritmo Held-Karp (exacto)
- [x] Algoritmo 2-Opt (heurístico)
- [x] Visualización interactiva Leaflet
- [x] Exportación GeoJSON/WKT
- [x] Comparación de rendimiento
- [x] Sistema de caché optimizado
- [x] Suite de testing unitario
- [x] Documentación completa
- [x] Scripts de inicio automático

---

**Desarrollado para Análisis de Algoritmos**  
**Enero 2025**

