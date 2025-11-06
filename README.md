# 🚀 Sistema de Optimización de Rutas - TSP en Redes Viales

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Problema a Resolver](#-problema-a-resolver)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Stack Tecnológico](#-stack-tecnológico)
- [Algoritmos Implementados](#-algoritmos-implementados)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Flujo de Funcionamiento](#-flujo-de-funcionamiento)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Casos de Uso](#-casos-de-uso)
- [Pruebas y Análisis](#-pruebas-y-análisis)

---

## 🎯 Descripción del Proyecto

Este proyecto implementa un **sistema web para optimizar rutas de visita** en una red vial real. El objetivo es determinar el **orden óptimo** para visitar un conjunto de ubicaciones, minimizando la distancia total recorrida sobre la red de calles (no en línea recta).

### Contexto
El gobierno local necesita un sistema que:
- Cargue una red vial (calles y intersecciones)
- Integre puntos de interés a esa red
- Calcule la mejor ruta para visitarlos todos
- Compare diferentes algoritmos para encontrar el más eficiente

---

## 🧩 Problema a Resolver

### El Problema del Viajante (TSP - Traveling Salesman Problem)

**Definición Clásica:**  
Dado un conjunto de ciudades y las distancias entre ellas, encuentra el recorrido más corto que visite cada ciudad exactamente una vez y regrese al punto de partida.

**Nuestra Variante:**  
En lugar de usar distancias en línea recta (euclidianas), calculamos distancias **reales sobre una red de calles**, usando el camino más corto entre cada par de puntos.

### ¿Por qué es difícil?

El TSP es un problema **NP-completo**, lo que significa que:
- No existe un algoritmo eficiente conocido para encontrar la solución óptima
- El número de rutas posibles crece factorialmente: **n!**
  - 5 ciudades = 120 rutas posibles
  - 10 ciudades = 3,628,800 rutas
  - 20 ciudades = 2.4 × 10¹⁸ rutas (imposible de evaluar todas)

Por eso necesitamos **diferentes estrategias algorítmicas** que balanceen calidad de solución vs tiempo de ejecución.

---

## 🏗️ Arquitectura del Sistema

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     USUARIO (Navegador)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Angular + TypeScript)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Mapa       │  │  Carga de    │  │  Análisis y  │      │
│  │  (Leaflet)   │  │  Archivos    │  │  Resultados  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Parser de   │  │  Gestor de   │  │  Algoritmos  │      │
│  │  Archivos    │  │   Grafos     │  │     TSP      │      │
│  │ (GeoJSON/WKT)│  │  (NetworkX)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Servicios de Geometría y Rutas           │       │
│  │  • Integración de puntos a la red                │       │
│  │  • Cálculo de caminos más cortos (Dijkstra)     │       │
│  │  • Generación de matriz de distancias           │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Principios de Diseño

1. **Separación Frontend/Backend**: Permite desarrollo independiente y escalabilidad
2. **API RESTful**: Comunicación estándar y bien documentada (Swagger automático)
3. **Arquitectura por Capas**: Separación clara de responsabilidades
4. **Modularidad**: Fácil agregar nuevos algoritmos sin afectar el resto del sistema

---

## 💻 Stack Tecnológico

### Frontend: Angular + TypeScript

#### ¿Por qué Angular?

✅ **Framework completo y estructurado**
- Arquitectura clara basada en componentes y servicios
- TypeScript nativo (tipado fuerte, menos errores)
- Perfecto para aplicaciones de mediana/gran escala

✅ **Ecosistema robusto**
- Angular Material: Componentes UI profesionales
- RxJS: Manejo potente de eventos asíncronos
- HttpClient: Comunicación HTTP integrada

✅ **Mantenibilidad**
- Código organizado y predecible
- Inyección de dependencias
- Herramientas de testing integradas

#### ¿Por qué Leaflet?

✅ **Biblioteca de mapas ligera y poderosa**
- Más simple que OpenLayers (curva de aprendizaje menor)
- Excelente documentación y comunidad
- Perfecto para visualización de datos geoespaciales
- Soporte nativo para GeoJSON

✅ **Características clave**
- Marcadores personalizables
- Capas y overlays
- Control de zoom y navegación
- Plugins para funcionalidades extra

**Alternativa considerada:** OpenLayers (más complejo, mayor funcionalidad que no necesitamos)

---

### Backend: Python + FastAPI

#### ¿Por qué Python?

✅ **Ideal para algoritmos y análisis de datos**
- Sintaxis clara y expresiva
- Excelentes bibliotecas científicas (NumPy, NetworkX)
- Fácil de leer y mantener

✅ **Ecosistema rico para grafos y geometría**
- NetworkX: Algoritmos de grafos listos para usar
- Shapely: Operaciones geométricas
- GeoPandas: Datos geoespaciales

#### ¿Por qué FastAPI?

✅ **Framework moderno y rápido**
- Alto rendimiento (comparable a Node.js)
- Documentación automática (Swagger/OpenAPI)
- Validación automática de datos con Pydantic
- Soporte async/await nativo

✅ **Developer Experience**
- Menos código boilerplate
- Autocompletado en IDEs gracias a tipos
- Fácil testing
- Despliegue simple

**Alternativas consideradas:** 
- Flask (más simple pero menos funcionalidades)
- Django (demasiado pesado para este proyecto)

---

### Bibliotecas Clave

#### NetworkX 

**¿Qué es?**  
Biblioteca de Python para crear, manipular y estudiar la estructura de redes complejas (grafos).

**¿Por qué la usamos?**
- ✅ Representa la red vial como un grafo (nodos = intersecciones, aristas = calles)
- ✅ Algoritmo de Dijkstra ya implementado y optimizado
- ✅ Funciones para análisis de grafos
- ✅ Visualización de grafos (útil para debugging)

**Ejemplo de uso:**
```python
import networkx as nx

# Crear grafo de la red vial
G = nx.Graph()
G.add_edge('A', 'B', weight=5.2)  # Calle de 5.2 km

# Camino más corto entre dos puntos
path = nx.shortest_path(G, 'A', 'Z', weight='weight')
distance = nx.shortest_path_length(G, 'A', 'Z', weight='weight')
```

#### Shapely - Geometría Computacional

**¿Para qué la usamos?**
- Calcular distancia perpendicular de un punto a una línea
- Encontrar la intersección donde un punto debe conectarse a una calle
- Operaciones geométricas en general

**Ejemplo:**
```python
from shapely.geometry import Point, LineString

# Calle (arista)
street = LineString([(0, 0), (10, 0)])

# Punto de interés
poi = Point(5, 3)

# Proyección perpendicular del punto sobre la calle
projection = street.interpolate(street.project(poi))
distance = poi.distance(street)
```

---

## 🧮 Algoritmos Implementados

### 1. Fuerza Bruta (Brute Force) - Caso Base

#### ¿Qué hace?
Genera **todas las permutaciones posibles** de visitar los puntos y elige la más corta.

#### ¿Cómo funciona?
```
Puntos: [A, B, C, D]

Evalúa TODAS las rutas:
- A → B → C → D → A
- A → B → D → C → A
- A → C → B → D → A
- A → C → D → B → A
- A → D → B → C → A
- A → D → C → B → A
... (24 rutas en total para 4 puntos)

Selecciona la de menor distancia total
```

#### Complejidad
- **Tiempo:** O(n!) - factorial
- **Espacio:** O(n)

#### Análisis Asintótico

| Puntos (n) | Permutaciones | Tiempo Aprox. |
|------------|---------------|---------------|
| 5          | 120           | < 1ms         |
| 10         | 3,628,800     | ~1s           |
| 12         | 479,001,600   | ~2 min        |
| 15         | 1.3 × 10¹²    | Días          |
| 20         | 2.4 × 10¹⁸    | Años          |

#### Ventajas
✅ Garantiza la **solución óptima**  
✅ Implementación simple

#### Desventajas
❌ Completamente **inviable** para más de ~12 puntos  
❌ Crece explosivamente

#### ¿Cuándo usarlo?
- Solo para validar otros algoritmos con casos pequeños (n ≤ 10)
- Establecer el "baseline" de comparación

---

### 2. Algoritmo Greedy (Vecino Más Cercano)

#### ¿Qué hace?
En cada paso, **elige el siguiente punto no visitado más cercano** al punto actual.

#### ¿Cómo funciona?
```
Puntos: [A, B, C, D, E]
Inicio: A

Paso 1: Desde A, ¿cuál es el más cercano? → B (3 km)
        Ruta: A → B

Paso 2: Desde B, ¿cuál es el más cercano no visitado? → D (2 km)
        Ruta: A → B → D

Paso 3: Desde D, ¿cuál es el más cercano no visitado? → C (4 km)
        Ruta: A → B → D → C

Paso 4: Desde C, solo queda E → E (5 km)
        Ruta: A → B → D → C → E

Paso 5: Regresar al inicio → A
        Ruta final: A → B → D → C → E → A
```

#### Pseudocódigo
```
función greedy_tsp(puntos, inicio):
    ruta = [inicio]
    actual = inicio
    no_visitados = puntos - {inicio}
    
    mientras no_visitados no esté vacío:
        más_cercano = encontrar_punto_más_cercano(actual, no_visitados)
        ruta.agregar(más_cercano)
        actual = más_cercano
        no_visitados.eliminar(más_cercano)
    
    ruta.agregar(inicio)  # Regresar al origen
    retornar ruta
```

#### Complejidad
- **Tiempo:** O(n²)
- **Espacio:** O(n)

**Desglose:**
- Para cada punto (n iteraciones)
- Buscamos el más cercano entre los restantes (hasta n comparaciones)
- Total: n × n = n²

#### Ventajas
✅ **Muy rápido** incluso con muchos puntos  
✅ **Fácil de implementar** y entender  
✅ Da soluciones **razonablemente buenas**  
✅ Escalable a cientos de puntos

#### Desventajas
❌ **No garantiza solución óptima**  
❌ Puede quedar "atrapado" en decisiones locales malas  
❌ La calidad depende del punto de inicio  
❌ Típicamente 15-25% peor que el óptimo

#### Ejemplo de Limitación
```
    A ---10--- B
    |          |
    1          1
    |          |
    C ---10--- D

Greedy desde A:
A → C (1) → D (10) → B (1) → A (10) = 22

Óptimo:
A → B (10) → D (1) → C (10) → A (1) = 22

En este caso da igual, pero considera:

    A ---1--- B
    |         |
   10         1
    |         |
    C --100-- D

Greedy desde A:
A → B (1) → D (1) → C (100) → A (10) = 112

Óptimo:
A → C (10) → D (100) → B (1) → A (1) = 112

Greedy puede fallar cuando la elección local óptima
lleva a una mala configuración global.
```

#### ¿Cuándo usarlo?
- Cuando necesitas una solución rápida
- Como **solución inicial** para otros algoritmos (como 2-Opt)
- Para datasets grandes donde fuerza bruta es imposible

---

### 3. Algoritmo 2-Opt (Optimización Local)

#### ¿Qué hace?
Toma una ruta inicial y la **mejora iterativamente** intercambiando pares de aristas que reducen la distancia total.

#### ¿Cómo funciona?

**Concepto Clave:** Eliminar cruces en la ruta

```
Ruta inicial (puede tener cruces):

A ----→ B
 \    ⨯
  \  /
   ⨯
  /  \
 ↙    ↘
C ----→ D

Distancia: AB + CD

Después de 2-opt (elimina el cruce):

A ----→ B
|       |
|       |
↓       ↓
C ----→ D

Distancia: AC + BD (generalmente menor)
```

#### Proceso Paso a Paso

```
Ruta inicial: A → B → C → D → E → A (de algoritmo Greedy)

Iteración 1:
- Prueba invertir segmento B-C: A → C → B → D → E → A
- ¿Es mejor? No → Mantener original

Iteración 2:
- Prueba invertir segmento B-D: A → D → C → B → E → A
- ¿Es mejor? Sí, distancia reduce de 50 a 45
- ACEPTAR cambio

Iteración 3:
- Prueba invertir segmento C-E: A → D → E → B → C → A
- ¿Es mejor? No → Mantener actual

... continúa hasta que no hay mejoras
```

#### Pseudocódigo
```
función 2opt(ruta):
    mejora = verdadero
    mejor_ruta = ruta
    
    mientras mejora:
        mejora = falso
        
        para i desde 0 hasta n-2:
            para j desde i+2 hasta n:
                nueva_ruta = ruta con segmento [i+1, j] invertido
                
                si distancia(nueva_ruta) < distancia(mejor_ruta):
                    mejor_ruta = nueva_ruta
                    mejora = verdadero
                    romper ciclos internos
    
    retornar mejor_ruta
```

#### Complejidad
- **Tiempo:** O(n² × k) donde k = número de iteraciones
  - En la práctica: O(n²) con k pequeño (típicamente 5-20)
- **Espacio:** O(n)

#### Ventajas
✅ **Mejora significativa** sobre soluciones greedy  
✅ **Implementación moderadamente simple**  
✅ Resultados típicamente **dentro de 2-5% del óptimo**  
✅ Funciona bien en práctica (datasets reales)

#### Desventajas
❌ Puede quedar atrapado en **óptimos locales**  
❌ No garantiza solución óptima global  
❌ El resultado depende de la ruta inicial  
❌ Más lento que greedy (pero mucho más rápido que fuerza bruta)

#### ¿Cuándo usarlo?
- Cuando necesitas **buena calidad** de solución
- Como algoritmo principal en producción
- Datasets de tamaño mediano a grande (hasta miles de puntos)

---

### Comparación de Algoritmos

| Algoritmo      | Tiempo      | Calidad    | Escalabilidad | Implementación |
|----------------|-------------|------------|---------------|----------------|
| Fuerza Bruta   | O(n!)       | ⭐⭐⭐⭐⭐ | ❌ n ≤ 12     | ⭐⭐⭐⭐⭐      |
| Greedy         | O(n²)       | ⭐⭐⭐      | ✅ n ≤ 1000+  | ⭐⭐⭐⭐⭐      |
| 2-Opt          | O(n² × k)   | ⭐⭐⭐⭐    | ✅ n ≤ 500    | ⭐⭐⭐⭐        |

**Leyenda:**
- ⭐⭐⭐⭐⭐ = Óptimo/Muy fácil
- ⭐⭐⭐⭐ = Excelente/Fácil
- ⭐⭐⭐ = Bueno/Medio

---

### Algoritmo de Caminos Más Cortos: Dijkstra

#### ¿Por qué lo necesitamos?

Para calcular el TSP sobre una red, primero necesitamos saber **la distancia real entre cada par de puntos** (no la distancia en línea recta).

#### ¿Qué hace Dijkstra?

Encuentra el **camino más corto** desde un nodo origen a todos los demás nodos en un grafo ponderado.

#### ¿Cómo funciona?

```
Red vial simplificada:
       2
   A ─── B
   │ \   │ 3
 1 │  5\ │
   │   \ │
   C ─── D
      4

Dijkstra desde A:
1. Inicio: distancia[A] = 0, resto = ∞
2. Visitar vecinos de A: B(2), C(1), D(5)
3. Siguiente más cercano: C(1)
4. Desde C, actualizar: D = min(5, 1+4) = 5
5. Siguiente más cercano: B(2)
6. Desde B, actualizar: D = min(5, 2+3) = 5
7. Terminar: Distancias finales = {A:0, B:2, C:1, D:5}

Camino A→D: A → C → D (distancia 5)
```

#### Complejidad
- **Tiempo:** O((V + E) log V) con heap binario
- **Espacio:** O(V)

donde V = nodos (intersecciones), E = aristas (calles)

#### Uso en nuestro proyecto

```python
# Matriz de distancias entre todos los puntos de interés
puntos = [P1, P2, P3, P4, P5]

matriz_distancias = []
para cada punto_i en puntos:
    fila = []
    para cada punto_j en puntos:
        distancia = dijkstra(grafo, punto_i, punto_j)
        fila.agregar(distancia)
    matriz_distancias.agregar(fila)

# Ahora usamos esta matriz para TSP
# Sin recalcular rutas constantemente
```

**Optimización:** Calculamos la matriz de distancias **una sola vez** al inicio, luego los algoritmos TSP solo consultan esta matriz.

---

## 📁 Estructura del Proyecto

```
ADAProjectBogotech/
│
├── README.md                           # Este archivo
├── .gitignore
│
├── frontend/                           # Aplicación Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/                  # Funcionalidad central
│   │   │   │   ├── services/          # Servicios singleton
│   │   │   │   │   ├── api.service.ts           # HTTP client
│   │   │   │   │   └── notification.service.ts  # Notificaciones
│   │   │   │   ├── guards/            # Guards de navegación
│   │   │   │   ├── interceptors/      # HTTP interceptors
│   │   │   │   └── models/            # Interfaces TypeScript
│   │   │   │       ├── network.model.ts         # Red vial
│   │   │   │       ├── point.model.ts           # Puntos de interés
│   │   │   │       └── route.model.ts           # Resultados
│   │   │   │
│   │   │   ├── shared/                # Componentes compartidos
│   │   │   │   ├── components/
│   │   │   │   │   ├── file-upload/
│   │   │   │   │   ├── loading-spinner/
│   │   │   │   │   └── metrics-card/
│   │   │   │   ├── pipes/             # Pipes personalizados
│   │   │   │   └── directives/        # Directivas
│   │   │   │
│   │   │   └── features/              # Módulos funcionales
│   │   │       ├── map/               # Visualización del mapa
│   │   │       │   ├── map.component.ts
│   │   │       │   ├── map.component.html
│   │   │       │   └── map.service.ts
│   │   │       │
│   │   │       ├── network-upload/    # Carga de red vial
│   │   │       │   └── network-upload.component.ts
│   │   │       │
│   │   │       ├── points-upload/     # Carga de puntos
│   │   │       │   └── points-upload.component.ts
│   │   │       │
│   │   │       └── analysis/          # Ejecución y resultados
│   │   │           ├── analysis.component.ts
│   │   │           ├── results-table/
│   │   │           └── route-comparison/
│   │   │
│   │   ├── assets/                    # Recursos estáticos
│   │   │   ├── icons/
│   │   │   └── styles/
│   │   │
│   │   ├── environments/              # Configuración por ambiente
│   │   │   ├── environment.ts
│   │   │   └── environment.prod.ts
│   │   │
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.scss
│   │
│   ├── angular.json                   # Configuración Angular
│   ├── package.json
│   ├── tsconfig.json
│   └── karma.conf.js                  # Testing config
│
├── backend/                            # API Python
│   ├── app/
│   │   ├── main.py                    # Punto de entrada FastAPI
│   │   │
│   │   ├── api/                       # Endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── network.py         # POST /network (cargar red)
│   │   │       ├── points.py          # POST /points (cargar puntos)
│   │   │       └── tsp.py             # POST /tsp/solve (ejecutar)
│   │   │
│   │   ├── core/                      # Configuración central
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Settings
│   │   │   └── exceptions.py          # Excepciones custom
│   │   │
│   │   ├── models/                    # Modelos Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── network.py             # NetworkRequest/Response
│   │   │   ├── point.py               # PointRequest/Response
│   │   │   └── tsp.py                 # TSPRequest/Response
│   │   │
│   │   ├── services/                  # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── graph_service.py       # Gestión del grafo NetworkX
│   │   │   │   # - Crear grafo desde GeoJSON
│   │   │   │   # - Integrar puntos a la red
│   │   │   │   # - Calcular matriz de distancias
│   │   │   │
│   │   │   ├── tsp_brute_force.py     # Algoritmo 1
│   │   │   ├── tsp_greedy.py          # Algoritmo 2
│   │   │   └── tsp_2opt.py            # Algoritmo 3
│   │   │
│   │   └── utils/                     # Utilidades
│   │       ├── __init__.py
│   │       ├── file_parser.py         # Parse GeoJSON/WKT
│   │       ├── geometry.py            # Cálculos geométricos
│   │       └── export.py              # Exportar resultados
│   │
│   ├── tests/                         # Pruebas unitarias
│   │   ├── __init__.py
│   │   ├── conftest.py                # Fixtures
│   │   ├── test_graph_service.py
│   │   ├── test_tsp_algorithms.py
│   │   └── test_api/
│   │       ├── test_network_routes.py
│   │       └── test_tsp_routes.py
│   │
│   ├── requirements.txt               # Dependencias
│   ├── pytest.ini                     # Config de pytest
│   └── .env                           # Variables de entorno
│
├── docs/                               # Documentación técnica
│   ├── informe_tecnico.md             # Informe del proyecto
│   ├── analisis_asintotico.md         # Análisis teórico
│   ├── analisis_empirico.md           # Resultados experimentales
│   └── api_documentation.md           # Docs de la API
│
└── data/                               # Datos de prueba
    ├── sample_networks/
    │   ├── small_grid.geojson         # Red pequeña (5x5)
    │   ├── medium_city.geojson        # Red mediana (50 nodos)
    │   └── large_city.geojson         # Red grande (200 nodos)
    │
    └── sample_points/
        ├── points_5.geojson           # 5 puntos
        ├── points_10.geojson          # 10 puntos
        └── points_20.geojson          # 20 puntos
```

### Explicación de la Estructura

#### Frontend (Angular)

**`core/`** - Servicios y funcionalidad que se usa en toda la app (singleton)
- `services/`: Comunicación con API, estado global
- `models/`: Interfaces TypeScript compartidas
- `guards/`: Protección de rutas

**`shared/`** - Componentes, pipes y directivas reutilizables
- Componentes de UI genéricos
- Utilidades comunes

**`features/`** - Módulos funcionales independientes
- Cada feature tiene su propio módulo
- Componentes específicos de cada funcionalidad

#### Backend (Python)

**`api/routes/`** - Endpoints REST organizados por recurso
- Cada archivo maneja un tipo de operación
- Validación automática con Pydantic

**`services/`** - Lógica de negocio separada de las rutas
- Operaciones sobre grafos
- Implementación de algoritmos TSP
- Reutilizable y testeable

**`utils/`** - Funciones auxiliares puras
- Sin estado
- Operaciones específicas (parseo, geometría)

**`tests/`** - Suite completa de pruebas
- Tests unitarios por servicio
- Tests de integración para API
- Fixtures compartidos

---

## 🔄 Flujo de Funcionamiento

### 1. Carga de Red Vial

```
Usuario selecciona archivo GeoJSON/WKT
           ↓
Frontend envía archivo a POST /api/network
           ↓
Backend parsea el archivo
           ↓
Crea grafo NetworkX (nodos = intersecciones, aristas = calles)
           ↓
Retorna GeoJSON procesado + metadata
           ↓
Frontend visualiza red en Leaflet
```

**Ejemplo de entrada (GeoJSON):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[14.25, -90.52], [14.26, -90.51]]
      },
      "properties": {
        "name": "Calle Principal",
        "length": 1.2
      }
    }
  ]
}
```

---

### 2. Integración de Puntos de Interés

```
Usuario selecciona archivo de puntos
           ↓
