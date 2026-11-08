# muestra_datos.py
# Examen Parcial II - Minería de Datos II
#
# Saca del dataset YA LIMPIO la muestra de 2 000 filas (2mil_online_retail.csv)
# que usa el grupo para las reglas de asociación (Apriori, FP-Growth y Eclat).
#
# La muestra son 90 FACTURAS COMPLETAS, no filas sueltas: si se tomaran filas al azar,
# las facturas quedarían partidas y se perderían los productos que se compran juntos,
# que es justo lo que buscan las reglas.
#
# Estos son los números de factura de la muestra que el grupo ya está usando.
# Así, correr esto da el mismo archivo (mismas 2 000 filas, en el mismo orden).

import pandas as pd

FACTURAS_MUESTRA = [
    536837, 536841, 537257, 537423, 537794, 538000, 539038, 539572, 540098, 540968,
    543054, 543470, 545398, 545522, 545698, 546028, 547078, 547690, 548216, 548358,
    548496, 549196, 549926, 549978, 550008, 550465, 551305, 551623, 552167, 552990,
    553140, 553488, 554524, 554560, 556472, 557006, 557284, 557628, 557846, 558350,
    558574, 559357, 559993, 560247, 560248, 560695, 560754, 560917, 561114, 561206,
    562373, 562532, 562719, 562967, 563070, 563189, 564634, 564851, 565241, 565261,
    565806, 565835, 566248, 567941, 568207, 569008, 569483, 569555, 569583, 569672,
    569843, 569865, 570101, 571030, 572312, 572453, 572696, 572769, 573159, 574077,
    574258, 574348, 575170, 576382, 576603, 578059, 578623, 580074, 580460, 581586
]


def crear_muestra(datos):
    """Devuelve las filas de las facturas de la muestra, tomadas del dataset limpio.

    datos : dataset limpio (el que devuelve LimpiezaOnlineRetail.limpiar())
    """
    # InvoiceNo es texto en la limpieza (paso 1), por eso la lista se pasa a texto
    facturas = [str(f) for f in FACTURAS_MUESTRA]
    muestra = datos[datos["InvoiceNo"].astype(str).isin(facturas)]
    return muestra.reset_index(drop=True)


if __name__ == "__main__":
    # el CSV limpio se guarda en UTF-8 (no en latin-1), por eso no se pone encoding
    limpio = pd.read_csv("online_retail_limpio.csv", parse_dates=["InvoiceDate"])
    muestra = crear_muestra(limpio)
    muestra.to_csv("2mil_online_retail.csv", index=False)
    print("Filas:", len(muestra), "| Facturas:", muestra["InvoiceNo"].nunique())
