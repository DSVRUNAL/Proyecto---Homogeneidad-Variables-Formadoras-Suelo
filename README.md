
# Análisis de Homogeneidad en Variables Formadoras del Suelo mediante Sensores Remotos

## Descripción

Este repositorio contiene el código y los datos necesarios para generar un **mapa de homogeneidad de las variables formadoras del suelo** utilizando imágenes de sensores remotos y cartografía temática en la cuenca de la quebrada Curití - Santander.

El proyecto identifica zonas homogéneas y heterogéneas dentro de cada forma del terreno, empleando índices espectrales, variables topográficas y técnicas de clasificación no supervisada.

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
│   ├── clustered_stack.py           # Generación de modelos de clustering por geoforma
│   ├── data_preprocessing.py        # Conversión de raster a dataframe y filtro por correlación
│   ├── raster_processing.py         # Rasterización y resampleo de capas vectoriales
│   ├── symbol_processing.py         # Procesamiento y análisis de símbolos por geoforma
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
from src.clustered_stack import ClusteredStack

modelo = ClusteredStack(raster_data)
modelo.set_raster_stack()
modelo.build_models(k_range=[2,3,4])
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

## Funciones Principales

### src/clip_rasters.py

**Función:**
- `cortar_rasters_por_geoformas(ruta_shp, ruta_ras, nombres_shp, nombres_raster, output_dir)`

**Entrada:**
- `ruta_shp`: ruta de los shapefiles.
- `ruta_ras`: ruta de los rasters.
- `nombres_shp`: diccionario de shapefiles.
- `nombres_raster`: diccionario de rasters.
- `output_dir`: directorio de salida.

**Salida:**
- Rasters recortados por geoforma, guardados en el directorio especificado.

---

### src/clustered_stack.py

**Clase:** `ClusteredStack`

**Métodos:**
- `set_raster_stack()`: reestructura y normaliza los datos.
- `build_models(k_values)`: entrena modelos K-means para un rango de K.
- `get_best_k()`: devuelve el mejor K y su Silhouette Score.
- `show_clustered()`: visualiza los clústeres.
- `show_inertia()`: muestra la curva del codo.
- `show_silhouette()`: muestra el gráfico de silhouette.

**Entrada:**
- Raster stack (array 3D).

**Salida:**
- Raster de etiquetas por K, valores de K óptimo y silhouette.

---

### src/data_preprocessing.py

**Función:**
- `carga_shp_raster_proj(ruta_base_shp, nombres_shp, ruta_base_ras, nombres_raster, epsg_destino)`

**Entrada:**
- Rutas y nombres de shapefiles y rasters.

**Salida:**
- Diccionario con shapefiles y rasters cargados y reproyectados.

---

### src/raster_processing.py

**Función:**
- `rasterizacion_shapefiles(ruta_shp, ruta_ras, nombres_shp, nombres_raster, column_dict)`

**Entrada:**
- Shapefiles, rasters y columnas a rasterizar.

**Salida:**
- Rasters de clima, geología y geomorfología rasterizados y resampleados a 20m.

---

### src/symbol_processing.py

**Función:**
- `procesar_simbolos(ruta_shp, ruta_ras, nombres_shp)`

**Entrada:**
- Rutas de entrada y diccionario de shapefiles.

**Salida:**
- DataFrame con los resultados de K y Silhouette por banda y símbolo, incluyendo promedios.

---

### src/visualization_tools.py

**Funciones:**
- `visualizar_dem(ruta_dem)`: visualiza un raster DEM de una banda.
- `visualizar_multibanda(ruta_raster)`: visualiza cada banda de un raster multibanda.

**Entrada:**
- Rutas de raster.

**Salida:**
- Gráficos con matplotlib.

## Resultados

- Mapas de homogeneidad por forma de la tierra.
- Dataframe con métricas por geoforma (K promedio, Silhouette Score promedio).

## Recomendaciones

- La función de K-means ya está paralelizada, por lo que se recomienda ajustar el número de núcleos dentro de la función symbol_processing.py según la capacidad del equipo. Por defecto está en 8 nucelos lógicos.

