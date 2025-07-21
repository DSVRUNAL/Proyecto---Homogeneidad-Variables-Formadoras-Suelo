# Importe de librerías

import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask

def cortar_rasters_por_geoformas(ruta_shp, ruta_ras, nombres_shp, nombres_raster, output_dir):
    """
    Corta los rasters según las geoformas definidas en un shapefile.
    
    - ruta_shp: Ruta donde se encuentran los shapefiles.
    - ruta_ras: Ruta donde se encuentran los rasters.
    - nombres_shp: Diccionario con los nombres de los shapefiles.
    - nombres_raster: Diccionario con los nombres de los rasters.
    - output_dir: Directorio donde se guardarán los rasters cortados.
    """

    # Cargar shapefiles
    shapefiles = {claves: gpd.read_file(ruta_shp + value) for claves, value in nombres_shp.items()}

    # Cargar rasters
    rasters = {claver: rasterio.open(ruta_ras + value) for claver, value in nombres_raster.items()}

    # Crear el directorio para los rasters cortados si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Iterar sobre cada geoforma
    for geoforma in shapefiles["geom"]["Simbolo"].unique():
        geoforma_gdf = shapefiles["geom"][shapefiles["geom"]["Simbolo"] == geoforma]

        # Obtener la geometría completa de la geoforma (usando union_all)
        geoforma_geometry = geoforma_gdf.geometry.union_all()  # Unión de todas las geometrías de la geoforma

        # Iterar sobre los rasters (DEM, índices_S2, clima)
        for raster_name, raster_data in rasters.items():
            print(f"Procesando {raster_name} para geoforma {geoforma}")

            out_image, out_transform = mask(raster_data, [geoforma_geometry], crop=True)

            # Verificar si el recorte tiene datos válidos
            if out_image.shape[1] == 0 or out_image.shape[2] == 0:
                print(f"No hay datos recortados para la geoforma {geoforma} y el raster {raster_name}")
                continue
            
            print(f"Recorte de {raster_name} para geoforma {geoforma} fue exitoso")
            
            # Generar nombre del raster cortado
            if raster_name == "indices_S2":
                output_raster_name = f"Ind_{geoforma}.tif"
            elif raster_name == "dem":
                output_raster_name = f"DEM_{geoforma}.tif"
            elif raster_name == "climaP":
                output_raster_name = f"ClimaP_{geoforma}.tif"
            elif raster_name == "climaC":
                output_raster_name = f"ClimaC_{geoforma}.tif"
            elif raster_name == "geol":
                output_raster_name = f"geol_{geoforma}.tif"
            else:
                print('No tengo nombre')
                continue

            output_raster_path = os.path.join(output_dir, output_raster_name)
            out_meta = raster_data.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "count": out_image.shape[0],  # Número de bandas
                "dtype": out_image.dtype
            })
            
            # Guardar el raster cortado
            with rasterio.open(output_raster_path, 'w', **out_meta) as dest:
                dest.write(out_image)

            print(f"Raster cortado guardado como: {output_raster_path}")
