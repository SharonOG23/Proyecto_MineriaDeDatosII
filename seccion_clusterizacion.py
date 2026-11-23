# Sección "Clusterización" de la app: usa las clases del equipo (carpeta Clusterizacion/)
# Requisitos extra: pip install scikit-learn umap-learn
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Las clases hacen "from limpieza_datos import ...": se agregan eda/ y Clusterizacion/ a la ruta
RAIZ = Path(__file__).parent
for carpeta in (RAIZ / "eda", RAIZ / "Clusterizacion"):
    if str(carpeta) not in sys.path:
        sys.path.insert(0, str(carpeta))

from ui import tarjeta, AZUL, ROJO
from acp_clientes import AnalisisACP, preparar_clientes
from tsne_clientes import AnalisisTSNE
from lasso_ import AnalisisLasso
from Ridge import AnalisisRidge

try:
    from umap_clientes import AnalisisUMAP
except ImportError:          # falta instalar umap-learn
    AnalisisUMAP = None

SUBMENUS = ["Clusterización", "PCA · t-SNE · UMAP", "Lasso", "Regresión Ridge"]


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


def _resultado_clusters(modelo, tiempo, num):
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
    tarjeta("💡 Interpretación", f"El cluster <b>{mayor}</b> reúne a los clientes de mayor gasto promedio. "
            "Comparar las barras y el radar permite distinguir clientes ocasionales, frecuentes y mayoristas "
            "para diseñar campañas distintas a cada grupo.")


# ------------------------------------------------------------ Clusterización (K-Means)
def pagina_kmeans(csv):
    st.title("🧬 Clusterización (K-Means)")
    est, num = clientes(csv)
    tope = max(3, min(8, len(est) - 1))
    k = st.slider("Número de clusters (k)", 2, tope, min(3, tope))
    if st.button("▶ Ejecutar K-Means", key="run_km"):
        with st.spinner("Calculando codo y silueta..."):
            ks = list(range(2, tope + 1))
            ms = [KMeans(i, n_init=10, random_state=42).fit(est) for i in ks]
            st.session_state["km"] = dict(ks=ks, k=k, inercia=[m.inertia_ for m in ms],
                                          sil=[silhouette_score(est, m.labels_) for m in ms], labels=ms[k - 2].labels_)
    r = st.session_state.get("km")
    if not r:
        st.info("👆 Pulsa **Ejecutar K-Means**."); return
    mejor = r["ks"][r["sil"].index(max(r["sil"]))]
    a, b, c = st.columns(3)
    a.metric("Clientes", len(est)); b.metric("Silueta (k elegido)", f"{r['sil'][r['k'] - 2]:.3f}"); c.metric("Mejor k por silueta", mejor)
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.line(x=r["ks"], y=r["inercia"], markers=True, title="Método del codo",
                            labels=dict(x="k", y="Inercia"), color_discrete_sequence=[ROJO]))
    c2.plotly_chart(px.line(x=r["ks"], y=r["sil"], markers=True, title="Coeficiente de silueta",
                            labels=dict(x="k", y="Silueta"), color_discrete_sequence=[AZUL]))
    st.subheader("Perfil de cada cluster")
    perfil = num.assign(Cluster=r["labels"]).groupby("Cluster").mean().round(2)
    perfil.insert(0, "Clientes", pd.Series(r["labels"]).value_counts().sort_index())
    st.dataframe(perfil)


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
        if r: _resultado_clusters(*r, num)
        else: st.info("👆 Pulsa **Ejecutar**.")
    with t2:
        r = _ejecutar_modelo("tsne", lambda: AnalisisTSNE(est, num, n_clusters=k, perplexity=perp))
        if r: _resultado_clusters(*r, num)
        else: st.info("👆 Pulsa **Ejecutar**.")
    with t3:
        if AnalisisUMAP is None:
            st.error("Falta instalar UMAP: pip install umap-learn")
        else:
            r = _ejecutar_modelo("umap", lambda: AnalisisUMAP(est, num, n_clusters=k, n_neighbors=nn))
            if r: _resultado_clusters(*r, num)
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
    tarjeta("💡 Interpretación", f"Lasso eligió <b>{m.metricas['Variables usadas']}</b> variables para predecir <b>{m.objetivo}</b> "
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
        _resultado_clusters(*r, num)
        st.caption("Ridge se ajusta sobre el Gasto y se usan las 2 variables con mayor coeficiente para agrupar a los clientes.")
    else:
        st.info("👆 Pulsa **Ejecutar**.")


def pagina(sub, csv):
    {"Clusterización": pagina_kmeans, "PCA · t-SNE · UMAP": pagina_reduccion,
     "Lasso": pagina_lasso, "Regresión Ridge": pagina_ridge}[sub](csv)
