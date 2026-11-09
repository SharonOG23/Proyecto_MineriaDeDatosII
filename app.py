# =====================================================================
# EXAMEN 2 - MINERÍA DE DATOS II
# App en Streamlit: CRISP-DM, EDA y Reglas de Asociación
#
# Ubicación: este archivo va en la carpeta raíz del proyecto
#   Proyecto_MineriaDeDatos/
#   ├── app.py                  <-- este archivo
#   ├── eda/limpieza_estadistica.py
#   ├── processed/2mil_online_retail.csv
#   └── reglas_asociacion/eclat.py, apriori.py, fp_growth.py
#
# Para ejecutar:  streamlit run app.py
# Requisitos:     pip install streamlit pandas plotly matplotlib
# =====================================================================

import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------
# 1. IMPORTACIÓN DE LAS CLASES DEL PROYECTO ---------------------------
# ---------------------------------------------------------------------
# Aquí se llaman las clases que hicieron en el equipo.
from reglas_asociacion.eclat import Eclat

# PENDIENTE: cuando sus compañeros entreguen los archivos, quiten el "#"
# de estas líneas y cambien el nombre de la clase si es distinto.
# from reglas_asociacion.apriori import Apriori
# from reglas_asociacion.fp_growth import FPGrowth
# from eda.limpieza_estadistica import LimpiezaEstadistica


# ---------------------------------------------------------------------
# 2. CONFIGURACIÓN ----------------------------------------------------
# ---------------------------------------------------------------------
# Aquí cambian los datos de la portada. El resto del código no se toca.
CONFIG = {
    "logo": "https://moria.aurens.com/organizations/497d3acf-35c0-4c90-8754-d5e71162119b/logos/3215d7-271.png",
    "csv": str(Path(__file__).parent / "processed" / "2mil_online_retail.csv"),
    "examen": "Examen 2",
    "materia": "Minería de Datos II",
    "profesor": "Nombre del profesor",
    "fecha_entrega": "DD de mes de 2026",
    "integrantes": ["Integrante 1", "Integrante 2", "Integrante 3"],
}

# Algoritmos disponibles. "None" significa que la clase aún no está lista.
# Cuando la tengan, cambian None por la clase (por ejemplo: "Apriori": Apriori).
ALGORITMOS = {
    "Apriori": None,
    "ECLAT": Eclat,
    "FP-Growth": None,
}

# Paleta de colores (se usa en el CSS y en las gráficas)
AZUL_OSCURO = "#1B2A49"
ROJO = "#C8102E"
DORADO = "#F2A900"
FONDO = "#F4F6FA"
COLORES = [ROJO, AZUL_OSCURO, DORADO, "#2A9D8F", "#6C757D"]

# Configuración de la página (título, ícono y ancho)
st.set_page_config(page_title="Examen 2 - Minería de Datos II", page_icon="📊", layout="wide")


