# Metodología _CRISP-DM_

# 1. Fase 1: Comprensión del Negocio

## 1.1 Contexto del problema

El conjunto de datos registra, durante poco más de un año (1 dic 2010 – 9 dic 2011), **25 900 facturas** emitidas por un comercio que vende por internet **541 909 líneas de producto**. El análisis del contenido sugiere el perfil del negocio:

- **Surtido de regalos y artículos decorativos para el hogar.** Los productos más frecuentes son _WHITE HANGING HEART T-LIGHT HOLDER_, _JUMBO BAG RED RETROSPOT_, _REGENCY CAKESTAND 3 TIER_, _PARTY BUNTING_ y _LUNCH BAG RED RETROSPOT_.
- **Operación internacional con fuerte concentración local.** Hay 38 valores de `Country`; Reino Unido concentra el 91,4 % de las filas y el 85,2 % del importe de las ventas válidas.
- **Posible clientela mayorista.** La mediana de `Quantity` es 3 unidades, pero el percentil 99 es 100 y el máximo es 80 995. Hay cestas de hasta 1 106 referencias distintas.
- **Rastros de la operación comercial.** Existen códigos que no son mercancía (`POST`, `AMAZONFEE`, `BANK CHARGES`, `CRUK`), lo que sugiere venta por varios canales, cobro de envíos y comisiones **[SUPUESTO]**.

En este contexto, el comercio necesita entender **qué productos se compran juntos**, pues con 3 791 referencias efectivamente vendidas y 19 773 facturas válidas, la matriz factura × producto tiene una densidad de solo 0,69 %. Es inviable detectar a simple vista qué combinaciones recurren.

## 1.2 Descripción del dominio de aplicación

| Elemento                    | Descripción basada en el dataset                                                                     |
| --------------------------- | ---------------------------------------------------------------------------------------------------- |
| Dominio                     | Comercio electrónico minorista/mayorista de artículos de regalo y decoración.                        |
| Unidad transaccional        | La factura (`InvoiceNo`), que actúa como "cesta de compra".                                          |
| Ítems                       | Productos identificados por `StockCode` (3 791 referencias vendidas tras la depuración).             |
| Tamaño típico de cesta      | Mediana de 15 productos distintos por factura; media de 26,2.                                        |
| Cobertura geográfica        | 38 países; Reino Unido, Alemania, Francia e Irlanda (`EIRE`) encabezan en facturas.                  |
| Estacionalidad aparente     | Crecimiento sostenido de septiembre a noviembre de 2011 (50 226 → 60 742 → 84 711 líneas mensuales). |
| Técnica natural del dominio | Análisis de la cesta de mercado (_market basket analysis_).                                          |

## 1.3 Problema de negocio

> **El comercio dispone de un volumen alto de transacciones pero carece de un conocimiento sistemático sobre las combinaciones de productos que sus clientes adquieren conjuntamente.**

Tres hechos del dataset justifican el problema:

1. **Dispersión del surtido:** 3 791 referencias y una densidad de cesta de 0,69 %. Solo 3 referencias aparecen en más del 10 % de las facturas y 829 en más del 1 %.
2. **Cestas heterogéneas:** el 7,6 % de las facturas válidas contiene un único producto, mientras que el 1 % contiene más de 218. Mezclar ambos tipos de compra dificulta detectar patrones.
3. **Facturación afectada por devoluciones:** el 14,8 % de las facturas (3 836 de 25 900) son cancelaciones, lo que indica un proceso de devolución relevante que debe tratarse con criterio.

## 1.4 Objetivos de negocio

