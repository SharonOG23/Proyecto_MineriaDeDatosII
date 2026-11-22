# lasso
# Examen Parcial II - Minería de Datos II
# Análisis Lasso por cliente

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV, lasso_path
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

from limpieza_datos import LimpiezaOnlineRetail

RUTA = "2mil_online_retail.csv"


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

    def _coeficientes(self, ax):
        c = self.coef.sort_values()
        colores = ["tab:red" if v < 0 else "tab:blue" for v in c]
        ax.barh(c.index, c.values, color=colores)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_title("Coeficientes (0 = variable eliminada)")
        ax.set_xlabel("Coeficiente")

    def _camino(self, ax):
        alphas, coefs, _ = lasso_path(self.X_tr, self.y_tr, alphas=100)
        for fila, nombre in zip(coefs, self.variables):
            ax.plot(alphas, fila, label=nombre)
        ax.axvline(self.modelo.alpha_, color="black", ls="--", label="alpha elegido")
        ax.set_xscale("log")
        ax.set_xlabel("alpha")
        ax.set_ylabel("Coeficiente")
        ax.set_title("Camino del Lasso")
        ax.legend(fontsize=7)
        ax.grid(True)

    def _error_cv(self, ax):
        error = self.modelo.mse_path_.mean(axis=1)
        ax.plot(self.modelo.alphas_, error)
        ax.axvline(self.modelo.alpha_, color="black", ls="--", label="alpha elegido")
        ax.set_xscale("log")
        ax.set_xlabel("alpha")
        ax.set_ylabel("Error cuadrático medio (CV)")
        ax.set_title("Validación cruzada")
        ax.legend()
        ax.grid(True)

    def _real_vs_predicho(self, ax):
        ax.scatter(self.y_te, self.pred_te, alpha=0.6)
        lim = [min(self.y_te.min(), self.pred_te.min()), max(self.y_te.max(), self.pred_te.max())]
        ax.plot(lim, lim, color="red", ls="--")
        ax.set_xlabel(f"{self.objetivo} real")
        ax.set_ylabel(f"{self.objetivo} predicho")
        ax.set_title("Real vs predicho (test)")
        ax.grid(True)

    def _residuales(self, ax):
        ax.hist(self.y_te - self.pred_te, bins=25, edgecolor="white")
        ax.axvline(0, color="red", ls="--")
        ax.set_xlabel("Residual")
        ax.set_ylabel("Clientes")
        ax.set_title("Residuales (test)")

    def _resumen(self, ax):
        ax.axis("off")
        texto = "\n".join(
            f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}"
            for k, v in self.metricas.items()
        )
        ax.text(0.05, 0.5, f"Objetivo: {self.objetivo}\n\n{texto}", fontsize=12, va="center")
        ax.set_title("Resumen del modelo")

    def graficar(self):
        """Todos los gráficos del Lasso en una sola figura."""
        if self.modelo is None:
            self.ajustar()

        fig, axs = plt.subplots(2, 3, figsize=(16, 9))
        self._coeficientes(axs[0, 0])
        self._camino(axs[0, 1])
        self._error_cv(axs[0, 2])
        self._real_vs_predicho(axs[1, 0])
        self._residuales(axs[1, 1])
        self._resumen(axs[1, 2])

        fig.suptitle(f"Análisis {self.nombre}", fontsize=15)
        fig.tight_layout()
        plt.show()
        return self

    __call__ = graficar


if __name__ == "__main__":
    datos_est, datos_num = preparar_clientes()
    print(datos_num.shape)
    lasso = AnalisisLasso(datos_est, datos_num).ajustar()
    print(lasso.coef)
    print(lasso.metricas)
    lasso.graficar()
