# Para ejecutar:  streamlit run app.py
# Requisitos:     pip install streamlit pandas plotly matplotlib mlxtend networkx openpyxl
# =====================================================================
 
import time
from pathlib import Path
 
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
 
# ---------------------------------------------------------------------
# 1. IMPORTACIÓN DE LAS CLASES DEL PROYECTO ---------------------------
# ---------------------------------------------------------------------
# Aquí se llaman las clases que hicieron en el equipo.
from eda.limpieza_datos import LimpiezaOnlineRetail
from eda.graficos_eda import GraficosEDA
from reglas_asociacion.apriori import Apriori
from reglas_asociacion.eclat import Eclat
from reglas_asociacion.fp_growth import FPGrowth
 
 
# ---------------------------------------------------------------------
# 2. CONFIGURACIÓN ----------------------------------------------------
# ---------------------------------------------------------------------
# Aquí cambian los datos de la portada. El resto del código no se toca.
CONFIG = {
    "logo": "https://moria.aurens.com/organizations/497d3acf-35c0-4c90-8754-d5e71162119b/logos/3215d7-271.png",
    "csv": str(Path(__file__).parent / "processed" / "2mil_online_retail.csv"),
    "excel": str(Path(__file__).parent / "eda" / "Online Retail.xlsx"),
    "examen": "Examen 2",
    "materia": "Minería de Datos II",
    "profesor": "Ronald Córdoba Vega",
    "fecha_entrega": "10 de noviembre de 2026",
    "integrantes": [
        "Johel Barquero Carvajal",
        "Sharon Obando Gómez",
        "Fabián Brenes Loría",
        "Steven Vindas Rivera",
        "Marisol Víquez Rivera",
    ],
}
 
