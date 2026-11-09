import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules


class FPGrowth:

    def __init__(self, min_support=0.05, min_confidence=0.30):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.patrones = None
        self.reglas = None

    def ejecutar(self, transacciones):

        self.patrones = fpgrowth(
            transacciones.astype(bool),
            min_support=self.min_support,
            use_colnames=True
        )

        self.patrones = self.patrones.sort_values(
            by="support",
            ascending=False
        )

        return self.patrones

    def generar_reglas(self):

        if self.patrones is None:
            raise ValueError(
                "Primero debe ejecutar FP-Growth."
            )

        self.reglas = association_rules(
            self.patrones,
            metric="confidence",
            min_threshold=self.min_confidence
        )

        self.reglas = self.reglas.sort_values(
            by="lift",
            ascending=False
        )

        return self.reglas