from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch
from mlxtend.frequent_patterns import apriori as apriori_mlxtend, association_rules
 
 
class Apriori:
    def __init__(self, df, min_support=0.03, min_confidence=0.5, max_len=2):
        self.df = df
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.max_len = max_len
        self.frequent_itemsets = None
        self.rules = None
 
    def ajustar(self):
        self.frequent_itemsets = apriori_mlxtend(
            self.df,
            min_support=self.min_support,
            use_colnames=True,
            max_len=self.max_len,
        )
        self.rules = association_rules(
            self.frequent_itemsets,
            metric="confidence",
            min_threshold=self.min_confidence,
        )
        return self
 
    def resumen(self):
        self._verificar()
        r = self.rules[
            ["antecedents", "consequents", "support", "confidence", "lift"]
        ].copy()
        r["antecedents"] = r["antecedents"].apply(lambda x: ", ".join(sorted(x)))
        r["consequents"] = r["consequents"].apply(lambda x: ", ".join(sorted(x)))
        return r.rename(columns={
            "antecedents": "Antecedente",
            "consequents": "Consecuente",
            "support": "Soporte",
            "confidence": "Confianza",
            "lift": "Elevación",
        })
 
    def graficar_dispersion(self):
        self._verificar()
        plt.figure(figsize=(8, 6))
        plt.scatter(
            self.rules["confidence"], self.rules["lift"], alpha=0.7, color="b"
        )
        plt.xlabel("Confidence")
        plt.ylabel("Lift")
        plt.title("Confidence vs Lift in Association Rules")
        plt.grid()
        plt.show()
 
    def graficar_red(self, top=10):
        self._verificar()
        reglas = self.rules.sort_values("lift", ascending=False).head(top)
        G = nx.DiGraph()
        edge_labels = {}
        for _, row in reglas.iterrows():
            origen = ", ".join(sorted(row["antecedents"]))
            destino = ", ".join(sorted(row["consequents"]))
            G.add_edge(origen, destino)
            edge_labels[(origen, destino)] = f"{row['confidence']:.2f}"
 
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=1.5, seed=42)
        nx.draw(
            G, pos, with_labels=True, node_color="lightblue",
            edge_color="gray", node_size=2500, font_size=7, arrows=True,
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        plt.title(f"Red de las {top} reglas con mayor elevación")
        plt.show()
 
    def graficar_barras(self, top=10, metrica="lift"):
        self._verificar()
        reglas = self.rules.sort_values(metrica, ascending=False).head(top).iloc[::-1]
        ant = [", ".join(sorted(x)) for x in reglas["antecedents"]]
        con = [", ".join(sorted(x)) for x in reglas["consequents"]]
        valores = reglas[metrica].values
 
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.barh(range(len(reglas)), valores, color="lightgray")
 
        for i, (a, c, v) in enumerate(zip(ant, con, valores)):
            ax.text(0, i, a + "  →  ", ha="right", va="center", color="red", fontsize=8)
            ax.text(v, i, "  " + c, ha="left", va="center", color="green", fontsize=8)
 
        ax.set_yticks([])
        ax.set_xlim(0, valores.max() * 1.8)
        ax.set_xlabel(metrica.capitalize())
        ax.set_title(f"Top {top} reglas por {metrica}")
        ax.grid(axis="x", alpha=0.3)
        plt.subplots_adjust(left=0.35)
 
        ax.legend(
            handles=[Patch(color="red", label="Antecedente"),
                     Patch(color="green", label="Consecuente")],
            loc="lower right",
        )
        plt.show()
 
    def _verificar(self):
        if self.rules is None:
            raise ValueError("Primero ejecuta .ajustar()")
 
 
# ---------- Datos ----------
ventas = pd.read_csv(Path(__file__).resolve().parent.parent / "processed" / "2mil_online_retail.csv")
 
# Limpieza
ventas = ventas.dropna(subset=["Description"])
ventas["Description"] = (
    ventas["Description"].str.strip().str.upper().str.replace(r"\s+", " ", regex=True)
)
ventas = ventas[~ventas["InvoiceNo"].astype(str).str.startswith("C")]
 
# Una fila por factura, una columna por producto (Verdadero/Falso)
df = pd.crosstab(ventas["InvoiceNo"], ventas["Description"]).gt(0)
 
# Solo productos que aparecen en al menos 2% de las facturas
df = df.loc[:, df.mean() >= 0.02]
 
print("Filas del CSV:", len(ventas))
print("Facturas:", df.shape[0], "| Productos:", df.shape[1])
 
# ---------- Modelo ----------
modelo = Apriori(df, min_support=0.03, min_confidence=0.5, max_len=2)
modelo.ajustar()
print("Reglas generadas:", len(modelo.rules))
 
# ---------- Resultados en terminal ----------
resultado = modelo.resumen().sort_values("Elevación", ascending=False)
print(resultado.head(20).to_string(index=False, float_format="%.3f"))
 
# ---------- Gráficos ----------
modelo.graficar_dispersion()
modelo.graficar_red(top=10)
modelo.graficar_barras(top=10) 