| Código | Objetivo                                                                                                                | Evidencia que lo motiva                                                                      |
| ------ | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| ON-1   | Identificar combinaciones de productos con alta probabilidad de compra conjunta para **venta cruzada** en el sitio web. | Existen 1 523 reglas con confianza ≥ 0,5 en un piloto con soporte ≥ 1 % (sección 2.11).      |
| ON-2   | Proponer **paquetes (_bundles_)** a partir de familias de producto que se compran juntas.                               | Familias como _HERB MARKER_ y _REGENCY TEACUP AND SAUCER_ muestran asociaciones muy fuertes. |
| ON-3   | Distinguir patrones de compra del **mercado nacional frente al internacional**.                                         | Reino Unido: 90,5 % de las facturas válidas; los otros 37 países suman el 9,5 %.             |
| ON-4   | Evaluar la **estabilidad temporal** de los patrones para planificar campañas.                                           | El volumen mensual crece de 25 525 (dic 2011, parcial) a 84 711 líneas (nov 2011).           |
| ON-5   | Sentar bases para una segmentación posterior de clientes.                                                               | Hay 4 334 clientes identificados; el 34,7 % compró una sola vez.                             |

> Los objetivos de negocio son **hipótesis de trabajo** derivadas del contenido del dataset; deben validarse con la persona responsable del negocio.

## 1.5 Objetivos de minería de datos

| Código | Objetivo técnico                                                                | Técnica / entregable                                                                                                |
| ------ | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| OM-1   | Extraer **conjuntos frecuentes** con distintos soportes mínimos.                | Apriori, ECLAT y FP-Growth.                                                                                         |
| OM-2   | Generar **reglas de asociación** y evaluarlas con múltiples métricas.           | Soporte, confianza, _lift_, _leverage_, _conviction_.                                                               |
| OM-3   | Descubrir patrones que incorporen **valor monetario**.                          | Minería de conjuntos de alta utilidad (_High-Utility Itemset Mining_), pues se dispone de `Quantity` y `UnitPrice`. |
| OM-4   | Explorar **patrones secuenciales** entre compras sucesivas de un mismo cliente. | PrefixSpan / SPADE sobre los clientes con más de una factura (65,3 % de 4 334).                                     |
| OM-5   | Segmentar facturas o clientes como técnica complementaria.                      | Clustering (RFM, _k_-means) si el tiempo lo permite.                                                                |

## 1.6 Criterios de éxito

### Criterios de éxito del negocio

| Código | Criterio                         | Umbral propuesto                                                                                                                             |
| ------ | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| CN-1   | Reglas accionables identificadas | Al menos 10 reglas con soporte ≥ 1 %, confianza ≥ 0,5 y _lift_ ≥ 1,2 que **no** sean simples variantes de color/diseño de un mismo producto. |
| CN-2   | Paquetes propuestos              | Al menos 3 propuestas de paquete respaldadas por reglas o conjuntos frecuentes.                                                              |
| CN-3   | Interpretabilidad                | Cada regla presentada incluye descripción de producto legible y lectura de negocio.                                                          |

### Criterios de éxito de minería de datos

| Código | Criterio                             | Umbral propuesto                                                                                             |
| ------ | ------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| CM-1   | Equivalencia entre algoritmos        | Apriori, ECLAT y FP-Growth devuelven el mismo número de conjuntos frecuentes para el mismo soporte.          |
| CM-2   | Comparación de desempeño documentada | Tiempo y memoria registrados para al menos 4 niveles de soporte.                                             |
| CM-3   | Validación temporal                  | Entrenar con dic 2010 – jun 2011 y comprobar en jul – nov 2011 que ≥ 70 % de las reglas conserva _lift_ > 1. |
| CM-4   | Reproducibilidad                     | Código y semillas versionados en el repositorio.                                                             |

## 1.7 Beneficios esperados

| Tipo      | Beneficio                                                                        |
| --------- | -------------------------------------------------------------------------------- |
| Comercial | Mejora del valor medio de factura mediante recomendaciones y paquetes.           |
| Operativo | Mejor planificación de inventario de referencias frecuentemente co-compradas.    |
| Analítico | Catálogo de patrones validados y reutilizables.                                  |
| Académico | Comparación empírica de Apriori, ECLAT y FP-Growth sobre datos reales dispersos. |

> El beneficio económico no puede estimarse con rigor porque el dataset **no contiene costos ni márgenes**.

## 1.8 Restricciones y supuestos

### Restricciones

