# Sección "Clusterización" de la app: usa las clases del equipo (carpeta Clusterizacion/)
# Requisitos extra: pip install scikit-learn umap-learn
import sys
import time
from pathlib import Path
 
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
 
# Las clases hacen "from limpieza_datos import ...": se agregan eda/ y Clusterizacion/ a la ruta
RAIZ = Path(__file__).parent
for carpeta in (RAIZ, RAIZ / "eda", RAIZ / "Clusterizacion"):
    if str(carpeta) not in sys.path:
        sys.path.insert(0, str(carpeta))
 
from ui import tarjeta
from acp_clientes import AnalisisACP, preparar_clientes
from tsne_clientes import AnalisisTSNE
from clusterizacion_clientes import AnalisisClusters
 
try:
    from lasso_clientes import AnalisisLasso
except ImportError:          # nombre anterior del archivo
    from lasso_ import AnalisisLasso
from Ridge import AnalisisRidge
 
try:
    from umap_clientes import AnalisisUMAP
except ImportError:          # falta instalar umap-learn
    AnalisisUMAP = None
 
SUBMENUS = ["Clusterización", "PCA · t-SNE · UMAP", "Lasso", "Regresión Ridge", "Conclusión"]
 
# Interpretaciones del reporte (valen para la configuración por defecto de cada modelo)
TEXTOS = {'acp': '<p>PCA es una técnica lineal: busca los dos ejes que conservan la mayor variación de los datos. El '
        'resultado se parece mucho al K-Means anterior:</p><ul><li>Un grupo a la izquierda de <strong>gasto '
        'bajo</strong> (cerca de 130) y unos 150 días sin comprar.</li><li>Un grupo a la derecha de '
        '<strong>gasto alto</strong> (cerca de 670) y muchas unidades.</li><li>Un grupo pequeño de <strong>4 '
        'clientes</strong> arriba, aislados, con el gasto más alto (cerca de 760) y más '
        'facturas.</li></ul><p>Los dos primeros grupos se tocan en el centro, lo que confirma que no están '
        'muy separados.</p><p><strong>Conclusión:</strong> PCA cuenta la misma historia: muchos clientes '
        'pequeños, un grupo grande de compra grande y muy pocos clientes top.</p>',
 'km': '<p>elegimos <strong>k = 3</strong> porque la silueta es la más alta en ese punto '
       '(<strong>0,25</strong>). El codo baja de forma suave y no tiene un quiebre claro, por eso nos '
       'apoyamos en la silueta. Una silueta de 0,25 es baja: los grupos se parecen y se traslapan un poco, '
       'así que los resultados son orientativos. Los tres grupos son:</p><ul><li><strong>Cluster 0 (33 '
       'clientes), compras pequeñas:</strong> gasto bajo (cerca de 155) y unos 150 días sin '
       'comprar.</li><li><strong>Cluster 1 (50 clientes), compras grandes de una sola vez:</strong> gasto y '
       'ticket altos (cerca de 680) y muchas unidades, pero también unos 170 días sin '
       'comprar.</li><li><strong>Cluster 2 (3 clientes), los mejores clientes:</strong> el gasto más alto '
       '(cerca de 900), más facturas y más cantidad, y compraron hace poco (unos 45 '
       'días).</li></ul><p><strong>Conclusión:</strong> casi todos compran poco, o compran en grande una vez '
       'y no vuelven. Solo 3 clientes combinan alto gasto y compra reciente.</p>',
 'lasso': '<p><strong>Interpretación del modelo:</strong> Lasso predice el <strong>gasto</strong> de cada '
          'cliente con las demás variables. Los ejes del gráfico son <strong>Cantidad</strong> y '
          '<strong>Precio promedio</strong>, las variables que el modelo consideró más importantes. El R² de '
          'prueba fue <strong>0,94</strong>: el modelo explica cerca del 94 % de lo que gasta un cliente que '
          'no vio al entrenar. Es casi igual al de entrenamiento (0,96), así que <strong>no hay sobreajuste '
          'importante</strong>. Usó las 6 variables porque el alpha es muy pequeño (0,0014) y penaliza poco. '
          'Es lo esperable: quien compra más unidades gasta más.</p><p><strong>Interpretación de los '
          'grupos:</strong></p><ul><li><strong>Cluster 0 (39 clientes), compradores grandes:</strong> gasto '
          'cerca de 780 y mucha cantidad (cerca de 570).</li><li><strong>Cluster 1 (39 clientes), '
          'compradores medianos e inactivos:</strong> gasto cerca de 270 y unos 180 días sin '
          'comprar.</li><li><strong>Cluster 2 (8 clientes), pocas unidades de productos caros:</strong> '
          'precio promedio muy alto, cantidad baja y gasto bajo (cerca de '
          '82).</li></ul><p><strong>Conclusión:</strong> para explicar el gasto importa sobre todo '
          '<strong>cuántas unidades se compran</strong> y <strong>a qué precio</strong>. Como hay solo 86 '
          'clientes, el resultado es orientativo.</p>',
 'ridge': '<p>Ridge también predice el gasto, pero encoge las variables en lugar de eliminarlas (alpha = 1); '
          'sus ejes son las dos variables de mayor peso. Es la segmentación que mejor <strong>ordena a los '
          'clientes por valor</strong>, en tres niveles:</p><ul><li><strong>Cluster 0 (azul, grupo pequeño), '
          'alto valor:</strong> gasto muy alto (cerca de 1,450), mucha cantidad (cerca de 910) y el ticket '
          'más grande.</li><li><strong>Cluster 2 (verde, el grupo más grande), valor medio:</strong> gasto '
          'cerca de 330.</li><li><strong>Cluster 1 (naranja), valor bajo:</strong> gasto cerca de 110, con '
          'productos de precio promedio más alto.</li></ul><p>Los tres grupos llevan unos 5 meses sin '
          'comprar (entre 150 y 165 días), incluso los de mayor valor.</p><p><strong>Conclusión:</strong> '
          'Lasso selecciona y Ridge reduce, pero llegan a una idea parecida. Con Ridge se ve claro a quién '
          'cuidar primero: el grupo de alto valor lleva unos 165 días sin comprar, así que es la prioridad '
          'para reactivarlo.</p>',
 'tsne': '<p>aquí los grupos tienen tamaños más parejos y se separan mejor:</p><ul><li><strong>Cluster 2 '
         '(verde, el más grande), compras pequeñas e inactivos:</strong> gasto bajo (cerca de 175), poca '
         'cantidad y los más días sin comprar (unos 180). Sus productos tienen el precio promedio más '
         'alto.</li><li><strong>Cluster 1 (naranja), grandes compradores:</strong> el gasto más alto (cerca '
         'de 830) y mucha cantidad (cerca de 590) en una compra grande.</li><li><strong>Cluster 0 (azul, el '
         'más pequeño), clientes recurrentes:</strong> gasto medio (cerca de 470), el que más facturas tiene '
         'y el más activo (unos 65 días sin comprar).</li></ul><p><strong>Conclusión:</strong> t-SNE deja '
         'ver un grupo nuevo y valioso: clientes que <strong>vuelven a comprar</strong>. Recordatorio: en '
         't-SNE la distancia entre grupos lejanos no debe interpretarse literalmente.</p>',
 'umap': '<p>es el gráfico donde los tres grupos se ven más separados:</p><ul><li><strong>Cluster 0 (azul), '
         'compras pequeñas e inactivos:</strong> gasto bajo (cerca de 170) y los más días sin comprar (unos '
         '180).</li><li><strong>Cluster 1 (naranja, el más pequeño), grandes compradores recientes:</strong> '
         'gasto alto (cerca de 750), mucha cantidad y el grupo que compró más recientemente (unos 125 '
         'días).</li><li><strong>Cluster 2 (verde), alto gasto con más variedad:</strong> gasto alto (cerca '
         'de 630), más facturas y más productos distintos.</li></ul><p><strong>Conclusión:</strong> PCA, '
         't-SNE y UMAP cuentan lo mismo con distinto detalle: siempre hay un grupo de <strong>compra pequeña '
         'e inactivo</strong> y uno o dos grupos de <strong>gasto alto</strong>. Que tres técnicas distintas '
         'coincidan nos da confianza de que los segmentos son reales.</p>'}
 
