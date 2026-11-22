# Panel para ejecutar los algoritmos de reglas de asociación EN VIVO desde la página
import math, time
import pandas as pd
import plotly.express as px
import streamlit as st
from reglas_asociacion.apriori import Apriori
from reglas_asociacion.eclat import Eclat
from reglas_asociacion.fp_growth import FPGrowth
from ui import ROJO, AZUL, DORADO


def _txt(x):
    return ", ".join(sorted(x)) if hasattr(x, "__iter__") and not isinstance(x, str) else x


def _correr(nombre, df, csv, sup, conf, max_len):
    if nombre == "Apriori":
        m = Apriori(df, min_support=sup, min_confidence=conf, max_len=max_len)
        t = time.perf_counter(); m.ajustar(); t = time.perf_counter() - t
        return dict(itemsets=len(m.frequent_itemsets), reglas=len(m.rules), t=t,
                    tabla=m.resumen().sort_values("Elevación", ascending=False))
    if nombre == "ECLAT":
        m = Eclat(min_support=max(1, math.ceil(sup * df.shape[0])), min_confidence=conf)
        m.load_csv(csv, transaction_col="InvoiceNo", item_col="Description")
        t = time.perf_counter(); m.fit(); t = time.perf_counter() - t
        r = m.generate_rules().copy()
        for c in ("antecedente", "consecuente"):
            r[c] = r[c].apply(_txt)
        if "lift" in r.columns:
            r = r.sort_values("lift", ascending=False)
        return dict(itemsets=len(m.frequent_itemsets), reglas=len(r), t=t, tabla=r)
    m = FPGrowth(min_support=sup, min_confidence=conf)
    t = time.perf_counter(); p = m.ejecutar(df); t = time.perf_counter() - t
    r = m.generar_reglas()[["antecedents", "consequents", "support", "confidence", "lift"]].copy()
    r["antecedents"], r["consequents"] = r["antecedents"].apply(_txt), r["consequents"].apply(_txt)
    return dict(itemsets=len(p), reglas=len(r), t=t, tabla=r.sort_values("lift", ascending=False))


def panel(nombre, df, csv):
    with st.expander("▶ EJECUTAR EN VIVO: cambia los parámetros y corre el algoritmo", expanded=True):
        c1, c2, c3 = st.columns(3)
        sup = c1.slider("Soporte mínimo", 0.01, 0.20, 0.03, 0.005, key=f"sup_{nombre}")
        conf = c2.slider("Confianza mínima", 0.10, 1.00, 0.50, 0.05, key=f"conf_{nombre}")
        ml = c3.slider("Máx. productos por regla (solo Apriori)", 2, 4, 2, key=f"ml_{nombre}")
        b1, b2 = st.columns(2)

        if b1.button(f"▶ Ejecutar {nombre}", key=f"run_{nombre}"):
            with st.spinner(f"Ejecutando {nombre}..."):
                st.session_state[f"vivo_{nombre}"] = _correr(nombre, df, csv, sup, conf, ml)

        if b2.button("⚖️ Ejecutar y comparar los 3 algoritmos", key=f"cmp_{nombre}"):
            filas = []
            with st.status("Ejecutando los tres algoritmos...", expanded=True) as estado:
                for alg in ["Apriori", "ECLAT", "FP-Growth"]:
                    st.write(f"Corriendo {alg}...")
                    r = _correr(alg, df, csv, sup, conf, ml)
                    filas.append([alg, r["itemsets"], r["reglas"], round(r["t"] * 1000, 2)])
                estado.update(label="¡Listo!", state="complete")
            st.session_state["vivo_cmp"] = pd.DataFrame(filas, columns=["Algoritmo", "Itemsets", "Reglas", "Tiempo (ms)"])

        r = st.session_state.get(f"vivo_{nombre}")
        if r:
            st.markdown(f"#### Resultado de {nombre} (soporte {sup} · confianza {conf})")
            a, b, c = st.columns(3)
            a.metric("Itemsets frecuentes", r["itemsets"]); b.metric("Reglas", r["reglas"])
            c.metric("Tiempo", f"{r['t'] * 1000:.1f} ms")
            st.dataframe(r["tabla"].head(20), hide_index=True)
        cmp_ = st.session_state.get("vivo_cmp")
        if cmp_ is not None:
            st.markdown("#### Comparación en vivo")
            st.dataframe(cmp_, hide_index=True)
            fig = px.bar(cmp_, x="Algoritmo", y="Tiempo (ms)", color="Algoritmo", text="Tiempo (ms)",
                         color_discrete_sequence=[ROJO, AZUL, DORADO])
            fig.update_layout(showlegend=False, font=dict(color=AZUL, size=14))
            st.plotly_chart(fig)
