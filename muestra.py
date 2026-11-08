import pandas as pd
 
 
def crear_muestra(
    entrada="online_retail_limpio.csv",
    salida="2mil_online_retail.csv",
    n_filas=2000,
    columna_factura="InvoiceNo",
    por_facturas=True,
    semilla=42,
):
    df = pd.read_csv(entrada)
 
    if por_facturas:
        tamaños = df.groupby(columna_factura).size().sample(frac=1, random_state=semilla)
        elegidas = []
        total = 0
        for factura, tam in tamaños.items():
            if total + tam <= n_filas:
                elegidas.append(factura)
                total += tam
            if total == n_filas:
                break
        muestra = df[df[columna_factura].isin(elegidas)]
    else:
        muestra = df.sample(n=n_filas, random_state=semilla)
 
    muestra = muestra.sort_index().reset_index(drop=True)
    muestra.to_csv(salida, index=False)
 
    print(f"Filas originales:  {len(df)}")
    print(f"Filas en muestra:  {len(muestra)}")
    print(f"Facturas en muestra: {muestra[columna_factura].nunique()}")
    print(f"Archivo guardado:  {salida}")
    return muestra
 
 
if __name__ == "__main__":
    crear_muestra()