Frontend envía a POST /api/points
           ↓
Backend procesa cada punto:
  1. Encuentra la arista (calle) más cercana
  2. Calcula proyección perpendicular
  3. Divide la arista en dos
  4. Inserta el punto como nuevo nodo
           ↓
Actualiza grafo NetworkX
           ↓
Retorna red actualizada + puntos integrados
           ↓
Frontend visualiza puntos en el mapa
```

**Proceso de integración:**

```
Antes:
A ────────────────── B  (calle completa)

Usuario quiere agregar punto P:
         P
         │ (distancia perpendicular)
A ───────X────────── B

Después:
A ───────X────────── B
         │
         P  (punto integrado como nodo)

Grafo actualizado:
- Eliminar arista A-B
- Agregar arista A-X con peso proporcional
- Agregar arista X-B con peso proporcional
- Agregar arista X-P con peso = distancia perpendicular
```

---

### 3. Ejecución de Algoritmos TSP

```
Usuario presiona "Calcular Rutas"
           ↓
Frontend envía POST /api/tsp/solve
           ↓
Backend ejecuta:
  
  1. Calcular matriz de distancias
     Para cada par de puntos (i, j):
       distancias[i][j] = dijkstra(grafo, i, j)
  
  2. Ejecutar algoritmo Fuerza Bruta
     - Iniciar cronómetro
     - Generar todas las permutaciones
     - Encontrar la mejor
     - Detener cronómetro
  
  3. Ejecutar algoritmo Greedy
     - Iniciar cronómetro
     - Aplicar estrategia de vecino más cercano
     - Detener cronómetro
  
  4. Ejecutar algoritmo 2-Opt
     - Iniciar cronómetro
     - Partir de solución greedy
     - Optimizar con intercambios
     - Detener cronómetro
  
  5. Para cada algoritmo, expandir ruta:
     ruta_nodos = [P1, P3, P2, P5, P4]
     
     Para cada segmento (Pi → Pj):
       camino_completo = dijkstra(grafo, Pi, Pj)
     
     ruta_expandida = concatenar todos los caminos
           ↓
