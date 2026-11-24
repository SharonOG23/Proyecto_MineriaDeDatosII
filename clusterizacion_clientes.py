# clusterizacion_clientes.py
# Examen Parcial II - Minería de Datos II

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

RUTA = "2mil_online_retail.csv"


def preparar_clientes(ruta=RUTA):
    """Lee el CSV (ya limpio) y resume una fila por cliente."""
    d = pd.read_csv(ruta, parse_dates=["InvoiceDate"])

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

    # log1p para que unos pocos clientes enormes no dominen la escala
    datos_est = pd.DataFrame(
        StandardScaler().fit_transform(np.log1p(datos_num)),
        columns=datos_num.columns,
        index=datos_num.index,
    )
    return datos_est, datos_num


class AnalisisClusters:
    nombre = "KMeans"

    def __init__(self, datos_est, datos_num, n_clusters=3):
        self.datos_est = datos_est
        self.datos_num = datos_num
        self.n_clusters = n_clusters
        self.df = None        # dim1, dim2 (solo para dibujar), cluster
        self.centros = None   # promedio de cada variable por cluster

    def elegir_k(self, k_max=8):
        """Calcula inercia (codo) y silueta para varios k."""
        ks = list(range(2, k_max + 1))
        inercias, siluetas = [], []
        for k in ks:
            km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(self.datos_est)
            inercias.append(km.inertia_)
            siluetas.append(silhouette_score(self.datos_est, km.labels_))
        return pd.DataFrame({"k": ks, "inercia": inercias, "silueta": siluetas}).set_index("k")

    def ajustar(self):
        # El KMeans se hace con TODAS las variables; el ACP es solo para poder dibujarlo en 2D
        kmeans = KMeans(n_clusters=self.n_clusters, max_iter=2000, n_init=150, random_state=42)
        clusters = kmeans.fit_predict(self.datos_est)

        self.df = pd.DataFrame(
            PCA(n_components=2).fit_transform(self.datos_est),
            columns=["dim1", "dim2"], index=self.datos_est.index,
        )
        self.df["cluster"] = clusters

        self.centros = np.array(
            [self.datos_num[clusters == i].mean() for i in range(self.n_clusters)]
        )
        self.silueta = silhouette_score(self.datos_est, clusters)
        return self

    def _codo(self, ax, tabla):
        ax.plot(tabla.index, tabla["inercia"], marker="o")
        ax.axvline(self.n_clusters, color="red", ls="--", label=f"k = {self.n_clusters}")
        ax.set_xlabel("k")
        ax.set_ylabel("Inercia")
        ax.set_title("Método del codo")
        ax.legend()
        ax.grid(True)

    def _silueta(self, ax, tabla):
        ax.plot(tabla.index, tabla["silueta"], marker="o", color="tab:green")
        ax.axvline(self.n_clusters, color="red", ls="--", label=f"k = {self.n_clusters}")
        ax.set_xlabel("k")
        ax.set_ylabel("Silueta")
        ax.set_title("Coeficiente de silueta")
        ax.legend()
        ax.grid(True)

    def _scatter(self, ax):
        for c in sorted(self.df["cluster"].unique()):
            sub = self.df[self.df["cluster"] == c]
            ax.scatter(sub["dim1"], sub["dim2"], label=f"Cluster {c} ({len(sub)})")
        ax.set_xlabel("dim1 (ACP)")
        ax.set_ylabel("dim2 (ACP)")
        ax.set_title(f"{self.nombre} - Clusters 2D")
        ax.legend()
        ax.grid(True)

    def _barras(self, fig, subgs):
        labels = self.datos_num.columns
        for i in range(self.n_clusters):
            ax = fig.add_subplot(subgs[0, i])
            ax.barh(labels, self.centros[i])
            ax.set_title(f"Cluster {i}")
            if i > 0:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=8)

    def _radar(self, ax):
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

    def graficar(self, k_max=8):
        """Codo + silueta + puntos + radar + barras en una sola figura."""
        if self.df is None:
            self.ajustar()
        tabla = self.elegir_k(k_max)

        fig = plt.figure(figsize=(16, 15))
        gs = fig.add_gridspec(3, 1, height_ratios=[0.8, 1.2, 1])

        arriba = gs[0].subgridspec(1, 2)
        self._codo(fig.add_subplot(arriba[0, 0]), tabla)
        self._silueta(fig.add_subplot(arriba[0, 1]), tabla)

        medio = gs[1].subgridspec(1, 2)
        self._scatter(fig.add_subplot(medio[0, 0]))
        self._radar(fig.add_subplot(medio[0, 1], polar=True))

        self._barras(fig, gs[2].subgridspec(1, self.n_clusters))

        fig.suptitle(f"Clusterización de clientes - {self.nombre} (silueta = {self.silueta:.2f})", fontsize=15)
        fig.tight_layout()
        plt.show()
        return self

    __call__ = graficar


if __name__ == "__main__":
    datos_est, datos_num = preparar_clientes()
    print(datos_num.shape)
    AnalisisClusters(datos_est, datos_num).graficar()
