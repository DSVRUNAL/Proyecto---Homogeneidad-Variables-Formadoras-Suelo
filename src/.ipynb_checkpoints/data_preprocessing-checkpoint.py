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

def carga_shp_raster_proj():

    #Rutas para cargar archivos shape
    SHP=r"/notebooks/Insumos_Proyecto_Clase/"
    geom_ruta=SHP+r"Geomorfologia.shp"
    geol_ruta=SHP+r"Geologia.shp"
    clim_ruta=SHP+r"Clima_IGAC.shp"
    limBuf_ruta=SHP+r"Limite_Buff_500.shp"
    # Carga de archivos shape y proyeccion a EPSG 9377
    geom_shp = gpd.read_file(geom_ruta)
    geom_shp = geom_shp.to_crs(9377)
    
    geol_shp = gpd.read_file(geol_ruta)
    geol_shp = geol_shp.to_crs(9377)
    
    clim_shp = gpd.read_file(clim_ruta)
    clim_shp = clim_shp.to_crs(9377)
    
    limBuf_shp = gpd.read_file(limBuf_ruta)
    limBuf_shp = limBuf_shp.to_crs(3116)
    
    #Rutas para raster
    RAS=r"/notebooks/Insumos_Proyecto_Clase/"
    Sentinel_ruta=RAS+r"Sentinel2.tif"
    Dem_ruta=RAS+r"Dem_alos_125.tif"
    
    #Carga de raster
    sentinel2 = rasterio.open(Sentinel_ruta)
    dem = rasterio.open(Dem_ruta)
    print('Datos del DEM\n',dem.meta)
    print('Datos del Sentinel 2\n',sentinel2.meta)