Retorna JSON con 3 soluciones:
  - Secuencia de nodos visitados
  - Ruta completa expandida (todos los nodos intermedios)
  - Distancia total
  - Tiempo de ejecución
           ↓
Frontend visualiza cada ruta en color diferente
Frontend muestra tabla comparativa
```

**Ejemplo de respuesta:**
```json
{
  "algorithms": [
    {
      "name": "Brute Force",
      "route": [1, 3, 2, 5, 4, 1],
      "expanded_route": [1, 10, 11, 3, 12, 2, 13, 14, 5, 15, 4, 16, 1],
      "total_distance": 23.5,
      "execution_time_ms": 45.2
    },
    {
      "name": "Greedy",
      "route": [1, 2, 3, 4, 5, 1],
      "expanded_route": [...],
      "total_distance": 25.1,
      "execution_time_ms": 0.8
    },
    {
      "name": "2-Opt",
      "route": [1, 3, 2, 5, 4, 1],
      "expanded_route": [...],
      "total_distance": 23.7,
      "execution_time_ms": 3.2
    }
  ],
  "distance_matrix": [[0, 5.2, 7.1, ...], ...]
}
```

---

### 4. Visualización de Resultados

```
Frontend recibe resultados
           ↓
Para cada algoritmo:
  - Dibuja ruta en el mapa con color único
  - Agrega leyenda identificando cada algoritmo
           ↓
