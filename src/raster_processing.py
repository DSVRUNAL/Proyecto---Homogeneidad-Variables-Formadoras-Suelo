# Importe de librerías

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_origirasterizacionhapefiles(ruta_shp, ruta_ras, nombres_shp, nombrescolumna_rasterizadalumn_dict):
    """
    Procesa los shapefiles y rasters: los carga, los rasteriza y los resamplea.
    """

    # Cargar los shapefiles
    shapefiles = {clave: gpd.read_file(ruta_shp + value) for clave, value in nombres_shp.items()}

    # Rasterizar shapefiles
    for clave, shapefile in shapefiles.items():
        for column, output_path in column_dict[clave].items():
            shapefile = shapefile.to_crs(epsg=9377)  # Asegura que el shapefile esté en el CRS correcto
            transform = from_origin(shapefile.total_bounds[0], shapefile.total_bounds[3], 20, 20)
            
            # Crear la plantilla para la rasterización (en blanco)
            with rasterio.open(output_path["raster"]) as src:
                meta = src.meta.copy()
                meta.update({
                    'dtype': 'float32',
                    'count': 1,
                    'crs': shapefile.crs,
                    'transform': transform,
                    'width': int((shapefile.total_bounds[2] - shapefile.total_bounds[0]) / 20),
                    'height': int((shapefile.total_bounds[3] - shapefile.total_bounds[1]) / 20)
                })

            # Crear una máscara rasterizada
            with rasterio.open(output_path["output"], 'w', **meta) as dst:
                out_image = np.zeros((meta['height'], meta['width']), dtype=np.float32)
                for _, row in shapefile.iterrows():
                    geometry = row['geometry']
                    value = row[column]  # Valor de la columna para rasterizar
                    geometry_mask(out_image, [geometry], transform, fill=0, invert=False, dtype=np.float32)
                    out_image[geometry_mask] = value
                dst.write(out_image, 1)  # Escribir la capa rasterizada

    # Resamplear rasters
    for raster, output in zip(nombres_raster.values(), ["output_dem_20m.tif", "output_indices_s2_20m.tif"]):
        with rasterio.open(ruta_ras + raster) as src:
            transform, width, height = calculate_default_transform(
                src.crs, src.crs, src.width, src.height, *src.bounds, resolution=(20, 20)
            )

            meta = src.meta.copy()
            meta.update({
                'crs': src.crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(output, 'w', **meta) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=src.crs,
                        resampling=Resampling.nearest
                    )

    print("Proceso de rasterización y resampleo completado.")