| #   | Restricción                                                | Evidencia                                                           |
| --- | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| R1  | Un solo comercio y un solo periodo (≈ 12 meses).           | Rango temporal 2010-12-01 a 2011-12-09.                             |
| R2  | Diciembre de 2011 está incompleto (hasta el día 9).        | 25 525 líneas frente a 84 711 de noviembre.                         |
| R3  | 24,93 % de las filas no tiene `CustomerID`.                | 135 080 nulos.                                                      |
| R4  | No hay taxonomía de productos, costos ni márgenes.         | Solo 8 atributos.                                                   |
| R5  | Los países distintos de Reino Unido tienen pocas facturas. | Alemania 443, Francia 382, EIRE 282, Bélgica 98 (facturas válidas). |

### Supuestos

| #   | Supuesto                                                                                                                    |
| --- | --------------------------------------------------------------------------------------------------------------------------- |
| S1  | Una factura equivale a una cesta de compra.                                                                                 |
| S2  | El prefijo `C` identifica cancelaciones; los registros con prefijo `A` son ajustes contables.                               |
| S3  | Las líneas con precio cero, cantidad negativa sin prefijo `C` y códigos no comerciales no representan compras de mercancía. |
| S4  | La moneda es la libra esterlina.                                                                                            |
| S5  | La presencia o ausencia de un producto (binaria) es suficiente para el análisis de reglas; la cantidad se tratará aparte.   |

## 1.9 Preguntas de investigación

| Código | Pregunta                                                                                               | Fase donde se responde |
| ------ | ------------------------------------------------------------------------------------------------------ | ---------------------- |
| PI-1   | ¿Qué productos y pares de productos presentan mayor soporte, y qué proporción del surtido explican?    | 2, 4                   |
| PI-2   | ¿Cómo varía el número de conjuntos frecuentes y reglas al reducir el soporte mínimo de 5 % a 1 %?      | 4                      |
| PI-3   | ¿Producen Apriori, ECLAT y FP-Growth los mismos resultados, y con qué diferencias de tiempo y memoria? | 4, 5                   |

---

# 2. Fase 2: Comprensión de los Datos

## 2.1 Descripción general del conjunto de datos

| Característica                      | Valor                                             |
| ----------------------------------- | ------------------------------------------------- |
| Archivo                             | `Online_Retail.xlsx` (23,7 MB)                    |
| Registros (líneas de factura)       | **541 909**                                       |
| Atributos                           | **8**                                             |
| Facturas distintas                  | 25 900                                            |
| Referencias (`StockCode`) distintas | 4 070 (3 958 tras unificar mayúsculas/minúsculas) |
| Descripciones distintas             | 4 223                                             |
| Clientes identificados              | 4 372                                             |
| Países                              | 38                                                |
| Periodo                             | 2010-12-01 08:26 – 2011-12-09 12:50               |

## 2.2 Origen de los datos

El archivo no incluye metadatos de procedencia. Su estructura (nombre `Online Retail`, ocho atributos y periodo de diciembre de 2010 a diciembre de 2011) **coincide con el conjunto público _Online Retail_ del repositorio UCI Machine Learning Repository** (Chen, Sain y Guo, 2012). Esta identificación proviene del conocimiento general del conjunto y **no puede verificarse con el archivo [POR CONFIRMAR]**. Según esa fuente pública, se trata de transacciones de un comercio minorista en línea registrado en el Reino Unido, sin tienda física, que vende regalos para toda ocasión y cuya clientela incluye mayoristas.

## 2.3 Descripción detallada de cada atributo

