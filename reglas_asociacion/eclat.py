from collections import defaultdict # Librería para crear diccionarios con valores por defecto
from itertools import combinations # Librería para generar combinaciones de elementos
import matplotlib.pyplot as plt # Librería para crear gráficos
import pandas as pd # Librería para manipulación y análisis de datos
 
 
class Eclat: # Clase que implementa el algoritmo Eclat para encontrar itemsets frecuentes y generar reglas de asociación.
 
    def __init__(self, min_support=2, min_confidence=0.5): # Inicializa la clase con soporte mínimo y confianza mínima.
        self.min_support = min_support # Soporte mínimo para considerar un itemset como frecuente.
        self.min_confidence = min_confidence # Confianza mínima para considerar una regla como válida.
        self.transactions = {} # Diccionario que almacenará las transacciones cargadas.
        self.item_tidset = {} # Diccionario que almacenará los conjuntos de transacciones (TID sets) para cada item.
        self.frequent_itemsets = {} # Diccionario que almacenará los itemsets frecuentes encontrados.
        self.rules = pd.DataFrame() # DataFrame que almacenará las reglas de asociación generadas.
 
    def load_csv(self, path, transaction_col="InvoiceNo", item_col="Description"): # Carga un archivo CSV y procesa las transacciones.
        df = pd.read_csv(path) # Lee el archivo CSV en un DataFrame de pandas.

        for col in (transaction_col, item_col): # Verifica que las columnas especificadas existan en el DataFrame.
            if col not in df.columns:
                raise ValueError(
                    f"La columna '{col}' no existe. Columnas disponibles: {list(df.columns)}"
                )
 
        df = df.dropna(subset=[transaction_col, item_col]) # Elimina filas con valores nulos en las columnas de transacción o item.
        df[item_col] = df[item_col].astype(str).str.strip() # Convierte los valores de la columna de items a cadenas y elimina espacios en blanco.
        df[transaction_col] = df[transaction_col].astype(str) # Convierte los valores de la columna de transacciones a cadenas.
 
        self.transactions = ( # Almacena las transacciones procesadas en un diccionario.
            df.groupby(transaction_col)[item_col]
            .apply(lambda s: sorted(set(s)))
            .to_dict()
        )
        return self
 
    def load_transactions(self, transactions): # Carga un diccionario de transacciones directamente.
        self.transactions = transactions
        return self
 
    def _absolute_min_support(self): # Calcula el soporte mínimo absoluto basado en el soporte mínimo relativo especificado.
        if isinstance(self.min_support, float) and self.min_support < 1:
            return max(1, int(round(self.min_support * len(self.transactions))))
        return int(self.min_support)
 
    def _generate_tidsets(self): # Genera los conjuntos de transacciones (TID sets) para cada item en las transacciones.
        item_tidset = defaultdict(set)
        for tid, items in self.transactions.items():
            for item in items:
                item_tidset[item].add(tid)
        self.item_tidset = dict(item_tidset)
 
    def _eclat(self, prefix, items, min_sup): # Implementa el algoritmo Eclat recursivamente para encontrar itemsets frecuentes.
        while items: # Mientras haya items en la lista, se procesan uno por uno.
            item, tidset = items.pop() # Se extrae un item y su conjunto de transacciones asociado.
            support = len(tidset) # Se calcula el soporte del itemset actual.
            if support >= min_sup: # Si el soporte es mayor o igual al soporte mínimo, se considera un itemset frecuente.
                new_itemset = prefix + [item] # Se crea un nuevo itemset combinando el prefijo actual con el item.
                self.frequent_itemsets[frozenset(new_itemset)] = support # Se almacena el itemset frecuente y su soporte en el diccionario de itemsets frecuentes.
 
                suffix = [] # Se crea una lista para almacenar los items que pueden formar nuevos itemsets frecuentes con el item actual.
                for other_item, other_tidset in items: # Se itera sobre los items restantes para encontrar combinaciones frecuentes.
                    intersection = tidset & other_tidset # Se calcula la intersección de los conjuntos de transacciones para determinar el soporte del nuevo itemset.
                    if len(intersection) >= min_sup: # Si la intersección tiene un soporte mayor o igual al soporte mínimo, se agrega a la lista de suffix.
                        suffix.append((other_item, intersection)) # Se agrega el item y su conjunto de transacciones intersectado a la lista de suffix.
 
                suffix.sort(key=lambda x: len(x[1])) # Se ordena la lista de suffix por el tamaño del conjunto de transacciones para optimizar la búsqueda.
                self._eclat(new_itemset, suffix, min_sup) # Se llama recursivamente a la función _eclat con el nuevo itemset y la lista de suffix para continuar buscando itemsets frecuentes.
 
    def fit(self): # Ejecuta el algoritmo Eclat para encontrar itemsets frecuentes en las transacciones cargadas.
        if not self.transactions:
            raise ValueError("No hay transacciones cargadas. Usa load_csv() o load_transactions().")
 
        self.frequent_itemsets = {}
        self._generate_tidsets()
 
        min_sup = self._absolute_min_support() # Calcula el soporte mínimo absoluto basado en el soporte mínimo relativo especificado.
        items = sorted(
            [(i, t) for i, t in self.item_tidset.items() if len(t) >= min_sup], # Filtra los items que cumplen con el soporte mínimo y los ordena por el tamaño del conjunto de transacciones.
            key=lambda x: len(x[1]), # Ordena los items por el tamaño del conjunto de transacciones para optimizar la búsqueda de itemsets frecuentes.
        )
        self._eclat([], items, min_sup) # Llama a la función _eclat para iniciar la búsqueda de itemsets frecuentes con un prefijo vacío y la lista de items filtrados.
        return self
 
    def get_frequent_itemsets(self): # Devuelve un DataFrame con los itemsets frecuentes encontrados, incluyendo su tamaño y soporte.
        n = len(self.transactions) # Calcula el número total de transacciones para calcular el soporte relativo de los itemsets frecuentes.
        rows = [ # Crea una lista de diccionarios que representan cada itemset frecuente y sus métricas asociadas.
            {
                "itemset": sorted(itemset), # Convierte el itemset a una lista ordenada para su presentación en el DataFrame.
                "tamaño": len(itemset), # Calcula el tamaño del itemset para incluirlo en el DataFrame.
                "soporte_abs": sup, # Almacena el soporte absoluto del itemset para incluirlo en el DataFrame.
                "soporte_rel": round(sup / n, 4), # Calcula el soporte relativo del itemset y lo redondea a 4 decimales para incluirlo en el DataFrame.
            }
            for itemset, sup in self.frequent_itemsets.items() # Itera sobre los itemsets frecuentes y sus soportes para crear la lista de diccionarios que se convertirá en un DataFrame.
        ]
        df = pd.DataFrame(rows, columns=["itemset", "tamaño", "soporte_abs", "soporte_rel"]) # Crea un DataFrame de pandas a partir de la lista de diccionarios, especificando las columnas que se incluirán en el DataFrame.
        return df.sort_values(["tamaño", "soporte_abs"], ascending=[False, False]).reset_index(drop=True) # Ordena el DataFrame por tamaño y soporte absoluto en orden descendente, y reinicia los índices del DataFrame antes de devolverlo.
 
    def generate_rules(self): # Genera reglas de asociación a partir de los itemsets frecuentes encontrados, calculando soporte, confianza y lift para cada regla.
        n = len(self.transactions)
        rules = []
 
        for itemset, sup_itemset in self.frequent_itemsets.items():
            if len(itemset) < 2:
                continue
            for r in range(1, len(itemset)):
                for antecedent in combinations(itemset, r):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
 
                    sup_a = self.frequent_itemsets[antecedent]
                    sup_c = self.frequent_itemsets[consequent]
                    confidence = sup_itemset / sup_a
 
                    if confidence >= self.min_confidence:
                        lift = confidence / (sup_c / n)
                        rules.append(
                            {
                                "antecedente": sorted(antecedent),
                                "consecuente": sorted(consequent),
                                "soporte": round(sup_itemset / n, 4),
                                "confianza": round(confidence, 4),
                                "lift": round(lift, 4),
                            }
                        )
 
        self.rules = pd.DataFrame(
            rules, columns=["antecedente", "consecuente", "soporte", "confianza", "lift"]
        )
        if not self.rules.empty:
            self.rules = self.rules.sort_values(
                ["lift", "confianza"], ascending=False
            ).reset_index(drop=True)
        return self.rules
 
    def _label(self, items, max_len=70): # Genera una etiqueta para un conjunto de items, truncando si excede la longitud máxima especificada.
        text = " + ".join(items)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."
 
    def plot_top_items(self, n=10): # Crea un gráfico de barras horizontales mostrando los n productos más vendidos según el soporte absoluto.
        data = sorted(
            [(next(iter(k)), v) for k, v in self.frequent_itemsets.items() if len(k) == 1],
            key=lambda x: x[1],
            reverse=True,
        )[:n]
        labels = [self._label([d[0]], 50) for d in data][::-1]
        values = [d[1] for d in data][::-1]
 
        plt.figure(figsize=(10, 5))
        plt.barh(labels, values, color="steelblue")
        plt.xlabel("Número de transacciones")
        plt.title(f"Top {n} productos más vendidos")
        plt.tight_layout()
        plt.show()
 
    def plot_top_itemsets(self, n=10, min_size=2): # Crea un gráfico de barras horizontales mostrando los n itemsets más frecuentes con al menos min_size productos.
        data = sorted(
            [(sorted(k), v) for k, v in self.frequent_itemsets.items() if len(k) >= min_size],
            key=lambda x: x[1],
            reverse=True,
        )[:n]
        labels = [self._label(d[0]) for d in data][::-1]
        values = [d[1] for d in data][::-1]
 
        plt.figure(figsize=(12, 5))
        plt.barh(labels, values, color="darkorange")
        plt.xlabel("Número de transacciones")
        plt.title(f"Top {n} combinaciones de productos más frecuentes")
        plt.tight_layout()
        plt.show()
 
    def plot_rules(self): # Crea un gráfico de dispersión mostrando las reglas de asociación generadas, con soporte en el eje x, confianza en el eje y y lift representado por el color de los puntos.
        if self.rules.empty:
            raise ValueError("No hay reglas. Ejecuta generate_rules() primero.")
 
        plt.figure(figsize=(9, 6))
        scatter = plt.scatter(
            self.rules["soporte"],
            self.rules["confianza"],
            c=self.rules["lift"],
            cmap="viridis",
            s=60,
            alpha=0.8,
        )
        plt.colorbar(scatter, label="Lift")
        plt.xlabel("Soporte")
        plt.ylabel("Confianza")
        plt.title("Reglas de asociación: soporte vs confianza")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()
 
    def summary(self): # Imprime un resumen de las transacciones, productos distintos, soporte mínimo, itemsets frecuentes y reglas generadas.
        print(f"Transacciones:            {len(self.transactions)}") # Imprime el número total de transacciones cargadas.
        print(f"Productos distintos:      {len(self.item_tidset)}") # Imprime el número de productos distintos encontrados en las transacciones.
        print(f"Soporte mínimo (abs):     {self._absolute_min_support()}") # Imprime el soporte mínimo absoluto calculado a partir del soporte mínimo relativo especificado.
        print(f"Itemsets frecuentes:      {len(self.frequent_itemsets)}") # Imprime el número de itemsets frecuentes encontrados por el algoritmo Eclat.
        print(f"Reglas generadas:         {len(self.rules)}") # Imprime el número de reglas de asociación generadas a partir de los itemsets frecuentes.
 

# Se utiliza para poder ejecutar la clase.

if __name__ == "__main__":
    pd.set_option("display.max_colwidth", 80)
    pd.set_option("display.width", 200)
 
    modelo = Eclat(min_support=3, min_confidence=0.5)
    modelo.load_csv(
    "2mil_online_retail.csv",
    transaction_col="InvoiceNo",
    item_col="Description",
    )
    modelo.fit()
    reglas = modelo.generate_rules()
 
    modelo.summary()
 
    print("\n=== Top 15 combinaciones de productos más compradas en la misma factura ===")
    itemsets = modelo.get_frequent_itemsets()
    print(itemsets[itemsets["tamaño"] >= 2].head(15).to_string(index=False))
 
    print("\n=== Top 15 reglas de asociación ===")
    print(reglas.head(15).to_string(index=False))
 
    modelo.plot_top_items()
    modelo.plot_top_itemsets()
    modelo.plot_rules()
 
    reglas.to_csv("reglas_eclat.csv", index=False)
    itemsets.to_csv("itemsets_eclat.csv", index=False)