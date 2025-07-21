
# Análisis de Homogeneidad en Variables Formadoras del Suelo mediante Sensores Remotos

## Descripción

Este repositorio contiene el código y los datos necesarios para generar un **mapa de homogeneidad de las variables formadoras del suelo** utilizando imágenes de sensores remotos y cartografía temática en la cuenca de la quebrada Curití - Santander.

El proyecto identifica zonas homogéneas y heterogéneas dentro de cada forma del terreno, empleando índices espectrales, variables topográficas y técnicas de clasificación no supervisada.

Repositorio oficial: [DSVRUNAL/Proyecto---Homogeneidad-Variables-Formadoras-Suelo](https://github.com/DSVRUNAL/Proyecto---Homogeneidad-Variables-Formadoras-Suelo)

## Estructura del Proyecto

```
├── notebooks/
│   ├── Analysis.ipynb              # Clasificación K-means y análisis de resultados
│   ├── Data_preparation.ipynb      # Carga y preprocesamiento de datos
│   └── Visualization.ipynb         # Visualización de resultados
│
│   └── results/                     # Resultados gráficos generados
│       ├── Geoformas_Clasificadas.jpg
│       ├── Visualizacion_Raster_1Banda.jpg
│       └── Visualizacion_Raster_Multibanda.jpg
│
├── src/
│   ├── clip_rasters.py              # Recorte de capas raster
│   ├── clustered_stack.py           # Generación de pilas de variables clusterizadas
│   ├── data_preprocessing.py        # Preprocesamiento de variables
│   ├── raster_processing.py         # Procesamiento de raster
│   ├── symbol_processing.py         # Procesamiento de simbología para resultados
│   └── visualization_tools.py       # Funciones de visualización de raster
│
└── README.md
```

## Flujo de Trabajo

### 1. Preparación de Datos

- Cálculo de índices espectrales en Google Earth Engine:
  - NDVI, EVI, SAVI, BSI, NBR, NDMI, NDRGI.
- Generación de variables topográficas en SAGA GIS:
  - Pendiente, Aspecto, Índice de Convergencia, TWI, Profundidad del Valle.
- Rasterización de capas temáticas (Clima, Geología, Geomorfología, Material Parental).
- Armonización y generalización de variables a 20m de resolución.

### 2. Corte por Geoforma

Se realiza un corte del stack de variables por cada geoforma, utilizando un iterador sobre cada símbolo del mapa geomorfológico.

### 3. Clasificación con K-Means

Se aplica K-means por cada geoforma usando `Analysis.ipynb`:

```python
from src.clustered_stack import generar_clustered_stack

stack_clusterizado = generar_clustered_stack(ruta_stack, K)
```

Se calcula:
- Valor de K óptimo por geoforma.
- Silhouette Score por geoforma.
- Segmentación y almacenamiento de las métricas en un dataframe.

### 4. Criterios de Homogeneidad

La clasificación de homogeneidad se realiza con los siguientes criterios:

| Criterio | Descripción |
| -------- | ----------- |
| K promedio ≥ 2 y K promedio ≤ 4 | Indica estabilidad en la segmentación |
| Silhouette Score promedio ≥ 0.87 | Indica alta cohesión y separación entre clusters |

Si ambos criterios se cumplen, la geoforma se clasifica como **homogénea**.

### 5. Visualización de Resultados

Se generan mapas y salidas gráficas usando `Visualization.ipynb` y las funciones de `visualization_tools.py`.

Los resultados se guardan en:

```
notebooks/results/
├── Geoformas_Clasificadas.jpg
├── Visualizacion_Raster_1Banda.jpg
└── Visualizacion_Raster_Multibanda.jpg
```

## Resultados

- Mapas de homogeneidad por forma de la tierra.
- Dataframe con métricas por geoforma (K promedio, Silhouette Score promedio).

## Recomendaciones

- La función de K-means ya está paralelizada, por lo que se recomienda ajustar el número de núcleos según la capacidad del equipo.
- Implementar análisis por teselas si se requiere un análisis espacial más detallado.
