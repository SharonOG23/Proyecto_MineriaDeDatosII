<h1 align="center">Proyecto Final · Minería de Datos II 🛒📊🧬</h1>

<p align="center">
  <b>Aplicación de técnicas de minería de datos y arquitectura de pipelines para el análisis de negocio</b><br>
  Colegio Universitario de Cartago · Tecnologías de Información – Big Data · BD-162 · IIIC-2026
</p>

<p align="center">
  <a href="#"><img alt="CRISP-DM" src="https://img.shields.io/badge/Metodolog%C3%ADa-CRISP--DM-FF5722?style=for-the-badge&logo=readthedocs&logoColor=white"></a>
  <a href="#"><img alt="POO" src="https://img.shields.io/badge/Arquitectura-POO-1B2A49?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="#"><img alt="Reglas" src="https://img.shields.io/badge/Reglas-Apriori%20%7C%20Eclat%20%7C%20FP--Growth-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="#"><img alt="Clustering" src="https://img.shields.io/badge/Clusterizaci%C3%B3n-K--Means%20%7C%20PCA%20%7C%20t--SNE%20%7C%20UMAP-2A9D8F?style=for-the-badge&logo=scikitlearn&logoColor=white"></a>
  <a href="#"><img alt="Regresión" src="https://img.shields.io/badge/Regularizaci%C3%B3n-Lasso%20%7C%20Ridge-9C27B0?style=for-the-badge&logo=scikitlearn&logoColor=white"></a>
  <a href="#"><img alt="Streamlit" src="https://img.shields.io/badge/App-Streamlit-C8102E?style=for-the-badge&logo=streamlit&logoColor=white"></a>
  <a href="#"><img alt="Informe HTML" src="https://img.shields.io/badge/Informe-HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white"></a>
</p>

---

## 📌 Descripción

Para este **Proyecto Final** se diseña e implementa un **flujo de trabajo automatizado (pipeline) basado en Programación Orientada a Objetos (POO)** que integra las fases del ciclo de vida de un proyecto de minería de datos siguiendo la metodología **CRISP-DM**: comprensión del negocio y de los datos.

El objetivo es procesar, transformar y modelar los datos para **tomar decisiones de negocio fundamentadas en ellos**. Todo el trabajo se presenta en una **aplicación web interactiva (Streamlit)** donde los algoritmos pueden ejecutarse **en vivo**, además del informe técnico en Word y HTML.

---

## 🎯 Objetivos específicos

| Objetivo | Cómo se cubre en el proyecto |
|----------|------------------------------|
| **Arquitectura POO** | Pipeline modular y reutilizable con una clase por responsabilidad: limpieza, gráficos y un algoritmo por clase. |
| **Análisis exploratorio y estadístico** | Estadísticas descriptivas para identificar comportamientos, distribuciones y anomalías (ventas por país, mes, día, hora y productos). |
| **Minería de patrones y reglas de asociación** | **Apriori**, **Eclat** y **FP-Growth**. Las reglas *antecedente → consecuente* se interpretan como recomendaciones de productos y paquetes (bundles). |
| **Modelado no supervisado (clusterización)** | **K-Means**, reducción de dimensionalidad (**PCA, t-SNE y UMAP**) y regularización (**Lasso** y **Ridge**), con evaluación de la calidad de los grupos (codo y silueta). |

---

## 📄 Datasets

Datasets asignados al **Grupo #1** en el enunciado del proyecto:

| Dataset | Formato |
|---------|---------|
| `grocery_chain_data.xlsx` | Excel |

Dataset trabajado en el **Examen II** y utilizado actualmente por la aplicación:

| Dataset | Fuente |
|---------|--------|
| **Online Retail** | https://archive.ics.uci.edu/dataset/352/online+retail |

| Característica | Detalle (Online Retail) |
|----------------|-------------------------|
| Descripción | Transacciones de una tienda en línea del Reino Unido que vende regalos para toda ocasión; muchos clientes son mayoristas |
| Registros | 541.909 |
| Periodo | 01/12/2010 al 09/12/2011 |
| Variables | `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country` |
| Archivo original | `Online Retail.xlsx` |
| Licencia | CC BY 4.0 |

---

