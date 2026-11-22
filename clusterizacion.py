# Sección "Clusterización": K-Means, PCA/t-SNE/UMAP, Lasso y Ridge (todo ejecutable en vivo)
# Requisitos extra: pip install scikit-learn umap-learn
import time
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import Lasso, LassoCV, LinearRegression, Ridge, RidgeCV
from sklearn.manifold import TSNE
from sklearn.metrics import mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from ui import AZUL, ROJO, DORADO, tarjeta

FEATS = ["Lineas", "Productos", "Unidades", "Monto", "PrecioMedio"]
COLORES = [ROJO, AZUL, DORADO, "#2A9D8F", "#6C757D", "#8E44AD", "#E67E22", "#16A085"]
SUBMENUS = ["Clusterización", "PCA · t-SNE · UMAP", "Lasso", "Regresión Ridge"]


def _estilo(fig):
    fig.update_layout(font=dict(color=AZUL, size=14), paper_bgcolor="white", plot_bgcolor="white",
                      title_font=dict(size=18, color=AZUL))
    return fig


@st.cache_data
def facturas(csv):
    # Una fila por factura con variables numéricas
    v = pd.read_csv(csv).dropna(subset=["Description"])
    v = v[~v["InvoiceNo"].astype(str).str.startswith("C")]
    v = v[(v["Quantity"] > 0) & (v["UnitPrice"] > 0)].copy()
    v["Monto"] = v["Quantity"] * v["UnitPrice"]
    return v.groupby("InvoiceNo").agg(Lineas=("StockCode", "count"), Productos=("StockCode", "nunique"),
                                      Unidades=("Quantity", "sum"), Monto=("Monto", "sum"),
                                      PrecioMedio=("UnitPrice", "mean"))


def _escalar(f, cols):
    return StandardScaler().fit_transform(np.log1p(f[cols]))   # log1p porque las variables son muy sesgadas