Muestra tabla comparativa:
  ┌──────────────┬──────────┬──────────┬─────────┐
  │ Algoritmo    │ Distancia│ Tiempo   │ Calidad │
  ├──────────────┼──────────┼──────────┼─────────┤
  │ Fuerza Bruta │ 23.5 km  │ 45.2 ms  │ 100%    │
  │ Greedy       │ 25.1 km  │ 0.8 ms   │ 93.6%   │
  │ 2-Opt        │ 23.7 km  │ 3.2 ms   │ 99.2%   │
  └──────────────┴──────────┴──────────┴─────────┘
           ↓
Usuario puede:
  - Activar/desactivar visualización de cada ruta
  - Descargar resultados en GeoJSON/WKT
  - Ver detalles de cada algoritmo
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Node.js** 18+ y npm
- **Python** 3.10+
- **Git**

### Instalación del Backend

```powershell
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verificar instalación:**
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Instalación del Frontend

```powershell
# Navegar a la carpeta frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
ng serve

# O especificar puerto
ng serve --port 4200
```

**Verificar instalación:**
- App: http://localhost:4200

### Configuración de Variables de Entorno

**Backend (`backend/.env`):**
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:4200

# Logging
LOG_LEVEL=INFO
```

**Frontend (`frontend/src/environments/environment.ts`):**
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

