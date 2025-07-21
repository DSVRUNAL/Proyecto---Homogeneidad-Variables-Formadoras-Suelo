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

def carga_shp_raster_proj(
    ruta_base_shp,
    nombres_shp,
    ruta_base_ras,
    nombres_raster,
    epsg_destino=9377
):
    # Se crea la lista de objetos vacía para cargar los shapefiles
    shp_cargados = {}
    for claves, nombre in nombres_shp.items():
        ruta = ruta_base_shp + nombre
        shapes = gpd.read_file(ruta).to_crs(epsg_destino)
        shp_cargados[claves] = shapes
        print(f'✅Shapefiles cargados {claves}\n') # imprime los shapes cargados como forma de ver que sí funciona para todos
    
    # Obtenemos el CRS de referencia del shapefile "limBuf"
    shp_referencia = shp_cargados.get("limBuf")
    crs_final = shp_referencia.crs
    print(f'✅CRS de los Shapefiles cargados {crs_final}\n')

    # Se crea la lista de objetos vacía para cargar los rasters
    rasters_cargados = {}
    for claver, nombre in nombres_raster.items():
        ruta = ruta_base_ras + nombre
        raster = rasterio.open(ruta)
        
        print(f'\n\nDatos del raster cargado {claver}\n', raster.meta) # imprime los metadatos de los raster cargados
        
        # Verifica si el CRS del raster es diferente al CRS del shapefile y se reproyecta en caso necesario
        if raster.crs != crs_final:
            print(f'\n\n⚠️ CRS del raster "{claver}" no coincide con el CRS de los shapefiles. Reproyectando...\n\n')
             
            # Calcular el transform y tamaño del raster reproyectado
            transform, width, height = calculate_default_transform(
                raster.crs,  # CRS original
                crs_final,   # CRS destino (del shapefile)
                raster.width,
                raster.height,
                *raster.bounds
            )
            
            # Crear los metadatos del raster reproyectado, preservando la descripción de las bandas
            metadato_repro = raster.meta.copy()
            metadato_repro.update({
                'crs': crs_final,  # Aseguramos que se pase el CRS correctamente
                'transform': transform,
                'width': width,
                'height': height,
                'nodata': raster.nodata,
                'count': raster.count,  # Mantener el número de bandas
                'dtype': raster.meta['dtype']  # Mantener el tipo de dato de las bandas
            })

            # Crear el array vacío para el raster reproyectado
            num_bandas = raster.count  # Cuenta el número de bandas del raster
            raster_reproyectado = np.empty((num_bandas, height, width), dtype=raster.meta['dtype'])  # Crear raster vacío

            # Reproyectar cada banda
            for i in range(1, num_bandas + 1):
                reproject(
                    source=rasterio.band(raster, i),
                    destination=raster_reproyectado[i - 1],
                    src_transform=raster.transform,
                    src_crs=raster.crs,
                    dst_transform=transform,
                    dst_crs=crs_final,
                    resampling=Resampling.bilinear  # Utiliza bilinear para datos continuos
                )

            # Guardar el raster reproyectado
            ruta_salida = ruta_base_ras + f"{Path(nombre).stem}_Reproyectado.tif"
            with rasterio.open(ruta_salida, 'w', **metadato_repro) as dst:
                dst.write(raster_reproyectado)

            raster.close()

            print(f"✅ Raster reproyectado y guardado en: {ruta_salida}\n\n")
        else:
            print(f'✅ Raster "{claver}" ya está en el mismo CRS de los shapefiles.')

        rasters_cargados[claver] = raster

    # Devuelve los shapefiles y rasters cargados para su uso posterior
    
    return {
        "shapefiles": shp_cargados,
        "rasters": rasters_cargados
    }