| #   | Atributo      | Descripción                                                                    | Tipo técnico (pandas)                | Tipo conceptual           | Nulos             | Valores distintos | Observaciones                                                                                             |
| --- | ------------- | ------------------------------------------------------------------------------ | ------------------------------------ | ------------------------- | ----------------- | ----------------- | --------------------------------------------------------------------------------------------------------- |
| 1   | `InvoiceNo`   | Identificador de la factura. Un prefijo `C` marca cancelaciones.               | `object` (mezcla de enteros y texto) | Nominal (identificador)   | 0                 | 25 900            | 532 618 líneas numéricas, 9 288 con prefijo `C` y 3 con prefijo `A`.                                      |
| 2   | `StockCode`   | Código del producto. Patrón habitual: 5 dígitos con sufijo opcional de letras. | `object` (mezcla de enteros y texto) | Nominal (identificador)   | 0                 | 4 070             | 33 códigos no son mercancía; 117 códigos tienen letras en minúscula.                                      |
| 3   | `Description` | Nombre del producto en texto libre.                                            | `str`                                | Nominal (texto)           | 1 454 (0,27 %)    | 4 223             | Espacios sobrantes en 113 453 registros; algunas descripciones son notas operativas ("damaged", "check"). |
| 4   | `Quantity`    | Unidades vendidas en la línea.                                                 | `int64`                              | Numérica discreta (razón) | 0                 | —                 | Mín −80 995 · mediana 3 · media 9,55 · desv. 218,08 · máx 80 995.                                         |
| 5   | `InvoiceDate` | Fecha y hora de la factura.                                                    | `datetime64`                         | Temporal                  | 0                 | —                 | 2010-12-01 08:26 a 2011-12-09 12:50.                                                                      |
| 6   | `UnitPrice`   | Precio unitario (moneda por confirmar).                                        | `float64`                            | Numérica continua (razón) | 0                 | —                 | Mín −11 062,06 · mediana 2,08 · media 4,61 · desv. 96,76 · máx 38 970,00.                                 |
| 7   | `CustomerID`  | Identificador numérico del cliente.                                            | `float64` (por los nulos)            | Nominal (identificador)   | 135 080 (24,93 %) | 4 372             | Rango 12 346 – 18 287; debe tratarse como categórico, no numérico.                                        |
| 8   | `Country`     | País de residencia del cliente.                                                | `str`                                | Nominal                   | 0                 | 38                | Reino Unido: 495 478 filas (91,43 %).                                                                     |

### Tipos de variables (resumen)

| Categoría             | Atributos                              |
| --------------------- | -------------------------------------- |
| Identificadores       | `InvoiceNo`, `StockCode`, `CustomerID` |
| Categóricas nominales | `Country`, `Description`               |
| Numéricas             | `Quantity`, `UnitPrice`                |
| Temporales            | `InvoiceDate`                          |

## 2.4 Cantidad de registros y atributos

- **Antes de depurar:** 541 909 × 8.
- **Base transaccional depurada** (criterios de la sección 2.9.1): **527 725 líneas** (97,4 % del total), **19 773 facturas**, **3 791 productos** y **4 334 clientes**.
- Tras eliminar duplicados factura-producto (10 471 líneas repetidas dentro de una misma factura) se obtiene la matriz binaria factura × producto de 19 773 × 3 791.

## 2.5 Calidad inicial de los datos

| Dimensión                 | Hallazgo                                                                                                                                      | Evaluación                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Completitud**           | `CustomerID` 24,93 % faltante; `Description` 0,27 % faltante.                                                                                 | Deficiente en `CustomerID`; aceptable en el resto. |
| **Unicidad**              | 5 268 filas duplicadas exactas (0,97 %).                                                                                                      | Requiere depuración.                               |
| **Validez**               | 2 precios negativos; 2 515 precios iguales a 0; 9 288 cantidades negativas en cancelaciones y 1 336 en filas sin prefijo `C`.                 | Requiere depuración.                               |
| **Consistencia**          | 650 códigos con más de una descripción; 172 descripciones asignadas a más de un código; 112 códigos duplicados por diferencias de mayúsculas. | Requiere normalización.                            |
| **Exactitud / atípicos**  | Cantidad y precio con extremos de ±80 995 y 38 970.                                                                                           | Requiere análisis de atípicos.                     |
| **Integridad de factura** | Ninguna factura tiene más de un país; 43 facturas tienen más de una marca temporal; 8 clientes aparecen en más de un país.                    | Aceptable con observaciones.                       |

## 2.6 Identificación de valores faltantes

| Atributo            | Faltantes | %     |
| ------------------- | --------- | ----- |
| `CustomerID`        | 135 080   | 24,93 |
| `Description`       | 1 454     | 0,27  |
| Resto (6 atributos) | 0         | 0,00  |

**Patrones de ausencia (evidencia):**