---

## 📊 Casos de Uso

### Caso de Uso 1: Carga de Red Vial

**Actor:** Usuario  
**Objetivo:** Visualizar una red vial en el mapa

**Flujo:**
1. Usuario hace clic en "Cargar Red Vial"
2. Selecciona archivo GeoJSON desde su disco
3. Sistema procesa el archivo
4. Sistema dibuja calles (líneas) e intersecciones (círculos) en el mapa
5. Sistema muestra estadísticas: número de nodos, aristas, longitud total

**Criterios de Aceptación:**
- ✅ El archivo se valida correctamente
- ✅ La red es visible en el mapa
- ✅ Se muestran estadísticas precisas
- ✅ Manejo de errores si el archivo es inválido

---

### Caso de Uso 2: Carga de Puntos de Interés

**Actor:** Usuario  
**Objetivo:** Integrar puntos a la red existente

**Precondición:** Red vial ya cargada

**Flujo:**
1. Usuario hace clic en "Cargar Puntos"
2. Selecciona archivo con coordenadas
3. Sistema encuentra la calle más cercana para cada punto
4. Sistema proyecta cada punto perpendicularmente
5. Sistema actualiza el grafo dividiendo aristas
6. Sistema muestra puntos integrados con marcadores especiales

**Criterios de Aceptación:**
- ✅ Cada punto se conecta a la arista más cercana
- ✅ Los puntos son visualmente distinguibles de los nodos normales
- ✅ La red se actualiza correctamente
- ✅ Se conserva la integridad del grafo