# Algoritmos que aparecen en el submenú de Reglas de asociación
ALGORITMOS = ["Apriori", "ECLAT", "FP-Growth"]
 
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
        <div class="campo"><b>👨‍🏫 Profesor:</b> {CONFIG['profesor']}</div>
        <div class="campo"><b>📅 Fecha de entrega:</b> {CONFIG['fecha_entrega']}</div>
        <div class="campo"><b>👥 Integrantes:</b><ul>{integrantes}</ul></div>
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
# 7. INTERPRETACIONES Y GRÁFICOS DE MATPLOTLIB ------------------------
# ---------------------------------------------------------------------
# Textos de interpretación: son los mismos del notebook reporte_final.ipynb
INTERPRETACION = {
    "eda_mes": "Diciembre de 2011 baja porque los datos terminan el 9 de diciembre (mes incompleto), no porque las ventas caigan. El crecimiento fuerte empieza en septiembre y llega al máximo en noviembre (£1.14 millones).",
    "eda_dia": "No hay facturas los sábados en todo el dataset y el jueves es el día más fuerte (4003 facturas).",
    "eda_hora": "Casi todas las compras ocurren entre las 8 y las 17 horas, con el pico al mediodía (12:00, 3118 facturas).",
    "ap_tabla": "Esta tabla muestra las reglas de Apriori ordenadas por elevación. Todas tienen un lift muy superior a 1, lo que indica que esos productos se compran juntos mucho más de lo que ocurriría al azar. Casi todas son productos de la misma familia, como parasoles, marcos de fotos o botellas de agua caliente en distintos colores, así que los clientes compran colecciones completas. Esto serviría para proponer paquetes o recomendar el producto complementario al cliente.",
    "ap_dispersion": "En este gráfico cada punto es una regla de asociación, con su confianza en el eje horizontal y su lift en el vertical. Todas las reglas tienen un lift mayor que 1, así que todas indican asociaciones reales entre productos. Las más fuertes están arriba a la derecha, con confianza de 1 y lift de hasta 30. Los puntos aparecen en columnas porque la muestra es de solo 90 facturas y la confianza solo toma valores como 0,5, 0,75 o 1.",
    "ap_red_barras": "Estos dos gráficos muestran las diez reglas con mayor elevación. En las barras se ve que ocho llegan a 30 y dos a 22,5, lo que indica que esos productos se compran juntos muchísimo más de lo esperado por azar. La red muestra cómo se conectan: son pares de productos de la misma colección, como parasoles, marcos de fotos y botellas de agua caliente, casi todos con confianza de 1,00 en ambos sentidos. Esto significa que los clientes compran juegos completos, y el negocio podría ofrecerlos como paquetes o recomendar el producto complementario.",
    "ec_resumen": "La muestra contiene 90 facturas con 1,126 productos distintos. Con un soporte mínimo de 3 facturas, el algoritmo ECLAT encontró 318 itemsets frecuentes (productos solos y combinaciones que se compran juntos) y generó 370 reglas de asociación con confianza mínima de 0,5. Como la mayoría de los productos aparece en muy pocas facturas, los patrones son ilustrativos por el tamaño reducido de la muestra.",
    "ec_combos": "Esta salida muestra las combinaciones de productos que más se compran juntas según ECLAT. Las más frecuentes aparecen en 5 de las 90 facturas, como Party Bunting con Spotty Bunting o con Regency Cakestand. Se ven dos patrones: productos de una misma colección, como las bolsas Vintage Doily o los moldes para pastelitos, y productos de decoración de fiestas, donde Party Bunting aparece en cinco combinaciones. Esto le sirve al negocio para ubicar esos productos juntos o ofrecerlos como paquete.",
    "ec_reglas": "Cada regla tiene un antecedente, que es lo que el cliente ya compró, y un consecuente, que es lo que probablemente también compra. Por ejemplo, la fila 6 dice que si la factura incluye el Jam Making Set Printed y el Spotty Bunting, entonces también incluye el Jumbo Bag y el Lunch Bag de la colección Vintage Doily. La confianza de 1,0 indica que esto se cumplió en todas las facturas donde apareció el antecedente, y el lift de 30 indica que es mucho más probable que el azar. Para el negocio, el antecedente sería lo que el cliente tiene en el carrito y el consecuente lo que se le recomendaría agregar.",
    "ec_top_items": "Este gráfico muestra los diez productos que aparecen en más facturas. Los tres primeros, Party Bunting, Jam Making Set Printed y White Hanging Heart T-Light Holder, aparecen en 11 de las 90 facturas, cerca del 12 %. Ningún producto domina: la diferencia entre el primero y el décimo es de solo cuatro facturas, lo que indica que las ventas están muy repartidas entre muchos productos. Estos mismos productos aparecen luego en las combinaciones más frecuentes, y varios coinciden con los más comprados del dataset completo. Cabe aclarar que el gráfico cuenta en cuántas facturas aparece cada producto, no las unidades vendidas.",
    "ec_top_itemsets": "Este gráfico muestra las diez combinaciones de productos que más se compran juntas según ECLAT. Las tres primeras aparecen en 5 de las 90 facturas: Party Bunting con Spotty Bunting, Party Bunting con Regency Cakestand y las dos bolsas Vintage Doily. Las demás aparecen en 4. Se ven dos patrones: productos de una misma colección, como los moldes para pastelitos o las bolsas, y productos populares de decoración de fiestas, como el Party Bunting, que aparece en varias combinaciones. Casi la mitad de las facturas con Party Bunting también incluyen Spotty Bunting.",
    "ec_reglas_plot": "Este gráfico muestra las reglas de ECLAT con su soporte y su confianza, y el color indica el lift. Los puntos se agrupan en tres columnas porque con 90 facturas las reglas solo aparecen en 3, 4 o 5 facturas. Las reglas con más soporte, a la derecha, tienen lift más bajo porque involucran productos muy populares. Las más fuertes están a la izquierda y arriba, con confianza de 1 y lift alto. Hay muchas reglas con los mismos valores, así que se dibujan encimadas y se ven pocos puntos para las 370 reglas.",
    "fp_patrones": "Esta tabla muestra los patrones frecuentes que encontró FP-Growth, ordenados por soporte. Los primeros son productos individuales, porque un producto solo siempre aparece en más facturas que cualquier combinación que lo incluya. Los tres más frecuentes, White Hanging Heart T-Light Holder, Party Bunting y Jam Making Set Printed, aparecen en 11 de las 90 facturas, un 12,2 %. Estos resultados coinciden con los de ECLAT, que es lo esperable, porque los dos algoritmos encuentran los mismos conjuntos frecuentes con el mismo soporte mínimo.",
    "fp_reglas": "Esta tabla muestra las reglas de FP-Growth con mayor lift. Las quince primeras tienen confianza de 1 y lift de 30, es decir, siempre que apareció el antecedente apareció el consecuente, y esos productos se compran juntos 30 veces más de lo esperado por azar. Casi todas son productos de una misma colección, como los marcos de fotos, las botellas de agua caliente, los moldes para pastelitos o la línea Vintage Doily. Algunas reglas incluyen varios productos en el antecedente, por ejemplo Lunch Bag Black Skull y Lunch Bag Vintage Doily juntos predicen la Silver Stars Table Decoration con confianza de 1. Los resultados coinciden con los de ECLAT: mismas 370 reglas y mismas métricas."
}
 
 
def interpretacion(clave):
    # Muestra la interpretación en una tarjeta
    tarjeta("💡 Interpretación", INTERPRETACION[clave])
 
 