- Las **1 454 filas sin `Description` carecen también de `CustomerID` y tienen `UnitPrice` = 0**. Son registros administrativos, no ventas.
- De las 2 515 líneas con precio 0, el 98,4 % no tiene `CustomerID`.
- Hay **3 710 facturas sin cliente** (14,3 % de las 25 900); ninguna factura mezcla líneas con y sin cliente, por lo que la ausencia es **a nivel de factura**, no de línea.
- Tras la depuración, 1 371 de las 19 773 facturas válidas (6,9 %) siguen sin cliente.

## 2.7 Identificación de posibles inconsistencias

| #    | Inconsistencia                                                                                                                                                                                       | Cantidad                                                         | Tratamiento sugerido                                             |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| I-1  | Facturas de cancelación (`C`) con cantidad negativa                                                                                                                                                  | 3 836 facturas / 9 288 líneas                                    | Excluir de la minería de cestas; analizar aparte (PI-11).        |
| I-2  | Facturas `A` ("Adjust bad debt", código `B`) con precios ±11 062,06                                                                                                                                  | 3 líneas                                                         | Excluir.                                                         |
| I-3  | Cantidad negativa **sin** prefijo `C`                                                                                                                                                                | 1 336 líneas (862 sin descripción; 100 % sin cliente y precio 0) | Excluir (ajustes de inventario).                                 |
| I-4  | Precio unitario igual a 0                                                                                                                                                                            | 2 515 líneas                                                     | Excluir.                                                         |
| I-5  | Códigos no comerciales (`POST` 1 256, `DOT` 710, `M` 571, `C2` 144, `D` 77, `S` 63, `BANK CHARGES` 37, `AMAZONFEE` 34, `CRUK` 16, `DCGS*`, `gift_0001_*`…)                                           | 33 códigos / 2 995 líneas                                        | Excluir de las cestas.                                           |
| I-6  | Duplicados exactos                                                                                                                                                                                   | 5 268 filas                                                      | Eliminar.                                                        |
| I-7  | Mismo producto en la misma factura repetido en varias líneas                                                                                                                                         | 10 471 líneas (en la base depurada)                              | Colapsar a una presencia por factura.                            |
| I-8  | Códigos con mayúsculas y minúsculas mezcladas (p. ej. `85123A` y `85123a`)                                                                                                                           | 4 070 → 3 958 códigos                                            | Pasar a mayúsculas.                                              |
| I-9  | Un mismo código con varias descripciones                                                                                                                                                             | 650 códigos                                                      | Usar la descripción más frecuente por código.                    |
| I-10 | Una misma descripción con varios códigos                                                                                                                                                             | 172 descripciones                                                | Revisar; posible consolidación.                                  |
| I-11 | Espacios sobrantes y dobles espacios en `Description`                                                                                                                                                | 113 453 y 22 290 registros                                       | `strip()` y normalización de espacios.                           |
| I-12 | `InvoiceNo` y `StockCode` con tipo mixto (entero/texto)                                                                                                                                              | 541 909                                                          | Convertir a `str`.                                               |
| I-13 | Países `Unspecified` y `European Community`                                                                                                                                                          | 446 y 61 filas                                                   | Mantener como categoría.                                         |
| I-14 | Cantidades extremas con cancelación inmediata (p. ej. 80 995 unidades, factura 581483 y su cancelación C581484 al mismo cliente; patrón análogo en la factura 541431 y la C541433 del cliente 12346) | Casos aislados                                                   | Revisar; pueden distorsionar estadísticas de cantidad e ingreso. |

> **Observación crítica.** La factura 581483 (80 995 unidades de _PAPER CRAFT, LITTLE BIRDIE_ a 2,08, equivalente a £168 469,60) se conserva en la base depurada, mientras que su cancelación C581484 se excluye. Por ello, ese producto aparece en segundo lugar por ingresos, resultado engañoso. **Si se calculan estadísticas de cantidad o ingreso, deben netearse las cancelaciones o eliminarse la pareja compra-cancelación.**

## 2.8 Análisis exploratorio inicial

### 2.8.1 Criterios de depuración aplicados para el análisis

Una línea se consideró **válida** si cumple simultáneamente:

1. `InvoiceNo` no empieza por `C` ni por `A`.
2. `Quantity` > 0 y `UnitPrice` > 0.
3. `StockCode` coincide con el patrón de producto (5 dígitos y hasta 2 letras).
4. `Description` no es nula.