---

### Caso de Uso 3: Calcular y Comparar Rutas

**Actor:** Usuario  
**Objetivo:** Encontrar la mejor ruta y comparar algoritmos

**Precondición:** Red y puntos ya cargados

**Flujo:**
1. Usuario hace clic en "Calcular Rutas Óptimas"
2. Sistema ejecuta los 3 algoritmos en secuencia
3. Sistema muestra barra de progreso
4. Sistema dibuja las 3 rutas en colores diferentes:
   - 🔴 Rojo: Fuerza Bruta
   - 🟢 Verde: Greedy
   - 🔵 Azul: 2-Opt
5. Sistema muestra tabla comparativa con métricas
6. Usuario puede ocultar/mostrar cada ruta individualmente

**Criterios de Aceptación:**
- ✅ Los 3 algoritmos se ejecutan correctamente
- ✅ Las rutas son visualmente distinguibles
- ✅ Las métricas son precisas y comparables
- ✅ La interfaz responde durante el procesamiento

---

### Caso de Uso 4: Exportar Resultados

**Actor:** Usuario  
**Objetivo:** Descargar datos para análisis externo

**Precondición:** Algoritmos ya ejecutados

**Flujo:**
1. Usuario hace clic en "Exportar Resultados"
2. Selecciona formato (GeoJSON o WKT)
3. Sistema genera archivo con:
   - Red actualizada
   - Puntos de interés
   - Las 3 rutas calculadas
   - Metadata (distancias, tiempos)
