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

# Carga y proyección de datos 

# Se define la funcion con los argumentos de entrada y queda por defecto un EPSG 9377 para reproyectar los shapes
def carga_shp_raster_proj(
    ruta_base_shp,
    nombres_shp,
    ruta_base_ras,
    nombres_raster,
    epsg_destino=9377
):
# Se crea la lista de objetos vacía para cargar los shapefiles con un ciclo for que depende de los parámetros ingresados en "nombres_shp"
# Carga la ruta ingresada e itera buscando cada nombre para guardarlo en la lista "shp_cargados" al mismo tiempo que convierte el CRS de cada shape
    shp_cargados = {}
    for claves, nombre in nombres_shp.items():
        ruta = ruta_base_shp + nombre
        shapes = gpd.read_file(ruta).to_crs(epsg_destino)
        shp_cargados[claves] = shapes
        print(f'✅Shapefiles cargados {claves}\n') # imprime los shapes cargados como forma de ver que sí funciona para todos
        
# Se crea la lista de objetos vacía para cargar los raster con un ciclo for que depende de los parámetros ingresados en "nombres_raster"
# Carga la ruta ingresada e itera buscando cada nombre para guardarlo en la lista "rasters_cargados"
    shp_referencia = shp_cargados.get("limBuf")
    crs_final = shp_referencia.crs
    
    rasters_cargados = {}
    for claver, nombre in nombres_raster.items():
        ruta = ruta_base_ras + nombre
        raster = rasterio.open(ruta)
        
        print(f'\n\nDatos del raster cargado {claver}\n', raster.meta) # imprime los metadatos de los raster cargados como forma de ver que sí funciona para todos
        
        # verifica si el crs del raster es diferente a los shapefiles y se inicia el proceso de reproyección en caso que así sea
        if raster.crs != crs_final:
            print(f'\n\n⚠️ CRS del raster "{claver}" no coincide con el CRS de los shapefiles. Reproyectando...\n\n')
             
            transform, width, height = calculate_default_transform(
                raster.crs,
                crs_final,
                raster.width,
                raster.height,
                *raster.bounds
            )
            metadato_repro = raster.meta.copy()
            metadato_repro.update({
                'crs':  crs_final,
                'transform': transform,
                'width': width,
                'height': height,
                'nodata': raster.nodata
            })

            num_bandas = raster.count # Cuenta el numero de bandas del raster
            raster_reproyectado = np.empty((num_bandas,height, width), dtype=raster.meta['dtype']) # Crear raster vacío con el numero de bandas, ancho y largo de cada raster de entrada
            # Ciclo For que recorre por el numero de bandas para reproyectar cada una y guardarla en su orden
            for i in range(1,num_bandas+1):
                reproject(
                    source=rasterio.band(raster, i),
                    destination=raster_reproyectado[i-1],
                    src_transform=raster.transform,
                    src_crs=raster.crs,
                    dst_transform=transform,
                    dst_crs=crs_final,
                    resampling=Resampling.bilinear # bilinear Para datos continuos
                )
            ruta_salida = ruta_base_ras + f"{Path(nombre).stem}_Reproyectado.tif"
            with rasterio.open(ruta_salida, 'w', **metadato_repro) as dst:
                dst.write(raster_reproyectado)
            
            raster.close()
             
            print(f"✅ Raster reproyectado y guardado en: {ruta_salida}\n\n")
        else:
            print(f'✅ Raster "{claver}" ya está en el mismo CRS de los shapefiles.')
            
        rasters_cargados[claver] = raster
    
# Devuelve las dos listas creadas con los shapefiles y los rasters para seguirla usando en el entorno
    return {
        "shapefiles": shp_cargados,
        "rasters": rasters_cargados
    }