def mostrar_grafico(funcion, *args, **kwargs):
    # Las clases dibujan con matplotlib y llaman a plt.show().
    # Aquí se ejecuta el método y se manda la figura a Streamlit.
    plt.close("all")
    mostrar_original = plt.show
    plt.show = lambda *a, **k: None   # en Streamlit no hace falta plt.show()
    try:
        funcion(*args, **kwargs)
        st.pyplot(plt.gcf())
    finally:
        plt.show = mostrar_original
        plt.close("all")
 
 
# ---------------------------------------------------------------------
# 8. PÁGINA: EDA ------------------------------------------------------
# ---------------------------------------------------------------------
# @st.cache_resource guarda el resultado: el Excel solo se limpia la primera vez
@st.cache_resource(show_spinner="Cargando y limpiando el Excel (la primera vez puede tardar uno o dos minutos)...")
def cargar_eda():
    limpieza = LimpiezaOnlineRetail(CONFIG["excel"])
    datos = limpieza.cargar()
    forma_original = datos.shape            # se guarda antes de limpiar
    datos_limpios = limpieza.limpiar()
    return limpieza, forma_original, datos_limpios
 
 
def pagina_eda():
    st.title("🔎 Análisis Exploratorio de Datos (EDA)")
 
    try:
        limpieza, forma_original, datos_limpios = cargar_eda()
    except (FileNotFoundError, ImportError) as error:
        st.error(f"No se pudo cargar el archivo de datos del EDA: {error}")
        st.caption("Revisa que exista eda/Online Retail.xlsx y que esté instalado openpyxl (pip install openpyxl).")
        return
 
    graficos = GraficosEDA(datos_limpios)   # Aquí se llama a la clase de gráficos
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Filas originales", f"{forma_original[0]:,}")
    c2.metric("Filas después de limpiar", f"{datos_limpios.shape[0]:,}")
    c3.metric("Columnas (con las nuevas)", datos_limpios.shape[1])
 
    tab1, tab2 = st.tabs(["🧹 Limpieza de datos", "📊 Gráficos"])
 
    with tab1:
        st.subheader("Filas eliminadas en cada paso")
        st.dataframe(limpieza.resumen(), hide_index=True)
        st.subheader("Datos ya limpios")
        st.dataframe(datos_limpios.head())
 
    with tab2:
        st.subheader("Países con más ventas")
        mostrar_grafico(graficos.ventas_por_pais)
 
        st.subheader("Ventas por mes")
        mostrar_grafico(graficos.ventas_por_mes)
        interpretacion("eda_mes")
 
        st.subheader("Facturas por día de la semana")
        mostrar_grafico(graficos.facturas_por_dia)
        interpretacion("eda_dia")
 
        st.subheader("Facturas por hora")
        mostrar_grafico(graficos.facturas_por_hora)
        interpretacion("eda_hora")
 
        st.subheader("Productos más vendidos (en cuántas facturas aparece cada uno)")
        top = graficos.tabla_top_productos().reset_index()
        top.columns = ["Producto", "Facturas"]
        st.dataframe(top, hide_index=True)
 
 
# ---------------------------------------------------------------------
# 9. PÁGINA: REGLAS DE ASOCIACIÓN -------------------------------------
# ---------------------------------------------------------------------
DESCRIPCION = {
    "Apriori": "Busca itemsets por niveles y **genera candidatos**. Poda los que tienen subconjuntos no frecuentes.",
    "ECLAT": "Usa el **formato vertical**: guarda para cada producto las facturas donde aparece y las **intersecta**.",
    "FP-Growth": "Construye un **árbol comprimido (FP-Tree)** y extrae los itemsets **sin generar candidatos**.",
}
 
 
def metricas(valores):
    # Dibuja una fila de métricas: valores = [(titulo, valor), ...]
    columnas = st.columns(len(valores))
    for columna, (titulo, valor) in zip(columnas, valores):
        columna.metric(titulo, valor)
 
 
