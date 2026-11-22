# Ridge.py
# Examen Parcial II - Minería de Datos II
# Análisis RIDGE por cliente: regresión L2 -> KMeans -> puntos + barras + radar

import sys
from pathlib import Path
from math import pi

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans

# El módulo de limpieza está en eda/, no junto a este archivo
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eda"))
from limpieza_datos import LimpiezaOnlineRetail

RUTA = str(Path(__file__).resolve().parents[1] / "processed" / "2mil_online_retail.csv")


def preparar_clientes(ruta=RUTA):
    """Limpia con LimpiezaOnlineRetail y resume una fila por cliente."""
    limpieza = LimpiezaOnlineRetail(ruta, exigir_cliente=True)
    limpieza.cargar()
    d = limpieza.limpiar()

    fecha_ref = d["InvoiceDate"].max() + pd.Timedelta(days=1)
    g = d.groupby("CustomerID")
    datos_num = pd.DataFrame({
        "Facturas": g["InvoiceNo"].nunique(),
        "Productos": g["StockCode"].nunique(),
        "Cantidad": g["Quantity"].sum(),
        "Gasto": g["TotalPrice"].sum(),
        "PrecioProm": g["UnitPrice"].mean(),
        "HoraProm": g["Hora"].mean(),
        "Inactividad": (fecha_ref - g["InvoiceDate"].max()).dt.days,
    })
    datos_num["Ticket"] = datos_num["Gasto"] / datos_num["Facturas"]

    # El log1p evita que unos pocos clientes dominen la escala
    datos_est = pd.DataFrame(
        StandardScaler().fit_transform(np.log1p(datos_num)),
        columns=datos_num.columns,
        index=datos_num.index,
    )
    return datos_est, datos_num


class AnalisisRidge:
    """Ajusta Ridge, agrupa a los clientes y dibuja los tres paneles."""

    nombre = "Ridge"

    def __init__(self, datos_est, datos_num, n_clusters=3, alpha=1.0):
        """Guarda los datos y los parámetros; los resultados empiezan vacíos."""
        self.datos_est = datos_est
        self.datos_num = datos_num
        self.n_clusters = n_clusters
        self.alpha = alpha
        self.df = None        # dim1, dim2, cluster
        self.centros = None   # promedio de cada variable por cluster

    def _reducir(self):
        """Ajusta Ridge sobre Gasto y toma las 2 variables con mayor coeficiente."""
        # Gasto se excluye de las entradas para que el modelo no copie la respuesta
        entradas = self.datos_est.drop(columns=["Gasto"])
        objetivo = self.datos_est["Gasto"]

        # La penalización L2 encoge los coeficientes sin llevarlos a cero
        modelo = Ridge(alpha=self.alpha, max_iter=10000).fit(entradas, objetivo)
        coeficientes = np.abs(modelo.coef_)
        columnas = entradas.columns[np.argsort(coeficientes)[-2:]][::-1]
        return self.datos_est[columnas].to_numpy()

    def ajustar(self):
        """Aplica KMeans sobre las 2 variables elegidas y calcula los promedios."""
        self.df = pd.DataFrame(
            self._reducir(), columns=["dim1", "dim2"], index=self.datos_est.index
        )
        kmeans = KMeans(n_clusters=self.n_clusters, max_iter=2000, n_init=150)
        self.df["cluster"] = kmeans.fit_predict(self.df[["dim1", "dim2"]])

        clusters = self.df["cluster"].values
        self.centros = np.array(
            [self.datos_num[clusters == i].mean() for i in range(self.n_clusters)]
        )
        return self

    def _scatter(self, ax):
        """Dibuja un conjunto de puntos por cluster en el plano 2D."""
        for c in sorted(self.df["cluster"].unique()):
            sub = self.df[self.df["cluster"] == c]
            ax.scatter(sub["dim1"], sub["dim2"], label=f"Cluster {c}")
        ax.set_xlabel("dim1")
        ax.set_ylabel("dim2")
        ax.set_title(f"{self.nombre} - Clusters 2D")
        ax.legend()
        ax.grid(True)

    def _barras(self, fig, subgs):
        """Muestra los promedios reales de cada variable en un panel por cluster."""
        labels = self.datos_num.columns
        for i in range(self.n_clusters):
            ax = fig.add_subplot(subgs[0, i])
            ax.barh(labels, self.centros[i])
            ax.set_title(f"Cluster {i}")
            if i > 0:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=8)

    def _radar(self, ax):
        """Compara los 8 perfiles en escala 0 a 100 dentro de un círculo."""
        labels = self.datos_num.columns
        centros = np.array([
            ((col - col.min()) / (col.max() - col.min()) * 100)
            if col.max() != col.min() else col
            for col in self.centros.T
        ]).T

        n_vars = len(labels)
        angulos = [n / float(n_vars) * 2 * pi for n in range(n_vars)]
        angulos += angulos[:1]

        for i in range(centros.shape[0]):
            valores = centros[i].tolist()
            valores += valores[:1]
            ax.plot(angulos, valores, label=f"Cluster {i}")
            ax.fill(angulos, valores, alpha=0.2)

        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(labels, fontsize=8)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))
        ax.set_title(f"{self.nombre} - Radar de Clusters")

    def graficar(self):
        """Puntos + barras + radar en una sola figura."""
        if self.df is None:
            self.ajustar()

        fig = plt.figure(figsize=(15, 11))
        gs = fig.add_gridspec(2, 1, height_ratios=[1.2, 1])

        top = gs[0].subgridspec(1, 2)
        self._scatter(fig.add_subplot(top[0, 0]))
        self._radar(fig.add_subplot(top[0, 1], polar=True))

        self._barras(fig, gs[1].subgridspec(1, self.n_clusters))

        fig.suptitle(f"Análisis {self.nombre}", fontsize=15)
        fig.tight_layout()
        plt.show()
        return self

    __call__ = graficar


if __name__ == "__main__":
    datos_est, datos_num = preparar_clientes()
    print(datos_num.shape)
    AnalisisRidge(datos_est, datos_num).graficar()