# Un modelo usa su interpretación del reporte solo si se ejecutó con los parámetros por defecto
DEFECTO = {
    "km": lambda m: m.n_clusters == 3,
    "acp": lambda m: m.n_clusters == 3,
    "tsne": lambda m: m.n_clusters == 3 and m.perplexity == 10,
    "umap": lambda m: m.n_clusters == 3 and m.n_neighbors == 10,
    "lasso": lambda m: m.objetivo == "Gasto" and abs(m.test_size - 0.2) < 1e-9,
    "ridge": lambda m: m.n_clusters == 3 and m.alpha == 1,
}
 
 
def interpretacion(clave, modelo, generica):
    # Interpretación detallada (por defecto) o una general calculada con los resultados de esta ejecución
    if DEFECTO[clave](modelo):
        tarjeta("💡 Interpretación", TEXTOS[clave])
    else:
        tarjeta("💡 Interpretación", generica)
        st.caption("Cambiaste los parámetros: la interpretación detallada corresponde a la configuración por defecto "
                   "(k = 3, perplexity = 10, n_neighbors = 10, alpha = 1, Gasto y 20 % de prueba).")
 
 
@st.cache_data(show_spinner="Preparando datos por cliente...")
def clientes(csv):
    # Una fila por cliente (estandarizada y en valores reales)
    return preparar_clientes(csv)
 
 
