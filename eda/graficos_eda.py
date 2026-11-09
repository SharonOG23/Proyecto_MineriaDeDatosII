import matplotlib.pyplot as plt  # Para los gráficos
import pandas as pd              # Para las tablas
 
 
class GraficosEDA:
 
    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
 
    def __init__(self, datos, etiqueta=""):
        self.datos = datos        # Datos ya limpios (resultado de limpieza.limpiar())
        self.etiqueta = etiqueta  # Texto extra para los títulos, por ejemplo " (muestra)"
 
    # ---------- Países ----------
    def tabla_paises(self):
        # Ventas totales por país y su porcentaje
        ventas_pais = self.datos.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
        return pd.DataFrame({'Ventas (£)': ventas_pais.round(0), '% del total': (ventas_pais / ventas_pais.sum() * 100).round(1)}).head(10)
 
    def ventas_por_pais(self):
        # Reino Unido es casi todo, por eso se grafica sin él
        paises = self.datos[self.datos['Country'] != 'United Kingdom'].groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10)
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        ax.bar(paises.index, paises.values, color='blue')
        ax.set_title('Ventas por país (sin Reino Unido)' + self.etiqueta)
        ax.set_ylabel('Ventas (£)')
        plt.xticks(rotation=45)
        plt.show()
 
    # ---------- Tiempo ----------
    def ventas_por_mes(self):
        ventas_mes = self.datos.groupby('Mes')['TotalPrice'].sum()
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        ax.plot(ventas_mes.index, ventas_mes.values, marker='o', color='blue')
        ax.set_title('Ventas por mes' + self.etiqueta)
        ax.set_ylabel('Ventas (£)')
        plt.xticks(rotation=45)
        plt.show()
 
    def facturas_por_mes(self):
        facturas_mes = self.datos.groupby('Mes')['InvoiceNo'].nunique()
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        ax.bar(facturas_mes.index, facturas_mes.values, color='blue')
        ax.set_title('Facturas por mes' + self.etiqueta)
        plt.xticks(rotation=45)
        plt.show()
 
    def facturas_por_dia(self):
        facturas_dia = self.datos.groupby('Dia')['InvoiceNo'].nunique().reindex(self.DIAS).fillna(0)
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        ax.bar(facturas_dia.index, facturas_dia.values, color='blue')
        ax.set_title('Facturas por día' + self.etiqueta)
        plt.show()
 
    def facturas_por_hora(self):
        facturas_hora = self.datos.groupby('Hora')['InvoiceNo'].nunique()
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        ax.bar(facturas_hora.index, facturas_hora.values, color='blue')
        ax.set_title('Facturas por hora' + self.etiqueta)
        ax.set_xlabel('Hora')
        plt.show()
 
    # ---------- Productos ----------
    def tabla_top_productos(self, n=10):
        # Se cuenta en cuántas facturas aparece cada producto
        return self.datos.groupby('Description')['InvoiceNo'].nunique().sort_values(ascending=False).head(n)
 
    def top_productos(self, n=10):
        top_productos = self.tabla_top_productos(n)
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        ax.barh(top_productos.index, top_productos.values, color='blue')
        ax.invert_yaxis()
        ax.set_title(f'Top {n} productos por número de facturas' + self.etiqueta)
        plt.show()
 
    # ---------- Cantidad y precio ----------
    def hist_cantidad(self):
        # Se recorta para que se pueda ver el grueso de los datos
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        self.datos[self.datos['Quantity'] <= 50]['Quantity'].plot(kind='hist', bins=50, ax=ax, color='blue')
        ax.set_title('Cantidad por línea de factura (hasta 50)' + self.etiqueta)
        plt.show()
 
    def hist_precio(self):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        self.datos[self.datos['UnitPrice'] <= 15]['UnitPrice'].plot(kind='hist', bins=50, ax=ax, color='blue')
        ax.set_title('Precio unitario (hasta £15)' + self.etiqueta)
        plt.show()
 
    def boxplots(self):
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize = (12,5), dpi = 100)
        for i, col in enumerate(['Quantity', 'UnitPrice', 'TotalPrice']):
            ax[i].boxplot(self.datos[col])
            ax[i].set_yscale('log')
            ax[i].set_title(col)
        plt.show()
 
    # ---------- Productos por factura ----------
    def productos_por_factura(self):
        # Tabla con las estadísticas de productos distintos por factura
        return self.datos.groupby('InvoiceNo')['StockCode'].nunique()
 
    def hist_productos_por_factura(self, maximo=80, bins=40):
        productos_factura = self.productos_por_factura()
        if maximo is not None:
            productos_factura = productos_factura[productos_factura <= maximo]
 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize = (10,5), dpi = 100)
        productos_factura.plot(kind='hist', bins=bins, ax=ax, color='blue')
        ax.set_title('Productos distintos por factura' + (f' (hasta {maximo})' if maximo is not None else '') + self.etiqueta)
        plt.show()
