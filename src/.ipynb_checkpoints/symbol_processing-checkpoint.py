#Importe de libererias

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import glob
from joblib import Parallel, delayed
from clustered_stack import ClusteredStack  # Importamos la clase ClusteredStack

def procesar_simbolos(ruta_shp, ruta_ras, nombres_shp):
    """
    Procesa los rasters para cada geoforma según los símbolos en el shapefile.
    
    - ruta_shp: Ruta donde se encuentran los shapefiles.
    - ruta_ras: Ruta donde se encuentran los rasters.
    - nombres_shp: Diccionario con los nombres de los shapefiles.
    
    Devuelve un DataFrame con los resultados procesados.
    """
    # Cargar shapefile
    shapefiles = {clave: gpd.read_file(ruta_shp + value) for clave, value in nombres_shp.items()}
    geoforma = shapefiles["geom"]

    # Obtener lista única de símbolos, excluyendo MVV
    simbolos = geoforma["Simbolo"].unique()
    simbolos_filtrados = [s for s in simbolos if s != "MVV"]

    # Función para procesar un símbolo completo (paralelizable)
    def procesar_simbolo(simbolo):
        resultados_simbolo = []
        patron_busqueda = os.path.join(ruta_ras, f"*{simbolo}*.tif")
        archivos_raster = glob.glob(patron_busqueda)

        if not archivos_raster:
            print(f"No se encontraron rasters para el símbolo {simbolo}")
            return resultados_simbolo

        print(f"\nProcesando símbolo {simbolo}, archivos encontrados: {len(archivos_raster)}")

        for raster_path in archivos_raster:
            raster_name = os.path.basename(raster_path).split(".tif")[0]
            tipo_raster = raster_name.split("_")[0]  # Ej: DEM, Ind, etc.

            with rasterio.open(raster_path) as raster_data:
                num_bands = raster_data.count

                for band in range(1, num_bands + 1):
                    band_data = raster_data.read(band)
                    if band_data.shape[0] == 0 or band_data.shape[1] == 0:
                        continue

                    band_data_3d = band_data[np.newaxis, :, :]

                    # Usamos la clase ClusteredStack para hacer el clustering
                    clustered_models = ClusteredStack(band_data_3d)
                    clustered_models.set_raster_stack()

                    k_range = np.arange(2, 5, 1)
                    clustered_models.build_models(k_range)

                    current_best_k, current_best_silhouette = clustered_models.get_best_k()

                    resultados_simbolo.append({
                        "Simbolo": simbolo,
                        "Tipo": tipo_raster,
                        "Banda": band,
                        "k": current_best_k,
                        "Silhouette_Score": current_best_silhouette
                    })

        return resultados_simbolo

    # Procesamiento en paralelo por símbolo completo
    resultados_paralelo = Parallel(n_jobs=8)(
        delayed(procesar_simbolo)(simbolo) for simbolo in simbolos_filtrados
    )

    # Aplanar la lista de listas
    resultados_list = [item for sublist in resultados_paralelo for item in sublist]

    # Convertir a DataFrame
    resultados = pd.DataFrame(resultados_list)

    # Crear columnas combinadas tipo "DEM_B1"
    resultados["Tipo_Banda"] = resultados.apply(lambda x: f"{x['Tipo']}_B{x['Banda']}", axis=1)

    # Pivot para tener k y SS por banda
    tabla_pivot = resultados.pivot_table(index="Simbolo",
                                         columns="Tipo_Banda",
                                         values=["k", "Silhouette_Score"])

    # Aplanar columnas MultiIndex y renombrar SS para acortar
    nuevas_columnas = []
    for col in tabla_pivot.columns:
        if col[0] == "k":
            nuevas_columnas.append(f"k_{col[1]}")
        elif col[0] == "Silhouette_Score":
            nuevas_columnas.append(f"SS_{col[1]}")

    tabla_pivot.columns = nuevas_columnas

    tabla_pivot.reset_index(inplace=True)

    # Calcular promedios
    ss_cols = [col for col in tabla_pivot.columns if col.startswith("SS_")]
    k_cols = [col for col in tabla_pivot.columns if col.startswith("k_")]

    tabla_pivot["Promedio_SS"] = tabla_pivot[ss_cols].mean(axis=1)
    tabla_pivot["Promedio_k"] = tabla_pivot[k_cols].mean(axis=1).round().astype(int)

    # Organizar columnas
    columnas_ordenadas = ["Simbolo"] + k_cols + ss_cols + ["Promedio_SS", "Promedio_k"]
    tabla_final = tabla_pivot[columnas_ordenadas]

    return tabla_final
    print('\n\ntabla_final como retorno de la función lista para usar dentro del entorno')