Resultado: **527 725 líneas, 19 773 facturas, 3 791 productos, 4 334 clientes**. Se perdió el 2,6 % de las líneas pero el **23,7 % de las facturas**: 3 836 son cancelaciones y las restantes 2 291 carecen de cualquier línea válida.

### 2.8.2 Distribución temporal

| Mes                      | Líneas     |
| ------------------------ | ---------- |
| 2010-12                  | 42 481     |
| 2011-01                  | 35 147     |
| 2011-02                  | 27 707     |
| 2011-03                  | 36 748     |
| 2011-04                  | 29 916     |
| 2011-05                  | 37 030     |
| 2011-06                  | 36 874     |
| 2011-07                  | 39 518     |
| 2011-08                  | 35 284     |
| 2011-09                  | 50 226     |
| 2011-10                  | 60 742     |
| **2011-11**              | **84 711** |
| 2011-12 (hasta el día 9) | 25 525     |

- Existe un **claro aumento hacia el final del año**: noviembre de 2011 concentra el 15,6 % de todas las líneas.
- **No hay ninguna transacción en sábado.** Los demás días: jueves 103 857 líneas (el máximo), martes 101 808, lunes 95 111, miércoles 94 565, viernes 82 193 y domingo 64 375.
- La actividad ocurre entre las **6:00 y las 20:59**, con máximo a las 12:00 (78 709 líneas); entre las 12:00 y las 15:59 se concentra el 54,6 % de las líneas.

### 2.8.3 Distribución geográfica

| País         | Líneas  | % de líneas | Facturas válidas |
| ------------ | ------- | ----------- | ---------------- |
| Reino Unido  | 495 478 | 91,43       | 17 901 (90,5 %)  |
| Alemania     | 9 495   | 1,75        | 443              |
| Francia      | 8 557   | 1,58        | 382              |
| EIRE         | 8 196   | 1,51        | 282              |
| España       | 2 533   | 0,47        | 88               |
| Países Bajos | 2 371   | 0,44        | 93               |
| Bélgica      | 2 069   | 0,38        | 98               |
| Australia    | 1 259   | 0,23        | 56               |

Participación en ingresos (ventas válidas, bruto): Reino Unido 85,2 %, Países Bajos 2,8 %, EIRE 2,6 %, Alemania 2,0 %, Francia 1,8 %, Australia 1,3 %. **Los Países Bajos y Australia pesan más en ingresos que en facturas**, lo que sugiere compras de mayor tamaño.

### 2.8.4 Cantidades y precios

| Estadístico    | `Quantity` | `UnitPrice` |
| -------------- | ---------- | ----------- |
| Mínimo         | −80 995    | −11 062,06  |
| Percentil 1    | −2         | 0,19        |
| Mediana        | 3          | 2,08        |
| Media          | 9,55       | 4,61        |
| Percentil 95   | 29         | 9,95        |
| Percentil 99   | 100        | 18,00       |
| Percentil 99,9 | 468,92     | 205,56      |
| Máximo         | 80 995     | 38 970,00   |

Las distribuciones son **fuertemente asimétricas a la derecha** (media muy superior a la mediana) y presentan extremos que no corresponden a ventas habituales (por ejemplo, `AMAZONFEE` y `Manual` con precios de hasta 38 970).

### 2.8.5 Productos

**Diez productos con mayor frecuencia de aparición** (base depurada, 19 773 facturas):

| #   | Producto                           | Facturas | Soporte |
| --- | ---------------------------------- | -------- | ------- |
| 1   | WHITE HANGING HEART T-LIGHT HOLDER | 2 265    | 11,46 % |
| 2   | JUMBO BAG RED RETROSPOT            | 2 089    | 10,56 % |
| 3   | REGENCY CAKESTAND 3 TIER           | 1 988    | 10,05 % |
| 4   | PARTY BUNTING                      | 1 685    | 8,52 %  |
| 5   | LUNCH BAG RED RETROSPOT            | 1 565    | 7,91 %  |
| 6   | ASSORTED COLOUR BIRD ORNAMENT      | 1 455    | 7,36 %  |
| 7   | SMALL POPCORN HOLDER               | 1 392    | 7,04 %  |
| 8   | SET OF 3 CAKE TINS PANTRY DESIGN   | 1 385    | 7,00 %  |
| 9   | PACK OF 72 RETROSPOT CAKE CASES    | 1 320    | 6,68 %  |
| 10  | LUNCH BAG SUKI DESIGN              | 1 284    | 6,49 %  |

