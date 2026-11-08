# limpieza_datos.py
# Examen Parcial II - Minería de Datos II


import numpy as np
import pandas as pd


class LimpiezaOnlineRetail:
    

    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    def __init__(self, ruta, exigir_cliente=True):
        self.ruta = ruta
        self.exigir_cliente = exigir_cliente
        self.datos = None
        self.cancelaciones = None
        self.pasos = []

    def cargar(self):
        if self.ruta.endswith(".csv"):
            self.datos = pd.read_csv(self.ruta, encoding="latin-1", parse_dates=["InvoiceDate"])
        else:
            self.datos = pd.read_excel(self.ruta)
        return self.datos

    def _paso(self, nombre, nuevo):
        """Guarda cuántas filas se eliminaron y se queda con el dataset nuevo."""
        self.pasos.append({"paso": nombre, "filas_eliminadas": len(self.datos) - len(nuevo)})
        self.datos = nuevo

    def limpiar(self):
        """Hace toda la limpieza en orden."""
        self.pasos = []

        # 1. Texto ordenado: sin espacios y la descripción en mayúsculas
        self.datos["InvoiceNo"] = self.datos["InvoiceNo"].astype(str)
        self.datos["StockCode"] = self.datos["StockCode"].astype(str).str.strip()
        self.datos["Description"] = self.datos["Description"].str.strip().str.upper()

        # 2. Filas repetidas
        self._paso("Duplicados", self.datos.drop_duplicates())

        # 3. Cancelaciones 
        es_cancelacion = self.datos["InvoiceNo"].str.startswith("C")
        self.cancelaciones = self.datos[es_cancelacion]
        self._paso("Cancelaciones (factura con C)", self.datos[~es_cancelacion])

        # 4. Códigos que no son productros
        es_producto = self.datos["StockCode"].str.match(r"^\d{5}")
        self._paso("Códigos que no son producto", self.datos[es_producto])

        # 5. Cantidades o precios en cero o negativos
        validos = (self.datos["Quantity"] > 0) & (self.datos["UnitPrice"] > 0)
        self._paso("Cantidad o precio <= 0", self.datos[validos])

        # 6. Líneas de más de £10.000
        total_linea = self.datos["Quantity"] * self.datos["UnitPrice"]
        self._paso("Líneas de más de £10.000", self.datos[total_linea < 10000])

        # 7. Descripción vacía
        self._paso("Description nula", self.datos.dropna(subset=["Description"]))

        # 8. Un código con varias descripciones: se deja la más común
        self.datos["Description"] = self.datos.groupby("StockCode")["Description"].transform(
            lambda x: x.mode()[0])

        # 9. Clientes nulos 
        if self.exigir_cliente:
            self._paso("CustomerID nulo", self.datos.dropna(subset=["CustomerID"]))
        self.datos["CustomerID"] = self.datos["CustomerID"].astype("Int64")   # 17850.0 -> 17850

        # 10. Columnas nuevas para el EDA
        self.datos["TotalPrice"] = (self.datos["Quantity"] * self.datos["UnitPrice"]).round(2)
        self.datos["Mes"] = self.datos["InvoiceDate"].dt.to_period("M").astype(str)
        self.datos["Dia"] = self.datos["InvoiceDate"].dt.dayofweek.map(dict(enumerate(self.DIAS)))
        self.datos["Hora"] = self.datos["InvoiceDate"].dt.hour

        self.datos = self.datos.reset_index(drop=True)
        return self.datos

    def resumen(self):
        """Tabla con las filas eliminadas en cada paso."""
        return pd.DataFrame(self.pasos)

    def matriz_canasta(self, pais=None):
        """Matriz facturas x productos (True/False)."""
        d = self.datos
        if pais:
            d = d[d["Country"] == pais]
        facturas = d["InvoiceNo"].astype("category")
        productos = d["Description"].astype("category")
        valores = np.zeros((len(facturas.cat.categories), len(productos.cat.categories)), dtype=bool)
        valores[facturas.cat.codes, productos.cat.codes] = True
        matriz = pd.DataFrame(valores, index=facturas.cat.categories, columns=productos.cat.categories)
        matriz.index.name = "InvoiceNo"
        matriz.columns.name = "Description"
        return matriz[matriz.sum(axis=1) >= 2]   # facturas de 1 solo producto no sirven

    def guardar(self, ruta="online_retail_limpio.csv"):
        self.datos.to_csv(ruta, index=False)


if __name__ == "__main__":
    limpieza = LimpiezaOnlineRetail("Online Retail.xlsx")
    limpieza.cargar()
    limpieza.limpiar()
    print(limpieza.resumen())
    print(limpieza.datos.shape)
