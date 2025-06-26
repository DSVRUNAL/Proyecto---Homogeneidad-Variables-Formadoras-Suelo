# Análisis de Homogeneidad en Variables Formadoras del Suelo mediante Sensores Remotos

## Descripción del Proyecto

El presente proyecto tiene como objetivo generar un mapa de homogeneidad de las variables formadoras del suelo utilizando imágenes de sensores remotos. El análisis se realiza para cada forma de la tierra interpretada en la cuenca de la quebrada Curití - Santander, con el fin de identificar vacíos de conocimiento en la caracterización del suelo.

## Objetivo Principal

* Generar un mapa de homogeneidad de las variables formadoras del suelo mediante imágenes de sensores remotos para cada forma de la tierra interpretada en la cuenca de la quebrada Curití - Santander.

## Fuentes de Información

Las siguientes fuentes de datos se utilizan en este proyecto:

* **Mapa Geomorfología:** A nivel de forma de la tierra.
* **Imágenes Sentinel 2:** Se utilizarán bandas SWIR, NIR, R, G, B.
    * **Índices Derivados:**
        * NDVI (Normalized Difference Vegetation Index).
        * EVI (Enhanced Vegetation Index).
        * SAVI (Soil Adjusted Vegetation Index).
        * BSI (Bare Soil Index).
        * SWI (Shortwave Infrared Index).
        * NDMI (Normalized Difference Moisture Index).
    * **Resolución:** Sentinel 2 tiene una resolución de 20m para una escala cartográfica máxima de 1:25.000 y un área mínima cartografiable de 1.5 ha.
* **DEM - Alos Palsar 12.5m:**.
    * Profundidad del valle.
    * Pendiente.
    * Curvatura del perfil respecto al plano vertical.
    * Curvatura respecto al plano horizontal.
    * Depresiones convergentes.
    * Direcciones de flujo.
    * Distancia de la red de canales.

## Metodología

La metodología para el análisis de homogeneidad sigue los siguientes pasos:

1.  **Armonización y Vectorización de Variables:** Las variables se armonizarán y vectorizarán, generalizándose a 20m y convirtiendo a centroides de píxel.
2.  **Correlación:** Se realizará un filtro para correlaciones mayores al 90% (inversa o directa).
3.  **Autocorrelación:** Se calculará el Índice de Morán Global, el Valor P y la puntuación Z (Z score).
    * **Interpretación del Índice de Morán:**
        * Si el valor P no es estadísticamente significativo, indica aleatoriedad completa y no se puede rechazar la hipótesis nula.
        * Si P es pequeño y Z es positiva, indica autocorrelación positiva estadísticamente significativa con altos-altos y bajos-bajos valores. Se puede rechazar la hipótesis nula.
        * Si P es pequeño y Z es negativa, indica autocorrelación negativa estadísticamente significativa con altos-bajos y bajos-altos valores. Se puede rechazar la hipótesis nula.
4.  **Clasificación Preliminar:**.
    * Si el Índice de Morán (IM) es diferente de cero ($IM \neq 0$).
    * Si el Valor P es menor a 0.05 ($P < 0.05$).
    * Si la puntuación Z está fuera del rango -1.96 a 1.96 ($Z > 1.96$ o $Z < -1.96$).
        * Si se cumplen estas condiciones, la zona es **Heterogénea**.
        * Si no se cumplen las condiciones, la zona es **Homogénea**.
5.  **Análisis de Puntos Calientes:** Se ejecuta por geoforma preclasificada, generando clusters por cada variable y conteo.
6.  **Clasificación Final de Formas del Terreno (Basado en Porcentaje de Variables Clusterizadas):**.
    * **0-65% de variables clusterizadas:** Zona homogénea.
    * **65-85% de variables clusterizadas:** Zona homogénea con el 65% al 85% de las variables clusterizadas.
    * **85-95% de variables clusterizadas:** Zona homogénea con el 85% al 95% de las variables clusterizadas.
    * **>95% de variables clusterizadas:** Zona homogénea con más del 95% de variables clusterizadas.