# ---------------------------------------------------------------- Clusterización
def pagina_kmeans(csv):
    st.title("🧬 Clusterización (K-Means)")
    tarjeta("¿Qué hacemos aquí?",
            "Agrupamos las <b>facturas</b> según su tamaño y valor (líneas, productos distintos, unidades, monto y precio medio). "
            "Las variables se transforman con <code>log1p</code> y se estandarizan. Cambia los parámetros y pulsa "
            "<b>Ejecutar</b> para correr el modelo en vivo.")
    f = facturas(csv)
    c1, c2 = st.columns([2, 1])
    cols = c1.multiselect("Variables a usar", FEATS, default=FEATS)
    k = c2.slider("Número de clusters (k)", 2, 8, 3)
    if len(cols) < 2:
        st.warning("Selecciona al menos 2 variables."); return

    if st.button("▶ Ejecutar K-Means", key="run_km"):
        with st.spinner("Calculando codo, silueta y clusters..."):
            X = _escalar(f, cols)
            ks = list(range(2, 9))
            ms = [KMeans(n_clusters=i, n_init=10, random_state=42).fit(X) for i in ks]
            sil = [silhouette_score(X, m.labels_) for m in ms]
            m = ms[k - 2]
            st.session_state["km"] = dict(cols=cols, k=k, ks=ks, inercia=[x.inertia_ for x in ms], sil=sil,
                                          labels=m.labels_, coords=PCA(2, random_state=42).fit_transform(X))
    r = st.session_state.get("km")
    if not r:
        st.info("👆 Pulsa **Ejecutar K-Means** para ver los resultados."); return

    lab = pd.Series(r["labels"] + 1, index=f.index).astype(str)
    mejor = r["ks"][int(np.argmax(r["sil"]))]
    a, b, c, d = st.columns(4)
    a.metric("Facturas", len(f)); b.metric("k elegido", r["k"])
    c.metric("Silueta (k elegido)", f"{r['sil'][r['k'] - 2]:.3f}"); d.metric("Mejor k por silueta", mejor)

    t1, t2, t3 = st.tabs(["📉 Codo y silueta", "🗺️ Clusters (PCA 2D)", "📋 Perfil de cada cluster"])
    with t1:
        col1, col2 = st.columns(2)
        col1.plotly_chart(_estilo(px.line(x=r["ks"], y=r["inercia"], markers=True, title="Método del codo",
                          labels=dict(x="k", y="Inercia"), color_discrete_sequence=[ROJO])))
        col2.plotly_chart(_estilo(px.line(x=r["ks"], y=r["sil"], markers=True, title="Coeficiente de silueta",
                          labels=dict(x="k", y="Silueta"), color_discrete_sequence=[AZUL])))
        tarjeta("💡 Interpretación", f"El codo muestra dónde la inercia deja de bajar rápido, y la silueta mide qué tan separados "
                f"están los grupos (más cerca de 1 es mejor). Según la silueta el mejor k es <b>{mejor}</b>; "
                f"el seleccionado es <b>{r['k']}</b> con silueta de <b>{r['sil'][r['k'] - 2]:.3f}</b>.")
    with t2:
        dfp = pd.DataFrame(r["coords"], columns=["PC1", "PC2"], index=f.index).assign(Cluster=lab, Monto=f["Monto"].round(2))
        st.plotly_chart(_estilo(px.scatter(dfp, x="PC1", y="PC2", color="Cluster", hover_data=["Monto"],
                        color_discrete_sequence=COLORES, title="Facturas agrupadas (proyección PCA)")))
    with t3:
        perfil = f[r["cols"]].assign(Cluster=lab).groupby("Cluster").mean().round(2)
        perfil["Facturas"] = lab.value_counts().sort_index()
        st.dataframe(perfil)
        g = perfil["Monto"].idxmax() if "Monto" in perfil else perfil.index[0]
        tarjeta("💡 Interpretación", f"El cluster <b>{g}</b> agrupa las facturas de mayor valor. Comparar las medias de cada "
                "cluster permite distinguir compras pequeñas, medianas y mayoristas, y diseñar ofertas distintas para cada grupo.")