4. Navegador descarga el archivo

**Criterios de Aceptación:**
- ✅ El archivo es válido según el formato elegido
- ✅ Incluye toda la información relevante
- ✅ Puede ser leído por software GIS (QGIS, ArcGIS)

---

## 🧪 Pruebas y Análisis

### Estrategia de Testing

#### 1. Pruebas Unitarias (Backend)

**Cobertura esperada:** >80%

**Áreas críticas:**
```python
# tests/test_graph_service.py
- Creación de grafo desde GeoJSON
- Integración de puntos a aristas
- Cálculo de matriz de distancias
- Validación de integridad del grafo

# tests/test_tsp_algorithms.py
- Fuerza bruta con casos conocidos
- Greedy con diferentes puntos de inicio
- 2-Opt con mejoras esperadas
- Comparación de resultados

# tests/test_geometry.py
- Proyección perpendicular
- Distancia punto-línea
- Cálculos de intersección
```

**Ejecutar pruebas:**
```powershell
cd backend
pytest --cov=app --cov-report=html
```

#### 2. Pruebas de Integración (API)

```python
# tests/test_api/test_integration.py
def test_complete_workflow():
    # 1. Cargar red
    response = client.post("/api/network", files={"file": network_file})
    assert response.status_code == 200
    
    # 2. Cargar puntos
    response = client.post("/api/points", files={"file": points_file})
    assert response.status_code == 200
    
    # 3. Calcular TSP
    response = client.post("/api/tsp/solve")
    assert response.status_code == 200
    assert len(response.json()["algorithms"]) == 3
```

#### 3. Pruebas de Rendimiento

