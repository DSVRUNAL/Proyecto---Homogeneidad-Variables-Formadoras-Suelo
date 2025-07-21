#Importe de librerías

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

class ClusteredStack:
    def __init__(self, raster_data): 
        self.raster_data = raster_data  # Array 3D de NumPy (bandas, filas, columnas)
        self.model_input = None  # La matriz de datos reestructurada  
        self.height = self.width = self.depth = 0  # Dimensiones de la imagen
        self.k_range = []  # Lista de todos los valores de k (número de clústeres) a evaluar
        self.models = []  # Modelos de KMeans entrenados para cada k
        self.predicted_rasters = []  # Imágenes de etiquetas de clústeres (reestructuradas al tamaño del raster)
        self.inertia_scores = []  # Puntuaciones de inercia (suma de distancias al cuadrado dentro de los clústeres)
        self.silhouette_scores = []  # Puntuaciones de Silhouette (medida de separación entre clústeres)
        self.best_k = None  # Mejor k basado en la puntuación de silhouette
        self.best_silhouette = -1  # Mejor puntuación de silhouette encontrada

    def set_raster_stack(self):
        """Lee el raster y lo reestructura en un formato adecuado para K-Means."""
        stack = self.raster_data

        # Reemplaza los valores NaN con cero (importante para KMeans)
        stack = np.nan_to_num(stack)

        self.depth, self.height, self.width = stack.shape
        # Reestructura el array 3D en una matriz 2D de forma (n_píxeles, n_bandas)
        self.model_input = stack.reshape(self.depth, -1).T

        # Escala los datos de entrada (importante para KMeans)
        scaler = StandardScaler()
        self.model_input = scaler.fit_transform(self.model_input)

    def build_models(self, k_values):
        """Entrena un modelo K-Means de clustering para cada valor de k."""
        self.k_range = list(k_values)
        n_datos = self.model_input.shape[0]
        
        for k in self.k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(self.model_input)

            self.models.append(km)
            self.inertia_scores.append(km.inertia_)

            # Calcular el silhouette score solo si hay más de 1 clúster
            if k > 1:
                silhouette_avg = silhouette_score(self.model_input, labels)
                if n_datos <= 10000:
                    # Si son pocos puntos, calcula silhouette normal
                    silhouette_avg = silhouette_score(self.model_input, labels)
                else:
                    # Si hay muchos puntos, muestrea
                    sample_size = min(5000, int(n_datos * 0.1))  # Máximo 5000 o 10% del total
                    idx = np.random.choice(n_datos, sample_size, replace=False)
                    X_sample = self.model_input[idx]
                    labels_sample = labels[idx]
    
                    silhouette_avg = silhouette_score(X_sample, labels_sample)
            else:
                silhouette_avg = np.nan  # Si solo hay un clúster, no se puede calcular el silhouette score

            self.silhouette_scores.append(silhouette_avg)
            self.predicted_rasters.append(labels.reshape(self.height, self.width))

            # Si el número de clústeres encontrados es menor que el valor de k, se registra
            num_clusters = len(np.unique(labels))
            #print(f"Geoforma con k={k}: Se encontraron {num_clusters} clústeres (Silhouette Score: {silhouette_avg})")

            # Actualizar el mejor k si la puntuación de silhouette es mayor
            if silhouette_avg > self.best_silhouette:
                self.best_silhouette = silhouette_avg
                self.best_k = k
                
    def get_best_k(self):
        """Devuelve el mejor k basado en la puntuación de silhouette."""
        return self.best_k, self.best_silhouette

    def show_clustered(self, cmap="Accent"):
        """Muestra el raster agrupado para cada k."""
        for k, img_cls in zip(self.k_range, self.predicted_rasters):
            plt.figure(figsize=(5, 5))
            plt.imshow(img_cls, cmap=cmap)
            plt.title(f"{k} clústeres")
            plt.axis("off")
            plt.colorbar()
            plt.show()

    def show_inertia(self):
        """Muestra las puntuaciones de inercia para cada k."""
        plt.figure(figsize=(5, 4))
        plt.plot(self.k_range, self.inertia_scores, "o-")
        plt.xlabel("Número de clústeres (k)")
        plt.ylabel("Inercia")
        plt.title("Método del codo")
        plt.show()

    def show_silhouette(self):
        """Muestra las puntuaciones de silhouette para cada k."""
        plt.figure(figsize=(5, 4))
        plt.plot(self.k_range, self.silhouette_scores, "o-")
        plt.xlabel("Número de clústeres (k)")
        plt.ylabel("Coef. de Silhouette")
        plt.title("Puntuaciones de Silhouette")
        plt.show()