## 🧭 Metodología CRISP-DM

| Fase | Qué se hizo | Dónde verlo |
|------|-------------|-------------|
| 1. Comprensión del negocio | Problema, objetivos de negocio y de minería, criterios de éxito y restricciones | App → **CRISP-DM** · `CRISP-DM_Fases1-2_Online_Retail.md` |
| 2. Comprensión de los datos | Descripción, calidad inicial, exploración y hallazgos | App → **CRISP-DM** |

---

## 🖥️ Aplicación interactiva

La barra de navegación superior contiene las siguientes secciones:

| Sección | Contenido |
|---------|-----------|
| 🏠 **Inicio** | Portada del proyecto |
| 🧭 **CRISP-DM** | Fases 1 y 2: negocio y datos |
| 🔎 **EDA** | Limpieza paso a paso y gráficos exploratorios con su interpretación |
| 🛒 **Reglas de asociación** | Submenú **Apriori · ECLAT · FP-Growth**, con comparación de tiempos |
| 🧬 **Clusterización** | Submenú **Clusterización · PCA – t-SNE – UMAP · Lasso · Regresión Ridge** |

---

## 📁 Estructura del repositorio

```
Proyecto_MineriaDeDatosII/
├── .streamlit/
│   └── config.toml              # Tema claro de la app
├── eda/                         # Limpieza y gráficos exploratorios
│   ├── limpieza_datos.py
│   ├── graficos_eda.py
│   └── Online Retail.xlsx
├── processed/                   # Datos procesados (muestra CSV)
├── reglas_asociacion/           # Algoritmos de reglas
│   ├── apriori.py
│   ├── eclat.py
│   └── fp_growth.py
├── Clusterizacion/              # Scripts y notebooks de Lasso y Ridge
├── reporte_final/               # Informes (notebook / HTML)
├── app.py                       # Aplicación Streamlit
├── ui.py                        # Estilos y navegación
├── clusterizacion.py            # Sección de clusterización de la app
├── en_vivo.py                   # Ejecución en vivo de los algoritmos
├── CRISP-DM_Fases1-2_Online_Retail.md
└── README.md
```

---

## ⚙️ Instalación y ejecución

**Requisitos:** Python 3.10 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/SharonOG23/Proyecto_MineriaDeDatosII.git
cd Proyecto_MineriaDeDatosII

# 2. Instalar dependencias
pip install streamlit pandas plotly matplotlib mlxtend networkx openpyxl scikit-learn umap-learn

# 3. Ejecutar la aplicación
streamlit run app.py
```

La app se abre en `http://localhost:8501`. La primera vez que se entra a **EDA** puede tardar uno o dos minutos mientras se limpia el Excel.

---

## 📦 Rúbrica

**Fecha de entrega:** 24 de noviembre de 2026, antes de las 6:00 p. m. en el CUCVirtual. La defensa se realiza el mismo día.

| Peso | Criterio | Entregable |
|------|----------|------------|
| 2% | Repositorio | Código fuente modular, estructura de directorios y documentación (este README) |
| 10% | Informe y HTML | Informe técnico en **Word** y en **HTML** (código, ejecución completa e interpretación) |
| 5% | Defensa | Demostración práctica **en vivo** del sistema funcionando |
| 3% | Foro | Experiencias vividas, aciertos y lecciones aprendidas |
| **20%** | **TOTAL** | |

---

## 🤝 Equipo (Grupo #1)

| Integrante | Responsabilidad |
|------------|-----------------|
| Johel Josue Barquero Carvajal | Apriori |
| Edward Steven Vindas Rivera | Limpieza y estadística |
| Marisol Víquez Rivera | FP-Growth |
| Fabián Brenes Loria | CRISP-DM (fases 1 y 2) |
| Sharon Valeria Obando Gómez | Eclat |

**Profesor:** Ronald Córdoba Vega
**Curso:** Minería de Datos II (BD-162) · IIIC-2026

---

## 📜 Licencia

Proyecto de uso académico. El dataset Online Retail se utiliza bajo su licencia CC BY 4.0.

---

<p align="center"><sub>Proyecto académico del Colegio Universitario de Cartago (CUC) · Curso de Minería de Datos II</sub></p>