# ---------------------------------------------------------------------
# 3. ESTILOS (CSS) ----------------------------------------------------
# ---------------------------------------------------------------------
# Streamlit permite meter CSS con st.markdown(..., unsafe_allow_html=True)
def aplicar_estilos():
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {FONDO}; }}

        /* Barra lateral */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {AZUL_OSCURO} 0%, #0F1A33 100%);
        }}
        [data-testid="stSidebar"] * {{ color: #FFFFFF; }}
        [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.25); }}

        /* Títulos del contenido principal */
        h1, h2, h3 {{ color: {AZUL_OSCURO}; }}

        /* Tarjeta de portada */
        .portada {{
            background: linear-gradient(135deg, {AZUL_OSCURO} 0%, #2E4A7D 100%);
            border-left: 10px solid {ROJO};
            border-radius: 18px;
            padding: 40px 50px;
            color: white;
            box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        }}
        .portada h1 {{ color: white; font-size: 3rem; margin: 0; }}
        .portada h3 {{ color: {DORADO}; margin: 4px 0 24px 0; font-weight: 500; }}
        .portada .campo {{ font-size: 1.1rem; margin: 6px 0; color: #E8ECF5; }}
        .portada .campo b {{ color: {DORADO}; }}
        .portada ul {{ margin: 4px 0 0 0; }}

        /* Tarjetas de información */
        .tarjeta {{
            background: white;
            border-radius: 14px;
            padding: 20px 24px;
            border-top: 5px solid {ROJO};
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            margin-bottom: 14px;
            color: #222;
        }}
        .tarjeta h4 {{ color: {AZUL_OSCURO}; margin-top: 0; }}
        .tarjeta ul {{ margin-bottom: 0; }}

        /* Tarjeta de "en construcción" */
        .pendiente {{
            background: white;
            border: 3px dashed {DORADO};
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            color: {AZUL_OSCURO};
        }}

        /* Métricas */
        [data-testid="stMetric"] {{
            background: white;
            border-radius: 12px;
            padding: 14px 18px;
            border-left: 5px solid {DORADO};
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        }}
        [data-testid="stMetricValue"] {{ color: {AZUL_OSCURO}; }}
        [data-testid="stMetricLabel"] p {{ color: #555; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# 4. FUNCIONES AUXILIARES ---------------------------------------------
# ---------------------------------------------------------------------
def tarjeta(titulo, contenido):
    # Dibuja una tarjeta blanca con título y texto (admite HTML)
    st.markdown(f'<div class="tarjeta"><h4>{titulo}</h4>{contenido}</div>', unsafe_allow_html=True)


def tabla(filas, columnas):
    # Muestra una tabla sencilla a partir de una lista de filas
    st.dataframe(pd.DataFrame(filas, columns=columnas), hide_index=True)


def pagina_pendiente(titulo, mensaje, codigo):
    # Espacio reservado para lo que aún no está listo
    st.title(titulo)
    st.markdown(
        f'<div class="pendiente"><h2>🚧 En construcción</h2><p>{mensaje}</p></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("**Para conectarlo cuando esté listo:**")
    st.code(codigo, language="python")


def texto_lista(lista):
    # Convierte ['A', 'B'] en "A, B" para mostrarlo en las tablas
    return ", ".join(lista)


# ---------------------------------------------------------------------
# 5. PÁGINA: INICIO (PORTADA) -----------------------------------------
# ---------------------------------------------------------------------
def pagina_inicio():
    integrantes = "".join(f"<li>{nombre}</li>" for nombre in CONFIG["integrantes"])
    st.markdown(
        f"""
        <div class="portada">
        <h1>{CONFIG['examen']}</h1>
        <h3>{CONFIG['materia']}</h3>
        <div class="campo"><b>👨‍🏫 Profesor: Ronald Córdoba Vega</b> {CONFIG['profesor']}</div>
        <div class="campo"><b>📅 Fecha de entrega: 10 - 11 - 2026</b> {CONFIG['fecha_entrega']}</div>
        <div class="campo"><b>👥 Integrantes: Sharon, Johel, Fabian, Steven, Marisol</b><ul>{integrantes}</ul></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.info("👈 Usa el menú de la izquierda para recorrer CRISP-DM, el EDA y las reglas de asociación.")


# ---------------------------------------------------------------------
# 6. PÁGINA: CRISP-DM (RESUMEN) ---------------------------------------
# ---------------------------------------------------------------------
# Resumen del documento CRISP-DM_Fases1-2_Online_Retail.md
def pagina_crisp():
    st.title("🧭 Metodología CRISP-DM")
    fase = st.radio(
        "Fase",
        ["1. Comprensión del negocio", "2. Comprensión de los datos"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if fase.startswith("1"):
        crisp_fase1()
    else:
        crisp_fase2()


def crisp_fase1():
    st.header("Fase 1: Comprensión del negocio")
    t1, t2, t3, t4 = st.tabs(["🏪 Contexto y problema", "🎯 Objetivos", "✅ Criterios de éxito", "⚠️ Restricciones"])

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Facturas (originales)", "25 900")
        c2.metric("Líneas de producto", "541 909")
        c3.metric("Productos vendidos", "3 791")
        c4.metric("Densidad de cesta", "0,69 %")

        col1, col2 = st.columns(2)
        with col1:
            tarjeta("🏪 Contexto del problema",
                    "<ul><li>Comercio en línea de <b>regalos y artículos decorativos</b> para el hogar.</li>"
                    "<li>Periodo: <b>1 dic 2010 – 9 dic 2011</b>.</li>"
                    "<li>Operación internacional (38 países), con <b>Reino Unido en el 91,4 %</b> de las filas.</li>"
                    "<li>Posible clientela mayorista: cestas de hasta 1 106 referencias.</li></ul>")
        with col2:
            tarjeta("❓ Problema de negocio",
                    "El comercio tiene muchas transacciones pero <b>no conoce de forma sistemática qué "
                    "productos se compran juntos</b>. Con una densidad de solo 0,69 % es imposible "
                    "detectarlo a simple vista.")

    with t2:
        st.subheader("Objetivos de negocio")
        tabla([
            ["ON-1", "Identificar combinaciones de productos para venta cruzada en el sitio web."],
            ["ON-2", "Proponer paquetes (bundles) con familias de producto que se compran juntas."],
            ["ON-3", "Distinguir patrones del mercado nacional frente al internacional."],
            ["ON-4", "Evaluar la estabilidad temporal de los patrones para planificar campañas."],
            ["ON-5", "Sentar bases para una segmentación posterior de clientes."],
        ], ["Código", "Objetivo"])

        st.subheader("Objetivos de minería de datos")
        tabla([
            ["OM-1", "Extraer conjuntos frecuentes con distintos soportes mínimos.", "Apriori, ECLAT y FP-Growth"],
            ["OM-2", "Generar reglas de asociación y evaluarlas.", "Soporte, confianza, lift, leverage, conviction"],
            ["OM-3", "Descubrir patrones con valor monetario.", "Conjuntos de alta utilidad"],
            ["OM-4", "Explorar patrones secuenciales entre compras de un mismo cliente.", "PrefixSpan / SPADE"],
            ["OM-5", "Segmentar facturas o clientes (complementario).", "Clustering (RFM, k-means)"],
        ], ["Código", "Objetivo técnico", "Técnica"])

    with t3:
        col1, col2 = st.columns(2)
        with col1:
            tarjeta("💼 Criterios del negocio",
                    "<ul><li><b>CN-1:</b> al menos 10 reglas con soporte ≥ 1 %, confianza ≥ 0,5 y lift ≥ 1,2 "
                    "que no sean simples variantes de color o diseño.</li>"
                    "<li><b>CN-2:</b> al menos 3 propuestas de paquete.</li>"
                    "<li><b>CN-3:</b> cada regla con descripción legible y lectura de negocio.</li></ul>")
        with col2:
            tarjeta("⛏️ Criterios de minería",
                    "<ul><li><b>CM-1:</b> los 3 algoritmos dan el mismo número de itemsets con el mismo soporte.</li>"
                    "<li><b>CM-2:</b> tiempo y memoria registrados para al menos 4 niveles de soporte.</li>"
                    "<li><b>CM-3:</b> validación temporal: ≥ 70 % de las reglas conserva lift > 1.</li>"
                    "<li><b>CM-4:</b> código y semillas versionados.</li></ul>")

    with t4:
        tabla([
            ["R1", "Un solo comercio y un solo periodo (≈ 12 meses)."],
            ["R2", "Diciembre de 2011 está incompleto (hasta el día 9)."],
            ["R3", "24,93 % de las filas no tiene CustomerID."],
            ["R4", "No hay taxonomía de productos, costos ni márgenes."],
            ["R5", "Los países distintos de Reino Unido tienen pocas facturas."],
        ], ["#", "Restricción"])
        st.caption("Supuesto principal: una factura equivale a una cesta de compra, y solo importa si el producto está o no en la factura.")


def crisp_fase2():
    st.header("Fase 2: Comprensión de los datos")
    t1, t2, t3, t4 = st.tabs(["📋 Datos", "🧹 Calidad y depuración", "📊 Exploración", "💡 Hallazgos"])

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registros", "541 909")
        c2.metric("Atributos", "8")
        c3.metric("Clientes", "4 372")
        c4.metric("Países", "38")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Descripción general")
            tabla([
                ["Archivo", "Online_Retail.xlsx (23,7 MB)"],
                ["Facturas distintas", "25 900"],
                ["Referencias (StockCode)", "4 070"],
                ["Descripciones distintas", "4 223"],
                ["Periodo", "2010-12-01 a 2011-12-09"],
            ], ["Característica", "Valor"])
        with col2:
            st.subheader("Atributos")
            tabla([
                ["InvoiceNo", "Identificador de la factura (prefijo C = cancelación)"],
                ["StockCode", "Código del producto"],
                ["Description", "Nombre del producto"],
                ["Quantity", "Unidades vendidas"],
                ["InvoiceDate", "Fecha y hora"],
                ["UnitPrice", "Precio unitario"],
                ["CustomerID", "Identificador del cliente"],
                ["Country", "País del cliente"],
            ], ["Atributo", "Descripción"])
        st.caption("Origen: coincide con el conjunto público Online Retail del repositorio UCI (por confirmar con el archivo).")

    with t2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Calidad inicial")
            tabla([
                ["Completitud", "CustomerID 24,93 % faltante; Description 0,27 %"],
                ["Unicidad", "5 268 filas duplicadas exactas (0,97 %)"],
                ["Validez", "2 515 precios en 0 y cantidades negativas"],
                ["Consistencia", "650 códigos con más de una descripción"],
                ["Atípicos", "Cantidad ±80 995 y precio hasta 38 970"],
            ], ["Dimensión", "Hallazgo"])
        with col2:
            st.subheader("Criterios de depuración")
            tarjeta("Una línea es válida si cumple todo",
                    "<ol><li><code>InvoiceNo</code> no empieza por C ni por A.</li>"
                    "<li><code>Quantity</code> > 0 y <code>UnitPrice</code> > 0.</li>"
                    "<li><code>StockCode</code> corresponde a un producto real.</li>"
                    "<li><code>Description</code> no es nula.</li></ol>")

        st.subheader("Resultado de la depuración")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Líneas válidas", "527 725")
        c2.metric("Facturas válidas", "19 773")
        c3.metric("Productos", "3 791")
        c4.metric("Clientes", "4 334")
        st.caption("Se perdió el 2,6 % de las líneas pero el 23,7 % de las facturas (cancelaciones y facturas sin líneas válidas).")

    with t3:
        col1, col2 = st.columns(2)
        with col1:
            productos = pd.DataFrame({
                "Producto": ["WHITE HANGING HEART T-LIGHT HOLDER", "JUMBO BAG RED RETROSPOT",
                             "REGENCY CAKESTAND 3 TIER", "PARTY BUNTING", "LUNCH BAG RED RETROSPOT",
                             "ASSORTED COLOUR BIRD ORNAMENT", "SMALL POPCORN HOLDER",
                             "SET OF 3 CAKE TINS PANTRY DESIGN", "PACK OF 72 RETROSPOT CAKE CASES",
                             "LUNCH BAG SUKI DESIGN"],
                "Facturas": [2265, 2089, 1988, 1685, 1565, 1455, 1392, 1385, 1320, 1284],
            }).iloc[::-1]
            fig = px.bar(productos, x="Facturas", y="Producto", orientation="h",
                         color_discrete_sequence=[ROJO], title="Top 10 productos por número de facturas")
            fig.update_layout(yaxis_title="")
            st.plotly_chart(fig)
        with col2:
            meses = pd.DataFrame({
                "Mes": ["2010-12", "2011-01", "2011-02", "2011-03", "2011-04", "2011-05", "2011-06",
                        "2011-07", "2011-08", "2011-09", "2011-10", "2011-11", "2011-12*"],
                "Líneas": [42481, 35147, 27707, 36748, 29916, 37030, 36874, 39518, 35284, 50226, 60742, 84711, 25525],
            })
            fig = px.line(meses, x="Mes", y="Líneas", markers=True,
                          color_discrete_sequence=[AZUL_OSCURO], title="Líneas de factura por mes")
            st.plotly_chart(fig)
            st.caption("*Diciembre de 2011 solo llega hasta el día 9.")

        st.subheader("Tamaño de las cestas (productos distintos por factura)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mediana", "15")
        c2.metric("Media", "26,2")
        c3.metric("Percentil 99", "218")
        c4.metric("Máximo", "1 106")

    with t4:
        col1, col2 = st.columns(2)
        with col1:
            tarjeta("🔍 Hallazgos principales",
                    "<ul><li>El dataset es <b>transaccional</b>: cada factura agrupa de 1 a 1 106 productos.</li>"
                    "<li><b>Alta dispersión</b> (0,69 %): se necesitan soportes bajos (1 % a 2 %).</li>"
                    "<li>El <b>14,8 %</b> de las facturas son cancelaciones.</li>"
                    "<li>Hay registros administrativos mezclados con ventas: la depuración es obligatoria.</li>"
                    "<li>Cestas muy heterogéneas: mediana 15, máximo 1 106.</li></ul>")
        with col2:
            tarjeta("📌 Más hallazgos",
                    "<ul><li>Reino Unido concentra el <b>90,5 %</b> de las facturas válidas.</li>"
                    "<li>Pico de ventas en <b>noviembre de 2011</b>.</li>"
                    "<li>Cola larga: el 12,6 % de las referencias genera el 50 % de las apariciones.</li>"
                    "<li>Hay compras extremas con cancelación inmediata que sesgan los análisis monetarios.</li></ul>")
        st.success("✅ Conclusión: el dataset es **adecuado para reglas de asociación** con Apriori, ECLAT y FP-Growth.")


# ---------------------------------------------------------------------
# 7. PÁGINA: EDA (PENDIENTE) ------------------------------------------
# ---------------------------------------------------------------------
def pagina_eda():
    pagina_pendiente(
        "🔎 Análisis Exploratorio de Datos (EDA)",
        "Esta sección mostrará lo que hace la clase de <b>eda/limpieza_estadistica.py</b>.",
        "# 1. Descomentar el import al inicio de app.py\n"
        "# from eda.limpieza_estadistica import LimpiezaEstadistica\n\n"
        "# 2. Aquí dentro de pagina_eda() se llama a la clase\n"
        "# eda = LimpiezaEstadistica(CONFIG['csv'])\n"
        "# st.dataframe(eda.resumen())",
    )


# ---------------------------------------------------------------------
# 8. PÁGINA: REGLAS DE ASOCIACIÓN -------------------------------------
# ---------------------------------------------------------------------
DESCRIPCION = {
    "Apriori": "Busca itemsets por niveles y **genera candidatos**. Poda los que tienen subconjuntos no frecuentes.",
    "ECLAT": "Usa el **formato vertical**: guarda para cada producto las facturas donde aparece y las **intersecta**.",
    "FP-Growth": "Construye un **árbol comprimido (FP-Tree)** y extrae los itemsets **sin generar candidatos**.",
}


# @st.cache_data guarda el resultado para no recalcular en cada clic
@st.cache_data
def ejecutar(nombre, ruta, min_support, min_confidence):
    # Llama a la clase del algoritmo elegido y devuelve sus resultados
    modelo = ALGORITMOS[nombre](min_support=min_support, min_confidence=min_confidence)
    modelo.load_csv(ruta, transaction_col="InvoiceNo", item_col="Description")

    inicio = time.perf_counter()
    modelo.fit()
    tiempo = time.perf_counter() - inicio

    reglas = modelo.generate_rules()
    itemsets = modelo.get_frequent_itemsets()
    return itemsets, reglas, tiempo, len(modelo.transactions)


def pagina_reglas(nombre):
    # Si la clase aún no está lista, se muestra el espacio reservado
    if ALGORITMOS[nombre] is None:
        archivo = "apriori" if nombre == "Apriori" else "fp_growth"
        clase = "Apriori" if nombre == "Apriori" else "FPGrowth"
        pagina_pendiente(
            f"🛒 Reglas de asociación: {nombre}",
            f"Esta sección mostrará la clase de <b>reglas_asociacion/{archivo}.py</b> cuando esté lista.",
            f"# 1. Descomentar el import al inicio de app.py\n"
            f"# from reglas_asociacion.{archivo} import {clase}\n\n"
            f"# 2. Cambiar None por la clase en el diccionario ALGORITMOS\n"
            f"# \"{nombre}\": {clase},",
        )
        return

    st.title(f"🛒 Reglas de asociación: {nombre}")
    st.markdown(DESCRIPCION[nombre])

    # Parámetros que el usuario puede mover
    col1, col2 = st.columns(2)
    min_support = col1.slider("Soporte mínimo (número de facturas)", 2, 10, 3)
    min_confidence = col2.slider("Confianza mínima", 0.1, 1.0, 0.5, 0.05)

    itemsets, reglas, tiempo, n_trans = ejecutar(nombre, CONFIG["csv"], min_support, min_confidence)

    # Métricas principales
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Transacciones", n_trans)
    m2.metric("Itemsets frecuentes", len(itemsets))
    m3.metric("Reglas", len(reglas))
    m4.metric("Tiempo", f"{tiempo * 1000:.1f} ms")

    tab1, tab2, tab3 = st.tabs(["📦 Itemsets frecuentes", "📜 Reglas", "📈 Gráficas"])

    with tab1:
        datos = itemsets.copy()
        datos["itemset"] = datos["itemset"].apply(texto_lista)
        st.dataframe(datos, hide_index=True)

    with tab2:
        if reglas.empty:
            st.warning("No hay reglas con estos parámetros. Prueba bajando la confianza o el soporte.")
        else:
            datos = reglas.copy()
            datos["antecedente"] = datos["antecedente"].apply(texto_lista)
            datos["consecuente"] = datos["consecuente"].apply(texto_lista)
            st.dataframe(datos, hide_index=True)

    with tab3:
        g1, g2 = st.columns(2)

        # Gráfica 1: combinaciones más frecuentes
        combos = itemsets[itemsets["tamaño"] >= 2].head(10).copy()
        if not combos.empty:
            combos["itemset"] = combos["itemset"].apply(lambda x: " + ".join(x)[:60])
            fig = px.bar(combos.iloc[::-1], x="soporte_abs", y="itemset", orientation="h",
                         color_discrete_sequence=[ROJO], title="Top combinaciones de productos",
                         labels={"soporte_abs": "Facturas", "itemset": ""})
            g1.plotly_chart(fig)

        # Gráfica 2: soporte vs confianza, coloreado por lift
        if not reglas.empty:
            fig = px.scatter(reglas, x="soporte", y="confianza", color="lift",
                             color_continuous_scale="Viridis", title="Soporte vs confianza")
            g2.plotly_chart(fig)

    # Comparación entre algoritmos (solo aparece cuando hay 2 o más listos)
    disponibles = [n for n, clase in ALGORITMOS.items() if clase is not None]
    if len(disponibles) > 1:
        with st.expander("⏱️ Comparar con los otros algoritmos"):
            filas = []
            for otro in disponibles:
                its, rgs, t, _ = ejecutar(otro, CONFIG["csv"], min_support, min_confidence)
                filas.append([otro, len(its), len(rgs), round(t * 1000, 2)])
            tabla(filas, ["Algoritmo", "Itemsets", "Reglas", "Tiempo (ms)"])
            st.caption("Los algoritmos deben dar los mismos itemsets; lo que cambia es el tiempo.")

    st.caption("Datos: muestra de 2 000 filas del dataset Online Retail.")


# ---------------------------------------------------------------------
# 9. MENÚ LATERAL Y NAVEGACIÓN ----------------------------------------
# ---------------------------------------------------------------------
def main():
    aplicar_estilos()

    with st.sidebar:
        st.markdown(
            f'<img src="{CONFIG["logo"]}" style="width:100%; border-radius:8px; background:white; padding:8px;">',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        seccion = st.radio(
            "Menú",
            ["🏠 Inicio", "🧭 CRISP-DM", "🔎 EDA", "🛒 Reglas de asociación"],
            label_visibility="collapsed",
        )

        # El submenú solo aparece cuando se elige Reglas de asociación
        algoritmo = None
        if seccion == "🛒 Reglas de asociación":
            st.markdown("**Algoritmo**")
            algoritmo = st.radio("Algoritmo", list(ALGORITMOS), label_visibility="collapsed")

        st.markdown("---")
        st.markdown("<h2 style='text-align:center; color:#F2A900;'>2026</h2>", unsafe_allow_html=True)

    # Se muestra la página que corresponde a la selección
    if seccion == "🏠 Inicio":
        pagina_inicio()
    elif seccion == "🧭 CRISP-DM":
        pagina_crisp()
    elif seccion == "🔎 EDA":
        pagina_eda()
    else:
        pagina_reglas(algoritmo)


main()
