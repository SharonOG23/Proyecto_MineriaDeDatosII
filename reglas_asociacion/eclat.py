from collections import defaultdict  # Para crear diccionarios con valores por defecto
from itertools import combinations   # Para generar combinaciones de items
 
from pathlib import Path             # Para armar la ruta del CSV
 
import matplotlib.pyplot as plt      # Para los gráficos
import pandas as pd                  # Para leer el CSV y guardar las reglas
 
 
class Eclat:  # Clase con el algoritmo ECLAT del notebook Practica-ECLAT
 
    def __init__(self, transactions=None, min_support=2, min_confidence=0.5):
        self.transactions = transactions if transactions is not None else {}  # {"T1": [items], ...}
        self.min_support = min_support        # Soporte mínimo absoluto (conteo)
        self.min_confidence = min_confidence  # Confianza mínima (solo para el gráfico de reglas)
        self.item_tidset = {}                 # {item: conjunto de transacciones}
        self.frequent_itemsets = {}           # {frozenset(itemset): soporte}
        self.rules = pd.DataFrame()           # Reglas (solo para el gráfico de reglas)
 
    # Carga el CSV y arma las transacciones: una factura = una transacción
    def load_csv(self, path, transaction_col="InvoiceNo", item_col="Description"):
        df = pd.read_csv(path)
        df = df.dropna(subset=[transaction_col, item_col])
        df[item_col] = df[item_col].astype(str).str.strip()
        df[transaction_col] = df[transaction_col].astype(str)
        self.transactions = (
            df.groupby(transaction_col)[item_col]
            .apply(lambda s: sorted(set(s)))
            .to_dict()
        )
        return self
 
    # 3. Función: genera los tidsets (en qué transacciones aparece cada item)
    def generate_tidsets(self):
        item_tidset = defaultdict(set)
        for tid, items in self.transactions.items():
            for item in items:
                item_tidset[item].add(tid)
        return item_tidset
 
    # Algoritmo ECLAT (recursivo)
    def eclat(self, prefix, items, min_support, frequent_itemsets):
        """
        prefix: list of items forming the current prefix
        items: list of tuples (item, tidset) to consider for extension
        min_support: absolute minimum support (count)
        frequent_itemsets: dict to collect results {frozenset(itemset): support_count}
        """
        while items:
            item, tidset = items.pop()
            support = len(tidset)
            if support >= min_support:
                new_itemset = prefix + [item]
                frequent_itemsets[frozenset(new_itemset)] = support
                suffix = []
                for other_item, other_tidset in items:
                    intersection = tidset & other_tidset
                    if len(intersection) >= min_support:
                        suffix.append((other_item, intersection))
                suffix = sorted(suffix, key=lambda x: len(x[1]))
                self.eclat(new_itemset, suffix, min_support, frequent_itemsets)
 
    # Ejecuta todo el proceso: tidsets -> items ordenados -> ECLAT
    def fit(self):
        self.item_tidset = self.generate_tidsets()
        items = sorted(self.item_tidset.items(), key=lambda x: len(x[1]))
        self.frequent_itemsets = {}
        self.eclat([], items, self.min_support, self.frequent_itemsets)
        return self
 
    # Imprime los tidsets de cada item
    def print_tidsets(self):
        for item, tidset in self.item_tidset.items():
            print(item, ":", sorted(tidset))
 
    # Imprime los itemsets frecuentes (ordenados como en el notebook)
    def print_itemsets(self):
        print("Frequent itemsets (as list) -> support count")
        for itemset, support in sorted(self.frequent_itemsets.items(), key=lambda x: (-len(x[0]), -x[1], sorted(list(x[0])))):
            print(list(itemset), "=>", support)
 
        # Con que frecuencia se compran los productos juntos.
 
    # Genera las reglas (soporte, confianza y lift). Se necesitan para plot_rules()
    def generate_rules(self):
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
                        rules.append(
                            {
                                "antecedente": sorted(antecedent),
                                "consecuente": sorted(consequent),
                                "soporte": round(sup_itemset / n, 4),
                                "confianza": round(confidence, 4),
                                "lift": round(confidence / (sup_c / n), 4),
                            }
                        )
        self.rules = pd.DataFrame(
            rules, columns=["antecedente", "consecuente", "soporte", "confianza", "lift"]
        )
        if not self.rules.empty:
            self.rules = self.rules.sort_values(["lift", "confianza"], ascending=False).reset_index(drop=True)
        return self.rules
 
    # Acorta los nombres largos para que quepan en los gráficos
    def _label(self, items, max_len=70):
        text = " + ".join(items)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."
 
    # Gráfico 1: productos más vendidos
    def plot_top_items(self, n=10):
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
 
    # Gráfico 2: combinaciones de productos más frecuentes
    def plot_top_itemsets(self, n=10, min_size=2):
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
 
    # Gráfico 3: reglas (soporte vs confianza, color según el lift)
    def plot_rules(self):
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
 
 
# Se utiliza para poder ejecutar la clase.
if __name__ == "__main__":
    # Ruta del CSV: sube de reglas_asociacion/ a la raíz del proyecto y entra a processed/
    ruta_csv = Path(__file__).resolve().parent.parent / "processed" / "2mil_online_retail.csv"
 
    modelo = Eclat(min_support=3, min_confidence=0.5)
    modelo.load_csv(ruta_csv, transaction_col="InvoiceNo", item_col="Description")
    modelo.fit()
    modelo.print_itemsets()
 
    modelo.generate_rules()
    modelo.plot_top_items()
    modelo.plot_top_itemsets()
    modelo.plot_rules()