### 2.8.6 Tamaño de las cestas (base depurada)

| Estadístico         | Productos distintos por factura |
| ------------------- | ------------------------------- |
| Media               | 26,16                           |
| Desviación estándar | 47,01                           |
| Mediana             | 15                              |
| Percentil 75        | 29                              |
| Percentil 90        | 52                              |
| Percentil 95        | 75                              |
| Percentil 99        | 218                             |
| Máximo              | 1 106                           |

- 1 500 facturas (7,6 %) contienen un solo producto: **no aportan información a las reglas**.
- 18 273 facturas (92,4 %) contienen al menos 2 productos y 17 460 al menos 3: la base permite generar reglas.

### 2.8.7 Clientes (base depurada con `CustomerID`)

| Estadístico  | Facturas por cliente | Gasto por cliente (£) |
| ------------ | -------------------- | --------------------- |
| Media        | 4,2                  | 2 021,5               |
| Mediana      | 2                    | 668,1                 |
| Percentil 75 | 5                    | 1 631,6               |
| Máximo       | 206                  | 279 138,0             |

- El **34,7 %** de los clientes realizó una única compra y el **65,3 %** compró más de una vez.
- La distribución del gasto es muy asimétrica (media = 3 veces la mediana).

## 2.9 Hallazgos preliminares

| #    | Hallazgo                                                | Evidencia                                                    | Implicación                                                       |
| ---- | ------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------- |
| H-1  | El dataset es de naturaleza transaccional.              | Cada factura agrupa 1 a 1 106 productos.                     | Es adecuado para reglas de asociación.                            |
| H-2  | Alta dispersión.                                        | Densidad de 0,69 %.                                          | Se necesitan soportes bajos (1 %–2 %) para obtener reglas.        |
| H-3  | Existen registros administrativos mezclados con ventas. | 2 995 líneas con códigos no comerciales; 2 515 con precio 0. | La depuración es obligatoria.                                     |
| H-4  | El 14,8 % de las facturas son cancelaciones.            | 3 836 de 25 900.                                             | Dejar cancelaciones dentro distorsiona cantidades e ingresos.     |
| H-5  | Cestas muy heterogéneas.                                | Mediana 15, percentil 99 = 218, máximo 1 106.                | Evaluar acotar cestas extremas o separar mayoristas.              |
| H-6  | `CustomerID` falta en una cuarta parte de las filas.    | 24,93 %.                                                     | Limita el análisis por cliente, no el análisis de cestas.         |
| H-7  | Fuerte concentración geográfica.                        | Reino Unido 90,5 % de las facturas válidas.                  | Analizar Reino Unido por separado; el resto tiene pocas facturas. |
| H-8  | Estacionalidad.                                         | Pico en noviembre de 2011; diciembre incompleto.             | Validar con partición temporal.                                   |
| H-9  | Cola larga de productos.                                | 12,6 % de las referencias genera el 50 % de las apariciones. | La mayoría de las referencias no alcanzará soporte útil.          |
| H-10 | Valores extremos con compra y cancelación inmediatas.   | Facturas 581483/C581484 y 541431/C541433.                    | Sesgan los análisis monetarios.                                   |

## 2.10 Potencial del dataset para técnicas de descubrimiento de patrones

### 2.10.1 Reglas de asociación, Apriori, ECLAT y FP-Growth

**Conclusión: el dataset es adecuado para reglas de asociación**, por las razones siguientes:

1. La unidad (factura) y los ítems (producto) están claramente definidos.
2. 18 273 facturas contienen al menos 2 productos.
3. Existen productos con soporte alto (3 con ≥ 10 %) y una cola larga para estudiar el efecto del umbral.

---