# ---------------------------------------------------------------- PCA / t-SNE / UMAP
def pagina_reduccion(csv):
    st.title("🗺️ PCA · t-SNE · UMAP")
    tarjeta("Reducción de dimensionalidad",
            "<ul><li><b>PCA:</b> proyección lineal que conserva la mayor varianza.</li>"
            "<li><b>t-SNE:</b> técnica no lineal que preserva vecindarios locales.</li>"
            "<li><b>UMAP:</b> no lineal, más rápida que t-SNE y conserva mejor la estructura global.</li></ul>")
    f = facturas(csv)
    if len(f) < 10:
        st.warning("Hay muy pocas facturas para reducir dimensionalidad."); return
    metodos = st.multiselect("Métodos a ejecutar", ["PCA", "t-SNE", "UMAP"], default=["PCA", "t-SNE", "UMAP"])
    c1, c2, c3, c4 = st.columns(4)
    k = c1.slider("Clusters (solo para colorear)", 2, 8, 3)
    perp = c2.slider("t-SNE: perplexity", 2, max(3, min(50, len(f) - 2)), min(15, max(3, len(f) // 4)))
    nn = c3.slider("UMAP: n_neighbors", 2, max(3, min(50, len(f) - 1)), min(15, max(3, len(f) // 4)))
    md = c4.slider("UMAP: min_dist", 0.0, 0.9, 0.1, 0.05)

    if st.button("▶ Ejecutar reducción", key="run_red") and metodos:
        X = _escalar(f, FEATS)
        lab = pd.Series(KMeans(k, n_init=10, random_state=42).fit_predict(X) + 1, index=f.index).astype(str)
        res = {}
        for m in metodos:
            with st.spinner(f"Ejecutando {m}..."):
                t = time.perf_counter()
                try:
                    if m == "PCA":
                        p = PCA(2, random_state=42); Z = p.fit_transform(X); extra = f"Varianza explicada: {p.explained_variance_ratio_.sum():.1%}"
                    elif m == "t-SNE":
                        Z = TSNE(2, perplexity=perp, init="pca", random_state=42).fit_transform(X); extra = f"perplexity = {perp}"
                    else:
                        import umap
                        Z = umap.UMAP(n_components=2, n_neighbors=nn, min_dist=md, random_state=42).fit_transform(X)
                        extra = f"n_neighbors = {nn}, min_dist = {md}"
                except ImportError:
                    st.error("Falta instalar UMAP: pip install umap-learn"); continue
                res[m] = (pd.DataFrame(Z, columns=["Dim 1", "Dim 2"], index=f.index).assign(Cluster=lab), time.perf_counter() - t, extra)
        st.session_state["red"] = res

    res = st.session_state.get("red")
    if not res:
        st.info("👆 Elige los métodos y pulsa **Ejecutar reducción**."); return
    cols = st.columns(len(res))
    for col, (m, (d, t, extra)) in zip(cols, res.items()):
        col.plotly_chart(_estilo(px.scatter(d, x="Dim 1", y="Dim 2", color="Cluster", color_discrete_sequence=COLORES,
                         title=f"{m} ({t:.2f} s)")))
        col.caption(extra)
    tarjeta("💡 Interpretación", "Si los colores (clusters de K-Means) aparecen agrupados y separados en el plano, la estructura "
            "encontrada es consistente. PCA suele mostrar los grupos más mezclados por ser lineal, mientras que t-SNE y UMAP "
            "separan mejor los vecindarios. Recuerda que en t-SNE y UMAP las distancias entre grupos lejanos no deben interpretarse literalmente.")


# ---------------------------------------------------------------- Lasso y Ridge
def pagina_regresion(nombre, csv, tabla_binaria):
    es_lasso = nombre == "Lasso"
    st.title("✂️ Regresión Lasso (L1)" if es_lasso else "🏔️ Regresión Lineal Ridge (L2)")
    tarjeta("¿Qué modelamos?",
            "Predecimos el <b>monto (log) de cada factura</b> a partir de los productos que contiene (presencia 0/1). " +
            ("<b>Lasso</b> penaliza con L1: lleva a cero los coeficientes poco útiles y <b>selecciona productos</b>."
             if es_lasso else "<b>Ridge</b> penaliza con L2: <b>encoge</b> los coeficientes y controla el sobreajuste cuando hay muchas variables correlacionadas."))
    df, fac = tabla_binaria(), facturas(csv)
    idx = df.index.intersection(fac.index)
    X, y = df.loc[idx].astype(int), np.log1p(fac.loc[idx, "Monto"])
    if len(idx) < 20:
        st.warning("Hay muy pocas facturas para entrenar el modelo."); return

    alphas = [0.001, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
    c1, c2, c3 = st.columns(3)
    alpha = c1.select_slider("Alpha (fuerza de la penalización)", alphas, value=0.1 if es_lasso else 10)
    prueba = c2.slider("% de datos para prueba", 10, 40, 25)
    auto = c3.checkbox("Elegir alpha por validación cruzada")

    if st.button(f"▶ Entrenar {nombre}", key=f"run_{nombre}"):
        with st.spinner("Entrenando..."):
            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=prueba / 100, random_state=42)
            sc = StandardScaler().fit(Xtr); A, B = sc.transform(Xtr), sc.transform(Xte)
            a = alpha
            if auto:
                cv = LassoCV(alphas=np.logspace(-3, 1, 30), cv=5, random_state=42, max_iter=20000) if es_lasso \
                    else RidgeCV(alphas=np.logspace(-2, 3, 30))
                a = float(cv.fit(A, ytr).alpha_)
            mk = (lambda al: Lasso(alpha=al, max_iter=20000)) if es_lasso else (lambda al: Ridge(alpha=al))
            m = mk(a).fit(A, ytr)
            coef = pd.Series(m.coef_, index=X.columns)
            top = coef.abs().sort_values(ascending=False).head(8).index
            ruta = pd.DataFrame({al: pd.Series(mk(al).fit(A, ytr).coef_, index=X.columns)[top] for al in np.logspace(-3, 2, 30)}).T
            st.session_state[f"reg_{nombre}"] = dict(
                alpha=a, coef=coef, ruta=ruta, r2_tr=r2_score(ytr, m.predict(A)), r2_te=r2_score(yte, m.predict(B)),
                rmse=float(np.sqrt(mean_squared_error(yte, m.predict(B)))),
                ols=r2_score(yte, LinearRegression().fit(A, ytr).predict(B)), n=len(idx), p=X.shape[1])
    r = st.session_state.get(f"reg_{nombre}")
    if not r:
        st.info("👆 Pulsa **Entrenar** para ejecutar el modelo."); return

    a, b, c, d = st.columns(4)
    a.metric("Alpha usado", f"{r['alpha']:.4g}"); b.metric("R² entrenamiento", f"{r['r2_tr']:.3f}")
    c.metric("R² prueba", f"{r['r2_te']:.3f}"); d.metric("RMSE prueba (log)", f"{r['rmse']:.3f}")
    t1, t2 = st.tabs(["📊 Coeficientes", "📈 Camino de regularización"])
    with t1:
        top = r["coef"][r["coef"] != 0].reindex(r["coef"].abs().sort_values(ascending=False).index).head(15)
        if top.empty:
            st.warning("Todos los coeficientes quedaron en 0: baja el alpha.")
        else:
            dfc = top.iloc[::-1].rename("Coeficiente").reset_index(); dfc.columns = ["Producto", "Coeficiente"]
            dfc["Signo"] = np.where(dfc["Coeficiente"] > 0, "Aumenta el monto", "Reduce el monto")
            st.plotly_chart(_estilo(px.bar(dfc, x="Coeficiente", y="Producto", orientation="h", color="Signo",
                            color_discrete_map={"Aumenta el monto": ROJO, "Reduce el monto": AZUL}, title="Top 15 coeficientes")))
    with t2:
        rr = r["ruta"].reset_index().melt(id_vars="index", var_name="Producto", value_name="Coeficiente")
        st.plotly_chart(_estilo(px.line(rr, x="index", y="Coeficiente", color="Producto", log_x=True,
                        labels={"index": "Alpha (escala log)"}, title="Cómo cambian los coeficientes al aumentar alpha")))
    nz = int((r["coef"] != 0).sum())
    extra = (f"Lasso conservó <b>{nz} de {r['p']}</b> productos (el resto quedó en 0)." if es_lasso
             else f"Ridge mantiene los {r['p']} productos pero encoge sus coeficientes.")
    aviso = " El R² de prueba es bajo o negativo: la muestra es pequeña y el modelo no generaliza bien." if r["r2_te"] < 0.3 else ""
    tarjeta("💡 Interpretación", f"{extra} El R² de prueba fue <b>{r['r2_te']:.3f}</b> frente a <b>{r['ols']:.3f}</b> de la regresión lineal "
            f"sin penalización con {r['n']} facturas. Una penalización adecuada reduce el sobreajuste (diferencia entre R² de "
            f"entrenamiento {r['r2_tr']:.3f} y de prueba).{aviso}")


def pagina(sub, csv, tabla_binaria):
    if sub == "Clusterización":
        pagina_kmeans(csv)
    elif sub == "PCA · t-SNE · UMAP":
        pagina_reduccion(csv)
    elif sub == "Lasso":
        pagina_regresion("Lasso", csv, tabla_binaria)
    else:
        pagina_regresion("Ridge", csv, tabla_binaria)