# ---- Preparación de datos (igual que en el notebook) ----
@st.cache_data
def tabla_binaria():
    # Una fila por factura y una columna por producto (Verdadero/Falso)
    ventas = pd.read_csv(CONFIG["csv"])
    ventas = ventas.dropna(subset=["Description"])
    ventas["Description"] = (
        ventas["Description"].str.strip().str.upper().str.replace(r"\s+", " ", regex=True)
    )
    ventas = ventas[~ventas["InvoiceNo"].astype(str).str.startswith("C")]
    df = pd.crosstab(ventas["InvoiceNo"], ventas["Description"]).gt(0)
    df = df.loc[:, df.mean() >= 0.02]      # solo productos en al menos el 2 % de las facturas
    return df
 
 
# ---- Ejecución de los tres modelos (se guardan para no repetir el cálculo) ----
@st.cache_resource
def correr_apriori():
    df = tabla_binaria()
    modelo = Apriori(df, min_support=0.03, min_confidence=0.5, max_len=2)
    inicio = time.perf_counter()
    modelo.ajustar()
    return modelo, df, time.perf_counter() - inicio
 
 
@st.cache_resource
def correr_eclat():
    modelo = Eclat(min_support=3, min_confidence=0.5)
    modelo.load_csv(CONFIG["csv"], transaction_col="InvoiceNo", item_col="Description")
    inicio = time.perf_counter()
    modelo.fit()
    tiempo = time.perf_counter() - inicio
    reglas = modelo.generate_rules()
    return modelo, reglas, tiempo
 
 
@st.cache_resource
def correr_fp_growth():
    df = tabla_binaria()
    modelo = FPGrowth(min_support=0.03, min_confidence=0.5)
    inicio = time.perf_counter()
    patrones = modelo.ejecutar(df)
    tiempo = time.perf_counter() - inicio
    reglas = modelo.generar_reglas()
    return modelo, patrones, reglas, tiempo, df
 
 
# ---- Apriori ----
def pagina_apriori():
    st.title("🛒 Reglas de asociación: Apriori")
    st.markdown(DESCRIPCION["Apriori"])
 
    modelo, df, tiempo = correr_apriori()
    metricas([
        ("Facturas", df.shape[0]),
        ("Productos", df.shape[1]),
        ("Reglas generadas", len(modelo.rules)),
        ("Tiempo", f"{tiempo * 1000:.1f} ms"),
    ])
    st.caption("Parámetros: soporte mínimo 0,03 · confianza mínima 0,5 · máximo 2 productos por regla (max_len=2) "
               "· solo productos que aparecen en al menos el 2 % de las facturas.")
 
    tab1, tab2 = st.tabs(["📜 Reglas", "📈 Gráficas"])
 
    with tab1:
        st.subheader("Top 20 reglas ordenadas por elevación")
        resultado = modelo.resumen().sort_values("Elevación", ascending=False)
        st.dataframe(resultado.head(20))
        interpretacion("ap_tabla")
 
    with tab2:
        st.subheader("Confianza vs elevación")
        mostrar_grafico(modelo.graficar_dispersion)
        interpretacion("ap_dispersion")
 
        st.subheader("Red de las 10 reglas con mayor elevación")
        mostrar_grafico(modelo.graficar_red, top=10)
 
        st.subheader("Top 10 reglas por elevación (barras)")
        mostrar_grafico(modelo.graficar_barras, top=10)
        interpretacion("ap_red_barras")
 
 
