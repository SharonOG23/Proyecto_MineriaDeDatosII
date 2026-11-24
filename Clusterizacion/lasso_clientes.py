# lasso_clientes.py
# Examen Parcial II - Minería de Datos II
# Análisis Lasso por cliente: selección de variables -> KMeans -> puntos + radar + barras

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV
from sklearn.cluster import KMeans
from math import pi
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

from pathlib import Path

RUTA = "2mil_online_retail.csv"


def preparar_clientes(ruta=RUTA):
    """Lee el CSV ya limpio y resume una fila por cliente."""
    ruta = Path(ruta)
    if not ruta.is_file() and ruta == Path(RUTA):
        for carpeta in (Path(__file__).resolve().parent, *Path(__file__).resolve().parents):
            for candidato in (carpeta / RUTA, carpeta / "processed" / RUTA):
                if candidato.is_file():
                    ruta = candidato
                    break
            if ruta.is_file():
                break
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


class AnalisisLasso:
    nombre = "Lasso"

    def __init__(self, datos_est, datos_num, objetivo="Gasto", excluir=("Ticket",), test_size=0.2):
        self.datos_est = datos_est
        self.datos_num = datos_num
        self.objetivo = objetivo
        # Ticket = Gasto / Facturas, así que se saca para que no "regale" la respuesta
        self.variables = [c for c in datos_est.columns if c != objetivo and c not in excluir]
        self.test_size = test_size
        self.modelo = None
        self.coef = None      # coeficiente de cada variable
        self.metricas = None  # R2 y MAE en train y test

    def ajustar(self):
        X = self.datos_est[self.variables]
        y = self.datos_est[self.objetivo]
        self.X_tr, self.X_te, self.y_tr, self.y_te = train_test_split(
            X, y, test_size=self.test_size, random_state=42
        )

        # LassoCV prueba muchos alpha con validación cruzada y se queda con el mejor
        self.modelo = LassoCV(cv=5, max_iter=10000, random_state=42).fit(self.X_tr, self.y_tr)
        self.coef = pd.Series(self.modelo.coef_, index=self.variables)

        self.pred_te = self.modelo.predict(self.X_te)
        self.metricas = {
            "alpha": self.modelo.alpha_,
            "R2 train": self.modelo.score(self.X_tr, self.y_tr),
            "R2 test": r2_score(self.y_te, self.pred_te),
            "MAE test": mean_absolute_error(self.y_te, self.pred_te),
            "Variables usadas": int((self.coef != 0).sum()),
        }
        return self

    def _agrupar(self):
        self.n_clusters = 3
        relevantes = self.coef[self.coef != 0].abs().sort_values(ascending=False)
        if len(relevantes) < 2:
            raise ValueError("Lasso seleccionó menos de dos variables no nulas.")
        self.columnas = relevantes.index[:2].tolist()
        self.df = self.datos_est[self.columnas].copy()
        self.df.columns = ["dim1", "dim2"]
        kmeans = KMeans(n_clusters=self.n_clusters, max_iter=2000, n_init=150, random_state=42)
        self.df["cluster"] = kmeans.fit_predict(self.df[["dim1", "dim2"]])
        self.centros = self.datos_num.groupby(self.df["cluster"]).mean().to_numpy()

    def _scatter(self, ax):
        for c in sorted(self.df["cluster"].unique()):
            sub = self.df[self.df["cluster"] == c]
            ax.scatter(sub["dim1"], sub["dim2"], label=f"Cluster {c} ({len(sub)})")
        ax.set_xlabel(self.columnas[0])
        ax.set_ylabel(self.columnas[1])
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
            if col.max() != col.min() else np.zeros_like(col)
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
        """Puntos + radar + barras en una sola figura."""
        if self.modelo is None:
            self.ajustar()
        self._agrupar()
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