def mostrar_grafico(funcion):
    # Las clases dibujan con matplotlib y llaman a plt.show(): se captura la figura para Streamlit
    plt.close("all")
    original = plt.show
    plt.show = lambda *a, **k: None
    try:
        funcion()
        st.pyplot(plt.gcf())
    finally:
        plt.show = original
        plt.close("all")
 
 
def _ejecutar_modelo(clave, crear):
    # Corre el modelo al pulsar el botón y lo guarda para no perderlo al interactuar
    if st.button("▶ Ejecutar", key=f"run_{clave}"):
        with st.spinner("Ejecutando..."):
            inicio = time.perf_counter()
            modelo = crear().ajustar()
            st.session_state[clave] = (modelo, time.perf_counter() - inicio)
    return st.session_state.get(clave)
 
 
def _resultado_clusters(modelo, tiempo, num, clave):
    tam = modelo.df["cluster"].value_counts().sort_index()
    a, b, c = st.columns(3)
    a.metric("Clientes", len(modelo.df)); b.metric("Clusters", len(tam)); c.metric("Tiempo", f"{tiempo:.2f} s")
    mostrar_grafico(modelo.graficar)
    st.subheader("Promedio real de cada variable por cluster")
    perfil = pd.DataFrame(modelo.centros, columns=num.columns).round(2)
    perfil.insert(0, "Clientes", tam.values)
    perfil.index.name = "Cluster"
    st.dataframe(perfil)
    mayor = perfil["Gasto"].idxmax()
    interpretacion(clave, modelo, f"El cluster <b>{mayor}</b> reúne a los clientes de mayor gasto promedio. "
            "Comparar las barras y el radar permite distinguir clientes ocasionales, frecuentes y mayoristas "
            "para diseñar campañas distintas a cada grupo.")
 
 
# ------------------------------------------------------------ Clusterización (K-Means)
def pagina_kmeans(csv):
    st.title("🧬 Clusterización de clientes (K-Means)")
    est, num = clientes(csv)
    tope = max(3, min(8, len(est) - 1))
    k = st.slider("Número de clusters (k)", 2, tope, min(3, tope))
    r = _ejecutar_modelo("km", lambda: AnalisisClusters(est, num, n_clusters=k))
    if not r:
        st.info("👆 Pulsa **Ejecutar** para correr K-Means."); return
    m, t = r
    a, b, c, d = st.columns(4)
    a.metric("Clientes", len(est)); b.metric("k", m.n_clusters)
    c.metric("Silueta", f"{m.silueta:.3f}"); d.metric("Tiempo", f"{t:.2f} s")
 
    mostrar_grafico(lambda: m.graficar(k_max=tope))
 
    tam = m.df["cluster"].value_counts().sort_index()
    perfil = pd.DataFrame(m.centros, columns=num.columns, index=[f"Cluster {i}" for i in range(m.n_clusters)])
    perfil["Clientes"] = tam.values
    perfil["% clientes"] = (tam.values / tam.sum() * 100).round(1)
    st.subheader("Perfil de cada cluster (promedios en escala original)")
    st.dataframe(perfil.round(2))
 
    st.subheader("Diferencia frente al promedio global (%)")
    dif = (perfil[num.columns] / num.mean() - 1) * 100
    st.dataframe(dif.style.format("{:+.0f}%").background_gradient(cmap="RdBu_r", axis=None, vmin=-100, vmax=100))
    mayor = perfil["Gasto"].idxmax()
    interpretacion("km", m, f"Con k = <b>{m.n_clusters}</b> la silueta es <b>{m.silueta:.3f}</b> (más cerca de 1, mejores grupos). "
            f"<b>{mayor}</b> reúne a los clientes de mayor gasto. Los valores positivos de la tabla de diferencias indican "
            "que el grupo está por encima del promedio en esa variable; sirve para nombrar cada segmento y definir acciones "
            "(fidelización, reactivación, ofertas para mayoristas).")
 
 
