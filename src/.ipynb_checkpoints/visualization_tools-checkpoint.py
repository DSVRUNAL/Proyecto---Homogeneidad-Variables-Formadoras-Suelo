# Importe de librerias
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.patches import Patch
import numpy as np
import shapely
import rasterio
import rasterio.plot
from rasterio.mask import mask
from shapely.geometry import mapping
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Se defne funcion de visualizacion para el DEM que solo tiene 1 banda
# Tiene como argumentos de entrada la ruta del dem y el cmap por defecto es "terrain"
def visualizar_dem(ruta_dem, cmap='terrain'):
# Abre el raster, obtiene los datos, el nodata y crea la mascara para los nodata
    with rasterio.open(ruta_dem) as dem:
        data = dem.read(1)
        nodata = dem.nodata
        data = np.ma.masked_equal(data, nodata)
# Plotea la figura
        plt.figure(figsize=(8, 6))
        plt.imshow(data, cmap=cmap)
        plt.colorbar(label="Elevación [m]")
        plt.title("Visualización DEM Cortado y Reproyectado")
        plt.axis("off")
        plt.show()

# Se defne funcion de visualizacion para raster con varias bandas (sentinel 2)
# Tiene como argumentos de entrada la ruta del raster y el cmap por defecto es "viridis"
def visualizar_multibanda(ruta_raster, cmap='viridis'):
# Abre el raster y obtiene el numero de bandas (imprime la cantidad para verificar), los datos, el nodata y crea la mascara de los nodata
    with rasterio.open(ruta_raster) as multibanda:
        num_bandas = multibanda.count
        print(f"Imagen Multibanda graficando ... Cantidad de bandas: {num_bandas}")
        data = multibanda.read()
        nodata = multibanda.nodata
        data = np.ma.masked_equal(data, nodata)
# Se definen los parámetros de los subplots dependiendo de la cantidad de bandas que tenga el raster
        filas = 2
        columnas = int(np.ceil(num_bandas / filas))
# Se crean los parámetros de los subplots
        fig, axes = plt.subplots(filas, columnas, figsize=(20, 10))
        axes = axes.flatten() # Para convertir los axes en un vector de 1D
# Se hace ciclo for que depende del numero de bandas para recorrer el raster, se pasan los parametros del subplot y se plotea
        for i in range(num_bandas):
            ax = axes[i]
            im = ax.imshow(data[i], cmap=cmap)
            ax.set_title(f"Banda {i+1}")
            ax.axis("off")
            plt.colorbar(im, ax=ax, shrink=0.6)

# Se ocultan subplots sobrantes en caso que la cantidad de bandas sea impar
        for j in range(num_bandas, len(axes)):
            axes[j].axis("off")

        plt.suptitle("Bandas raster multibanda", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()