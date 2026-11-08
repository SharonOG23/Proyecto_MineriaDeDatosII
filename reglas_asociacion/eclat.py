from collections import defaultdict
from itertools import combinations
 
import matplotlib.pyplot as plt
import pandas as pd
 
 
class Eclat:
 
    def __init__(self, min_support=2, min_confidence=0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.transactions = {}
        self.item_tidset = {}
        self.frequent_itemsets = {}
        self.rules = pd.DataFrame()
 
    def load_csv(self, path, transaction_col="InvoiceNo", item_col="Description"):
        df = pd.read_csv(path)
 
        for col in (transaction_col, item_col):
            if col not in df.columns:
                raise ValueError(
                    f"La columna '{col}' no existe. Columnas disponibles: {list(df.columns)}"
                )
 
        df = df.dropna(subset=[transaction_col, item_col])
        df[item_col] = df[item_col].astype(str).str.strip()
        df[transaction_col] = df[transaction_col].astype(str)
 
        self.transactions = (
            df.groupby(transaction_col)[item_col]
            .apply(lambda s: sorted(set(s)))
            .to_dict()
        )
        return self
 
    def load_transactions(self, transactions):
        self.transactions = transactions
        return self
 
    def _absolute_min_support(self):
        if isinstance(self.min_support, float) and self.min_support < 1:
            return max(1, int(round(self.min_support * len(self.transactions))))
        return int(self.min_support)
 
    def _generate_tidsets(self):
        item_tidset = defaultdict(set)
        for tid, items in self.transactions.items():
            for item in items:
                item_tidset[item].add(tid)
        self.item_tidset = dict(item_tidset)
 
    def _eclat(self, prefix, items, min_sup):
        while items:
            item, tidset = items.pop()
            support = len(tidset)
            if support >= min_sup:
                new_itemset = prefix + [item]
                self.frequent_itemsets[frozenset(new_itemset)] = support
 
                suffix = []
                for other_item, other_tidset in items:
                    intersection = tidset & other_tidset
                    if len(intersection) >= min_sup:
                        suffix.append((other_item, intersection))
 
                suffix.sort(key=lambda x: len(x[1]))
                self._eclat(new_itemset, suffix, min_sup)
 
    def fit(self):
        if not self.transactions:
            raise ValueError("No hay transacciones cargadas. Usa load_csv() o load_transactions().")
 
        self.frequent_itemsets = {}
        self._generate_tidsets()
 
        min_sup = self._absolute_min_support()
        items = sorted(
            [(i, t) for i, t in self.item_tidset.items() if len(t) >= min_sup],
            key=lambda x: len(x[1]),
        )
        self._eclat([], items, min_sup)
        return self
 
    def get_frequent_itemsets(self):
        n = len(self.transactions)
        rows = [
            {
                "itemset": sorted(itemset),
                "tamaño": len(itemset),
                "soporte_abs": sup,
                "soporte_rel": round(sup / n, 4),
            }
            for itemset, sup in self.frequent_itemsets.items()
        ]
        df = pd.DataFrame(rows, columns=["itemset", "tamaño", "soporte_abs", "soporte_rel"])
        return df.sort_values(["tamaño", "soporte_abs"], ascending=[False, False]).reset_index(drop=True)
 
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
 
    def _label(self, items, max_len=70):
        text = " + ".join(items)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."
 
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
 
    def summary(self):
        print(f"Transacciones:            {len(self.transactions)}")
        print(f"Productos distintos:      {len(self.item_tidset)}")
        print(f"Soporte mínimo (abs):     {self._absolute_min_support()}")
        print(f"Itemsets frecuentes:      {len(self.frequent_itemsets)}")
        print(f"Reglas generadas:         {len(self.rules)}")
 
 
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
 
    print("\n=== Top 15 itemsets frecuentes (2+ productos) ===")
    itemsets = modelo.get_frequent_itemsets()
    print(itemsets[itemsets["tamaño"] >= 2].head(15).to_string(index=False))
 
    print("\n=== Top 15 reglas de asociación ===")
    print(reglas.head(15).to_string(index=False))
 
    modelo.plot_top_items()
    modelo.plot_top_itemsets()
    modelo.plot_rules()
 
    reglas.to_csv("reglas_eclat.csv", index=False)
    itemsets.to_csv("itemsets_eclat.csv", index=False)