# ------------------------------------------------------------ PCA · t-SNE · UMAP
def pagina_reduccion(csv):
    st.title("🗺️ PCA · t-SNE · UMAP")
    est, num = clientes(csv)
    n = len(est)
    c1, c2, c3 = st.columns(3)
    k = c1.slider("Clusters (K-Means)", 2, 6, 3)
    perp = c2.slider("t-SNE: perplexity", 2, max(3, min(50, n - 1)), min(10, max(3, n - 1)))
    nn = c3.slider("UMAP: n_neighbors", 2, max(3, min(50, n - 1)), min(10, max(3, n - 1)))
 
    t1, t2, t3 = st.tabs(["ACP (PCA)", "t-SNE", "UMAP"])
    with t1:
        r = _ejecutar_modelo("acp", lambda: AnalisisACP(est, num, n_clusters=k))
        if r: _resultado_clusters(*r, num, "acp")
        else: st.info("👆 Pulsa **Ejecutar**.")
    with t2:
        r = _ejecutar_modelo("tsne", lambda: AnalisisTSNE(est, num, n_clusters=k, perplexity=perp))
        if r: _resultado_clusters(*r, num, "tsne")
        else: st.info("👆 Pulsa **Ejecutar**.")
    with t3:
        if AnalisisUMAP is None:
            st.error("Falta instalar UMAP: pip install umap-learn")
        else:
            r = _ejecutar_modelo("umap", lambda: AnalisisUMAP(est, num, n_clusters=k, n_neighbors=nn))
            if r: _resultado_clusters(*r, num, "umap")
            else: st.info("👆 Pulsa **Ejecutar**.")
 
 
# ------------------------------------------------------------ Lasso
def pagina_lasso(csv):
    st.title("✂️ Regresión Lasso (L1)")
    est, num = clientes(csv)
    c1, c2 = st.columns(2)
    objetivo = c1.selectbox("Variable a predecir", list(est.columns), index=list(est.columns).index("Gasto"))
    prueba = c2.slider("% de clientes para prueba", 10, 40, 20)
    r = _ejecutar_modelo("lasso", lambda: AnalisisLasso(est, num, objetivo=objetivo, test_size=prueba / 100))
    if not r:
        st.info("👆 Pulsa **Ejecutar**."); return
    m, t = r
    cols = st.columns(len(m.metricas))
    for col, (nombre, valor) in zip(cols, m.metricas.items()):
        col.metric(nombre, f"{valor:.4f}" if isinstance(valor, float) else valor)
    mostrar_grafico(m.graficar)
    interpretacion("lasso", m, f"Lasso eligió <b>{m.metricas['Variables usadas']}</b> variables para predecir <b>{m.objetivo}</b> "
            f"(el resto quedó con coeficiente 0). El R² de prueba fue <b>{m.metricas['R2 test']:.3f}</b> frente a "
            f"<b>{m.metricas['R2 train']:.3f}</b> en entrenamiento; si la diferencia es grande hay sobreajuste.")
 
 
# ------------------------------------------------------------ Ridge
def pagina_ridge(csv):
    st.title("🏔️ Regresión Lineal Ridge (L2)")
    est, num = clientes(csv)
    c1, c2 = st.columns(2)
    alpha = c1.select_slider("Alpha (penalización L2)", [0.01, 0.1, 0.5, 1, 5, 10, 50, 100], value=1)
    k = c2.slider("Clusters (K-Means)", 2, 6, 3)
    r = _ejecutar_modelo("ridge", lambda: AnalisisRidge(est, num, n_clusters=k, alpha=alpha))
    if r:
        _resultado_clusters(*r, num, "ridge")
        st.caption("Ridge se ajusta sobre el Gasto y se usan las 2 variables con mayor coeficiente para agrupar a los clientes.")
    else:
        st.info("👆 Pulsa **Ejecutar**.")

# ------------------------------------------------------------ Conclusión
def pagina_conclusion(csv):
    st.title("✅ Conclusión de la clusterización")
    c1, c2 = st.columns(2)
    with c1:
        tarjeta("🔍 Qué encontramos",
                "En todas las técnicas aparecen los mismos tipos de cliente: <b>compradores pequeños e inactivos</b>, "
                "<b>compradores grandes de una sola compra</b> y un <b>grupo pequeño de clientes de alto valor o recurrentes</b>.")
        tarjeta("🛠️ Qué hacer",
                "<ol><li><b>Reactivar</b> a los clientes inactivos, porque casi todos llevan unos 5 meses sin comprar.</li>"
                "<li><b>Fidelizar</b> a los recurrentes y a los de alto valor.</li>"
                "<li>Ofrecer <b>descuentos por volumen o paquetes</b> a los grandes compradores.</li></ol>")
    with c2:
        tarjeta("📏 Qué tan confiable es",
                "La silueta es baja (<b>0,25</b>) y solo hay <b>86 clientes</b> en la muestra, así que los patrones son orientativos. "
                "Que PCA, t-SNE y UMAP coincidan da confianza.")
        tarjeta("🔗 Unión con la primera parte",
                "Las reglas de asociación dicen <b>qué</b> productos se compran juntos y los grupos dicen <b>quién</b> los compra. "
                "Así se puede ofrecer cada paquete al tipo de cliente que más lo aprovecha.")
 
 
def pagina(sub, csv):
    {"Clusterización": pagina_kmeans, "PCA · t-SNE · UMAP": pagina_reduccion,
     "Lasso": pagina_lasso, "Regresión Ridge": pagina_ridge, "Conclusión": pagina_conclusion}[sub](csv) 