# ---- ECLAT ----
def pagina_eclat():
    st.title("🛒 Reglas de asociación: ECLAT")
    st.markdown(DESCRIPCION["ECLAT"])
 
    modelo, reglas, tiempo = correr_eclat()
    metricas([
        ("Transacciones", len(modelo.transactions)),
        ("Itemsets frecuentes", len(modelo.frequent_itemsets)),
        ("Reglas generadas", len(modelo.rules)),
        ("Tiempo", f"{tiempo * 1000:.1f} ms"),
    ])
    st.caption(f"Parámetros: soporte mínimo {modelo.min_support} facturas · confianza mínima {modelo.min_confidence} "
               f"· productos distintos: {len(modelo.item_tidset)}")
    interpretacion("ec_resumen")
 
    tab1, tab2, tab3 = st.tabs(["📦 Combinaciones frecuentes", "📜 Reglas", "📈 Gráficas"])
 
    with tab1:
        st.subheader("Combinaciones de productos que más se compran juntas")
        combos = [(sorted(k), v) for k, v in modelo.frequent_itemsets.items() if len(k) >= 2]
        top = sorted(combos, key=lambda x: -x[1])[:15]
        tabla_combos = pd.DataFrame({
            "Facturas": [v for _, v in top],
            "Combinación": [" + ".join(items) for items, _ in top],
        })
        st.dataframe(tabla_combos, hide_index=True)
        interpretacion("ec_combos")
 
    with tab2:
        st.subheader("Primeras 15 reglas de asociación")
        datos = reglas.head(15).copy()
        datos["antecedente"] = datos["antecedente"].apply(texto_lista)
        datos["consecuente"] = datos["consecuente"].apply(texto_lista)
        st.dataframe(datos)
        interpretacion("ec_reglas")
 
    with tab3:
        st.subheader("Top 10 productos más vendidos")
        mostrar_grafico(modelo.plot_top_items)
        interpretacion("ec_top_items")
 
        st.subheader("Top 10 combinaciones de productos más frecuentes")
        mostrar_grafico(modelo.plot_top_itemsets)
        interpretacion("ec_top_itemsets")
 
        st.subheader("Reglas de asociación: soporte vs confianza")
        mostrar_grafico(modelo.plot_rules)
        interpretacion("ec_reglas_plot")
 
 
# ---- FP-Growth ----
def pagina_fp_growth():
    st.title("🛒 Reglas de asociación: FP-Growth")
    st.markdown(DESCRIPCION["FP-Growth"])
 
    modelo, patrones, reglas, tiempo, df = correr_fp_growth()
    metricas([
        ("Facturas", df.shape[0]),
        ("Patrones frecuentes", len(patrones)),
        ("Reglas generadas", len(reglas)),
        ("Tiempo", f"{tiempo * 1000:.1f} ms"),
    ])
    st.caption("Parámetros: soporte mínimo 0,03 · confianza mínima 0,5")
 
    tab1, tab2 = st.tabs(["📦 Patrones frecuentes", "📜 Reglas"])
 
    with tab1:
        st.subheader("Los 15 patrones más frecuentes")
        datos = patrones.head(15).copy()
        datos["itemsets"] = datos["itemsets"].apply(lambda x: ", ".join(sorted(x)))
        st.dataframe(datos)
        interpretacion("fp_patrones")
 
    with tab2:
        st.subheader("Primeras 15 reglas ordenadas por elevación")
        datos = reglas[["antecedents", "consequents", "support", "confidence", "lift"]].copy()
        datos["antecedents"] = datos["antecedents"].apply(lambda x: ", ".join(sorted(x)))
        datos["consequents"] = datos["consequents"].apply(lambda x: ", ".join(sorted(x)))
        st.dataframe(datos.head(15))
        interpretacion("fp_reglas")
 
 
# ---- Comparación de los tres algoritmos ----
def comparar_algoritmos():
    with st.expander("⏱️ Comparar los tres algoritmos"):
        apriori, _, t_apriori = correr_apriori()
        eclat, reglas_eclat, t_eclat = correr_eclat()
        _, patrones, reglas_fp, t_fp, _ = correr_fp_growth()
        filas = [
            ["Apriori", len(apriori.frequent_itemsets), len(apriori.rules), round(t_apriori * 1000, 2)],
            ["ECLAT", len(eclat.frequent_itemsets), len(reglas_eclat), round(t_eclat * 1000, 2)],
            ["FP-Growth", len(patrones), len(reglas_fp), round(t_fp * 1000, 2)],
        ]
        tabla(filas, ["Algoritmo", "Itemsets", "Reglas", "Tiempo (ms)"])
        st.caption("ECLAT y FP-Growth dan los mismos resultados; lo que cambia es el tiempo. "
                   "Apriori da menos porque se limitó a reglas de 2 productos (max_len=2).")
 
 
def pagina_reglas(nombre):
    if nombre == "Apriori":
        pagina_apriori()
    elif nombre == "ECLAT":
        pagina_eclat()
    else:
        pagina_fp_growth()
 
    comparar_algoritmos()
    st.caption("Datos: muestra de 2 000 filas del dataset Online Retail.")
 
 
# ---------------------------------------------------------------------
# 10. MENÚ LATERAL Y NAVEGACIÓN ----------------------------------------
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