**Datasets sintéticos:**

| Tamaño | Nodos Red | Puntos TSP | Objetivo Tiempo |
|--------|-----------|------------|-----------------|
| Pequeño| 20        | 5          | < 100ms         |
| Mediano| 100       | 10         | < 2s            |
| Grande | 500       | 15         | < 30s           |

**Script de generación:**
```python
# backend/tests/generate_test_data.py
def generate_random_network(num_nodes, density):
    """Genera red vial aleatoria"""
    pass

def generate_random_points(network, num_points):
    """Genera puntos aleatorios sobre la red"""
    pass
```

---

### Análisis Empírico

#### Experimentos a Realizar

**Experimento 1: Escalabilidad**
- Variar número de puntos TSP: 5, 7, 10, 12, 15, 20
- Medir tiempo de ejecución de cada algoritmo
- Graficar resultados

**Experimento 2: Calidad de Solución**
- Para cada tamaño, comparar distancia obtenida vs óptimo (cuando sea posible)
- Calcular % de desviación
- Analizar en qué casos cada algoritmo funciona mejor

**Experimento 3: Sensibilidad a la Red**
- Probar con redes de diferentes topologías:
  - Grid regular
  - Red tipo estrella
  - Red aleatoria
- Analizar cómo afecta al desempeño

#### Métricas a Reportar

```
Para cada combinación (algoritmo, tamaño):
  ✓ Tiempo promedio de ejecución (10 corridas)
  ✓ Desviación estándar del tiempo
  ✓ Distancia total de la ruta
  ✓ Desviación respecto al óptimo (cuando se conozca)
  ✓ Uso de memoria (si es relevante)
```

---

## 📈 Análisis Teórico vs Empírico

### Comparación Esperada

| Algoritmo     | Complejidad Teórica | Tiempo Esperado (10 puntos) | Tiempo Medido |
|---------------|---------------------|-----------------------------|---------------|
| Fuerza Bruta  | O(10!) = 3,628,800  | ~500ms                      | *A medir*     |
| Greedy        | O(10²) = 100        | ~2ms                        | *A medir*     |
| 2-Opt         | O(10² × k) ≈ 500    | ~10ms                       | *A medir*     |

### Gráficas a Incluir en el Informe

1. **Tiempo vs Tamaño del Problema**
   - Eje X: Número de puntos
   - Eje Y: Tiempo (escala logarítmica)
   - 3 líneas (una por algoritmo)

2. **Calidad de Solución vs Tiempo**
   - Eje X: Tiempo de ejecución
   - Eje Y: % respecto al óptimo
   - Scatter plot con los 3 algoritmos

3. **Escalabilidad**
   - Tabla mostrando tamaño máximo viable para cada algoritmo

---

## 🎓 Conclusiones

Este proyecto integra:
- ✅ **Teoría de grafos** (representación de redes)
- ✅ **Algoritmos clásicos** (Dijkstra, TSP)
- ✅ **Análisis de complejidad** (asintótico y empírico)
- ✅ **Desarrollo full-stack** (Angular + FastAPI)
- ✅ **Visualización de datos** (mapas interactivos)
- ✅ **Testing** (unitarias e integración)

### Habilidades Desarrolladas

- Implementación de algoritmos complejos
- Trabajo con estructuras de datos avanzadas (grafos)
- Análisis y comparación de rendimiento
- Desarrollo de aplicaciones web completas
- Procesamiento de datos geoespaciales
- Documentación técnica profesional

---

## 📚 Referencias y Recursos

### Papers y Artículos
1. Nogales Giné, R. "Different Approaches to Travelling Salesman Problem"
2. Kumar, R., Wei, X., Singh, A. "Different Approaches to Solve TSP"

### Bibliotecas Utilizadas
- **NetworkX**: https://networkx.org/documentation/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Angular**: https://angular.io/docs
- **Leaflet**: https://leafletjs.com/reference.html
- **Shapely**: https://shapely.readthedocs.io/

### Recursos Adicionales
- TSP Game (TUM): https://algorithms.discrete.ma.tum.de/graph-games/tsp-game/
- TSPLIB: http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/

---

## 👥 Autores

**Proyecto Final - Análisis de Algoritmos**  
Universidad: Ponticia Universidad Javeriana Bogotá  
Autores: Pablo Gonzales, Juliana Lugo, Juan Diego Arias y Santiago Mesa
Curso: Análisis de Algoritmos  
Instructor: Andrés Oswaldo Calderón Romero, Ph.D.  
Fecha: Noviembre 2025

---

## 📄 Licencia

Este proyecto es desarrollado con fines académicos.

---

**¿Preguntas?** Consulta la documentación en `/docs` o abre un issue en el repositorio.
