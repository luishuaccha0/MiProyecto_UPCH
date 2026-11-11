
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="Arborización de Lima | SERPAR",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "datos"

MESES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]
MESES_ES = {
    "ENERO": "Enero", "FEBRERO": "Febrero", "MARZO": "Marzo",
    "ABRIL": "Abril", "MAYO": "Mayo", "JUNIO": "Junio",
    "JULIO": "Julio", "AGOSTO": "Agosto", "SETIEMBRE": "Setiembre",
    "OCTUBRE": "Octubre", "NOVIEMBRE": "Noviembre", "DICIEMBRE": "Diciembre"
}

# Paleta pastel desaturada
BG = "#F2F7F0"
PANEL = "#EAF2E8"
GREEN = "#B7CDBB"
GREEN_MID = "#91B39A"
GREEN_DARK = "#63866F"
GREEN_PALE = "#E1EBE3"
BLUE_PALE = "#DCE8E9"
TEXT = "#35443A"
GRID = "#E6ECE7"
PALETTE = ["#B7CDBB", "#DCE8DF", "#91B39A", "#C9DAD1", "#E8EFEB", "#B8CCD1", "#D9E2D5"]

# ============================================================
# UTILIDADES
# ============================================================
def leer_csv(ruta, archivo_subido=None):
    """Lee un CSV local o uno cargado desde la interfaz."""
    if archivo_subido is not None:
        return pd.read_csv(archivo_subido, encoding="utf-8-sig")
    if ruta.exists():
        return pd.read_csv(ruta, encoding="utf-8-sig")
    return None


def convertir_numero(serie):
    """Convierte números con separador de miles y porcentajes."""
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace({"": None, "nan": None, "None": None}),
        errors="coerce"
    )


def estilo_figura(fig, altura=400):
    fig.update_layout(
        height=altura,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=TEXT, family="Arial"),
        margin=dict(l=20, r=30, t=45, b=35),
        hoverlabel=dict(
            bgcolor="#F3F7F3",
            bordercolor="#C9D8CC",
            font=dict(color=TEXT)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#DCE5DE"
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        linecolor="#DCE5DE"
    )
    return fig


def figura_arboles_barras(x, y, orientacion="v", color=GREEN):
    fig = go.Figure()
    if orientacion == "h":
        fig.add_trace(go.Bar(
            x=x, y=y, orientation="h",
            marker=dict(color=color, line=dict(color=GREEN_DARK, width=1)),
            text=[f"🌳 {v:,.0f}" for v in x],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>Árboles: %{x:,.0f}<extra></extra>"
        ))
    else:
        fig.add_trace(go.Bar(
            x=x, y=y,
            marker=dict(color=color, line=dict(color=GREEN_DARK, width=1)),
            text=[f"🌳 {v:,.0f}" for v in y],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>Árboles: %{y:,.0f}<extra></extra>"
        ))
    return fig


# ============================================================
# CARGA Y PREPARACIÓN DE LOS DOS ARCHIVOS
# ============================================================
@st.cache_data(show_spinner=False)
def preparar_programa(df):
    df = df.copy()
    df.columns = [str(c).strip().upper() for c in df.columns]

    col_meta = next((c for c in df.columns if "METAS" in c), None)
    col_total = next((c for c in df.columns if "CANTIDAD ARBOLES PLANTADOS" in c), None)
    col_cumplimiento = next((c for c in df.columns if "CUMPLIMIENTO" in c), None)

    if not col_meta or not col_total:
        raise ValueError(
            "El CSV del programa requiere las columnas METAS y CANTIDAD ARBOLES PLANTADOS."
        )

    df["AÑO"] = pd.to_numeric(
        df[col_meta].astype(str).str.extract(r"(20\d{2})")[0],
        errors="coerce"
    )
    df["TOTAL_PLANTADO"] = convertir_numero(df[col_total])

    if col_cumplimiento:
        df["CUMPLIMIENTO"] = convertir_numero(df[col_cumplimiento])
    else:
        df["CUMPLIMIENTO"] = pd.NA

    for mes in MESES:
        if mes in df.columns:
            df[mes] = convertir_numero(df[mes])

    return df


@st.cache_data(show_spinner=False)
def preparar_distribucion(df):
    df = df.copy()
    df.columns = [str(c).strip().upper() for c in df.columns]

    if "AÑO" not in df.columns or "MES" not in df.columns:
        raise ValueError("El CSV distrital requiere las columnas AÑO y MES.")

    df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
    df["MES"] = df["MES"].astype(str).str.strip().str.upper()

    columnas_fijas = {"ITEM", "AÑO", "MES", "TOTAL"}
    distritos = [c for c in df.columns if c not in columnas_fijas]

    for distrito in distritos:
        df[distrito] = convertir_numero(df[distrito])

    # Excluir filas de resumen y conservar solo registros mensuales con año.
    df = df[df["MES"].isin(MESES) & df["AÑO"].notna()].copy()
    return df, distritos


# ============================================================
# BARRA LATERAL Y CARGA DE ARCHIVOS
# ============================================================
st.sidebar.title("🌳 SERPAR Lima")
st.sidebar.caption("Explorador interactivo de arborización")
st.sidebar.divider()

with st.sidebar.expander("📂 Actualizar archivos CSV", expanded=False):
    subir_programa = st.file_uploader(
        "Programa de arborización",
        type=["csv"],
        key="upload_programa"
    )
    subir_distritos = st.file_uploader(
        "Distribución por distrito",
        type=["csv"],
        key="upload_distritos"
    )

try:
    raw_programa = leer_csv(DATA_DIR / "programa_arborizacion.csv", subir_programa)
    raw_distritos = leer_csv(DATA_DIR / "distribucion_distritos.csv", subir_distritos)

    if raw_programa is None or raw_distritos is None:
        st.error("Faltan los archivos CSV. Colócalos en la carpeta datos o súbelos desde el panel lateral.")
        st.stop()

    programa = preparar_programa(raw_programa)
    distribucion, lista_distritos = preparar_distribucion(raw_distritos)

except Exception as error:
    st.error(f"No se pudieron procesar los archivos: {error}")
    st.stop()

if programa.empty or distribucion.empty:
    st.warning("Uno de los archivos no contiene registros para mostrar.")
    st.stop()

# ============================================================
# FILTROS INTERACTIVOS
# ============================================================
st.sidebar.subheader("🎛️ Filtros")

anios_disponibles = sorted(
    set(programa["AÑO"].dropna().astype(int).tolist())
    | set(distribucion["AÑO"].dropna().astype(int).tolist())
)
anios_seleccionados = st.sidebar.multiselect(
    "Años",
    options=anios_disponibles,
    default=anios_disponibles,
    help="Selecciona uno o varios años para actualizar las visualizaciones."
)

meses_seleccionados = st.sidebar.multiselect(
    "Meses",
    options=MESES,
    default=MESES,
    format_func=lambda m: MESES_ES[m],
    help="Los meses seleccionados se aplican a los gráficos mensuales y distritales."
)

distritos_ordenados = sorted(lista_distritos)
distritos_seleccionados = st.sidebar.multiselect(
    "Distritos",
    options=distritos_ordenados,
    default=distritos_ordenados,
    help="Selecciona los distritos que quieres comparar."
)

st.sidebar.divider()
st.sidebar.caption("Los gráficos tienen zoom, desplazamiento y detalles al pasar el cursor.")

# Si se desmarca toda la lista, indicamos que no hay selección en vez de mostrar datos engañosos.
programa_f = programa[programa["AÑO"].isin(anios_seleccionados)].copy()
distribucion_f = distribucion[
    distribucion["AÑO"].isin(anios_seleccionados)
    & distribucion["MES"].isin(meses_seleccionados)
].copy()

# ============================================================
# TÍTULO Y RESUMEN
# ============================================================
st.title("🌳 Arborización en la Ciudad de Lima")
st.markdown(
    "Panel interactivo para explorar la evolución anual, mensual y distrital "
    "del programa de arborización de SERPAR Lima."
)

# El total del programa se recalcula con los meses elegidos para que responda al filtro.
meses_programa_validos = [m for m in meses_seleccionados if m in programa_f.columns]
if not programa_f.empty and meses_programa_validos:
    total_programa = int(programa_f[meses_programa_validos].sum(min_count=1).sum(skipna=True))
else:
    total_programa = 0

cumplimientos = programa_f["CUMPLIMIENTO"].dropna() if "CUMPLIMIENTO" in programa_f else pd.Series(dtype=float)
promedio_cumplimiento = float(cumplimientos.mean()) if not cumplimientos.empty else 0

if not distribucion_f.empty and distritos_seleccionados:
    suma_por_distrito = distribucion_f[distritos_seleccionados].sum(min_count=1).fillna(0)
    total_distrital = int(suma_por_distrito.sum())
    distritos_activos = int((suma_por_distrito > 0).sum())
    distrito_lider = str(suma_por_distrito.idxmax()) if distritos_activos else "Sin datos"
    cantidad_lider = int(suma_por_distrito.max()) if distritos_activos else 0
else:
    total_distrital, distritos_activos = 0, 0
    distrito_lider, cantidad_lider = "Sin datos", 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Árboles del programa", f"{total_programa:,}", help="Suma de los registros mensuales seleccionados en el archivo del programa.")
k2.metric("Cumplimiento promedio", f"{promedio_cumplimiento:.1f}%")
k3.metric("Distritos con registros", f"{distritos_activos}")
k4.metric("Distrito con mayor registro", distrito_lider, f"{cantidad_lider:,} árboles")

with st.expander("ℹ️ ¿De dónde salen estos indicadores?"):
    st.write(
        "Los árboles del programa y el cumplimiento provienen del archivo del programa de arborización. "
        "Los distritos y su ranking provienen del archivo de distribución por distrito. "
        "Se mantienen como fuentes separadas, sin combinar cifras de forma artificial."
    )

st.divider()

# ============================================================
# PESTAÑAS PRINCIPALES
# ============================================================
tab_resumen, tab_tiempo, tab_distritos, tab_datos = st.tabs(
    ["🏡 Resumen", "📅 Años y meses", "🏙️ Distritos", "📋 Datos"]
)

# ------------------------------------------------------------
# RESUMEN
# ------------------------------------------------------------
with tab_resumen:
    st.subheader("Panorama general")

    col_a, col_b = st.columns([1.3, 1])

    with col_a:
        st.markdown("**Evolución anual del programa**")
        tipo_anual = st.selectbox(
            "Presentación del gráfico anual",
            ["Barras", "Línea", "Área"],
            key="tipo_anual"
        )

        anual = (
            programa_f.dropna(subset=["AÑO"])
            .groupby("AÑO", as_index=False)["TOTAL_PLANTADO"]
            .sum(min_count=1)
            .sort_values("AÑO")
        )

        fig_anual = go.Figure()
        x_anual = anual["AÑO"].astype(int).astype(str).tolist()
        y_anual = anual["TOTAL_PLANTADO"].fillna(0).tolist()

        if tipo_anual == "Barras":
            fig_anual = figura_arboles_barras(x_anual, y_anual)
        elif tipo_anual == "Línea":
            fig_anual.add_trace(go.Scatter(
                x=x_anual, y=y_anual,
                mode="lines+markers+text",
                line=dict(color=GREEN_DARK, width=3, shape="spline"),
                marker=dict(size=11, color=GREEN_MID),
                text=["🌳"] * len(x_anual),
                textposition="top center",
                hovertemplate="Año %{x}<br>Árboles: %{y:,.0f}<extra></extra>"
            ))
        else:
            fig_anual.add_trace(go.Scatter(
                x=x_anual, y=y_anual,
                mode="lines+markers+text",
                line=dict(color=GREEN_DARK, width=3, shape="spline"),
                marker=dict(size=9, color=GREEN_MID),
                fill="tozeroy",
                fillcolor="rgba(183,205,187,0.35)",
                text=["🌳"] * len(x_anual),
                textposition="top center",
                hovertemplate="Año %{x}<br>Árboles: %{y:,.0f}<extra></extra>"
            ))

        fig_anual.update_layout(
            title="Árboles plantados por año",
            xaxis_title="Año",
            yaxis_title="Árboles",
            yaxis=dict(gridcolor=GRID)
        )
        estilo_figura(fig_anual, 420)
        st.plotly_chart(
            fig_anual,
            use_container_width=True,
            config={"displayModeBar": True, "scrollZoom": True}
        )

    with col_b:
        st.markdown("**Distribución de los registros por distrito**")
        if not distribucion_f.empty and distritos_seleccionados:
            ranking_resumen = (
                distribucion_f[distritos_seleccionados]
                .sum(min_count=1).fillna(0)
                .sort_values(ascending=False)
                .head(8)
                .reset_index()
            )
            ranking_resumen.columns = ["DISTRITO", "ÁRBOLES"]

            fig_dona = go.Figure(go.Pie(
                labels=ranking_resumen["DISTRITO"],
                values=ranking_resumen["ÁRBOLES"],
                hole=0.55,
                marker=dict(colors=PALETTE, line=dict(color=BG, width=2)),
                textinfo="percent",
                hovertemplate="%{label}<br>Árboles: %{value:,.0f}<br>%{percent}<extra></extra>"
            ))
            fig_dona.update_layout(
                title="Participación de los 8 principales distritos",
                showlegend=True,
                legend=dict(orientation="h", y=-0.12)
            )
            estilo_figura(fig_dona, 420)
            st.plotly_chart(
                fig_dona,
                use_container_width=True,
                config={"displayModeBar": True}
            )
        else:
            st.info("Selecciona al menos un distrito y un mes.")

    st.markdown("**Resumen por año**")
    resumen_anual = (
        programa_f.groupby("AÑO", as_index=False)
        .agg(
            Arboles_programa=("TOTAL_PLANTADO", "sum"),
            Cumplimiento_promedio=("CUMPLIMIENTO", "mean")
        )
    )
    resumen_anual["AÑO"] = resumen_anual["AÑO"].astype("Int64")
    st.dataframe(
        resumen_anual,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Arboles_programa": st.column_config.NumberColumn("Árboles del programa", format="%d"),
            "Cumplimiento_promedio": st.column_config.NumberColumn("Cumplimiento promedio", format="%.1f%%")
        }
    )

# ------------------------------------------------------------
# AÑOS Y MESES
# ------------------------------------------------------------
with tab_tiempo:
    st.subheader("Explora el comportamiento temporal")

    c1, c2 = st.columns(2)
    with c1:
        fuente_mensual = st.selectbox(
            "Fuente para el gráfico mensual",
            ["Programa de arborización", "Distribución por distrito"],
            key="fuente_mensual"
        )
    with c2:
        tipo_mensual = st.selectbox(
            "Tipo de gráfico mensual",
            ["Barras", "Línea", "Área"],
            key="tipo_mensual"
        )

    if fuente_mensual == "Programa de arborización":
        meses_validos = [m for m in meses_seleccionados if m in programa_f.columns]
        if not programa_f.empty and meses_validos:
            serie_mes = programa_f[meses_validos].sum(min_count=1)
            datos_mes = pd.DataFrame({
                "MES": meses_validos,
                "ÁRBOLES": [serie_mes.get(m, pd.NA) for m in meses_validos]
            }).dropna(subset=["ÁRBOLES"])
        else:
            datos_mes = pd.DataFrame(columns=["MES", "ÁRBOLES"])
    else:
        if not distribucion_f.empty and distritos_seleccionados:
            valores_mes = (
                distribucion_f.groupby("MES")[distritos_seleccionados]
                .sum(min_count=1)
                .sum(axis=1, min_count=1)
            )
            orden = {m: i for i, m in enumerate(MESES)}
            datos_mes = valores_mes.reset_index(name="ÁRBOLES")
            datos_mes["ORDEN"] = datos_mes["MES"].map(orden)
            datos_mes = datos_mes.sort_values("ORDEN")
        else:
            datos_mes = pd.DataFrame(columns=["MES", "ÁRBOLES"])

    if not datos_mes.empty:
        etiquetas = [MESES_ES.get(m, m.title()) for m in datos_mes["MES"]]
        valores = datos_mes["ÁRBOLES"].fillna(0).tolist()
        fig_mes = go.Figure()

        if tipo_mensual == "Barras":
            fig_mes = figura_arboles_barras(etiquetas, valores, color=GREEN_PALE)
        else:
            fig_mes.add_trace(go.Scatter(
                x=etiquetas,
                y=valores,
                mode="lines+markers+text",
                line=dict(
                    color=GREEN_DARK,
                    width=3,
                    shape="spline",
                    dash="solid"
                ),
                marker=dict(size=10, color=GREEN_MID),
                text=["🌳"] * len(etiquetas),
                textposition="top center",
                fill="tozeroy" if tipo_mensual == "Área" else None,
                fillcolor="rgba(183,205,187,0.30)" if tipo_mensual == "Área" else None,
                hovertemplate="%{x}<br>Árboles: %{y:,.0f}<extra></extra>"
            ))

        fig_mes.update_layout(
            title=f"Distribución mensual · {fuente_mensual}",
            xaxis_title="Mes",
            yaxis_title="Árboles registrados",
            yaxis=dict(gridcolor=GRID)
        )
        estilo_figura(fig_mes, 440)
        st.plotly_chart(
            fig_mes,
            use_container_width=True,
            config={"displayModeBar": True, "scrollZoom": True}
        )
    else:
        st.info("No hay datos mensuales en la selección actual. Prueba con otros años, meses o distritos.")

    st.divider()
    st.markdown("**Comparación entre años**")
    if not programa_f.empty:
        comparacion = (
            programa_f.groupby("AÑO", as_index=False)["TOTAL_PLANTADO"]
            .sum()
            .sort_values("AÑO")
        )
        comparacion["AÑO"] = comparacion["AÑO"].astype(int).astype(str)
        fig_comp = px.bar(
            comparacion,
            x="AÑO",
            y="TOTAL_PLANTADO",
            color="AÑO",
            color_discrete_sequence=PALETTE,
            text_auto=",.0f"
        )
        fig_comp.update_traces(
            textposition="outside",
            hovertemplate="Año %{x}<br>Árboles: %{y:,.0f}<extra></extra>"
        )
        fig_comp.update_layout(
            title="Comparación del total anual informado",
            xaxis_title="Año",
            yaxis_title="Árboles"
        )
        estilo_figura(fig_comp, 380)
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("No hay registros para comparar.")

# ------------------------------------------------------------
# DISTRITOS
# ------------------------------------------------------------
with tab_distritos:
    st.subheader("Compara los distritos de Lima")

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        top_n = st.slider(
            "Cantidad de distritos en el ranking",
            min_value=5,
            max_value=30,
            value=15,
            step=1
        )
    with col_b:
        tipo_distrito = st.selectbox(
            "Visualización del ranking",
            ["Barras horizontales", "Dona"],
            key="tipo_distrito"
        )
    with col_c:
        criterio = st.selectbox(
            "Orden del ranking",
            ["Mayor a menor", "Menor a mayor"],
            key="orden_distrito"
        )

    if not distribucion_f.empty and distritos_seleccionados:
        ranking = (
            distribucion_f[distritos_seleccionados]
            .sum(min_count=1).fillna(0)
            .sort_values(ascending=(criterio == "Menor a mayor"))
        )
        ranking = ranking.head(top_n) if criterio == "Menor a mayor" else ranking.head(top_n)
        ranking_df = ranking.reset_index()
        ranking_df.columns = ["DISTRITO", "ÁRBOLES"]

        if tipo_distrito == "Barras horizontales":
            ranking_orden = ranking_df.sort_values("ÁRBOLES", ascending=True)
            fig_ranking = figura_arboles_barras(
                ranking_orden["ÁRBOLES"].tolist(),
                ranking_orden["DISTRITO"].tolist(),
                orientacion="h"
            )
            fig_ranking.update_layout(
                title=f"Ranking de {len(ranking_df)} distritos",
                xaxis_title="Árboles registrados",
                yaxis_title=""
            )
        else:
            fig_ranking = go.Figure(go.Pie(
                labels=ranking_df["DISTRITO"],
                values=ranking_df["ÁRBOLES"],
                hole=0.48,
                marker=dict(colors=PALETTE, line=dict(color=BG, width=2)),
                hovertemplate="%{label}<br>Árboles: %{value:,.0f}<br>%{percent}<extra></extra>"
            ))
            fig_ranking.update_layout(title=f"Participación de {len(ranking_df)} distritos")

        estilo_figura(fig_ranking, 520)
        st.plotly_chart(
            fig_ranking,
            use_container_width=True,
            config={"displayModeBar": True, "scrollZoom": True}
        )

        st.markdown("**Comparación mensual de distritos seleccionados**")
        disponibles_comparacion = ranking_df["DISTRITO"].tolist()
        comparacion_distritos = st.multiselect(
            "Elige hasta 6 distritos para comparar",
            options=disponibles_comparacion,
            default=disponibles_comparacion[:4],
            max_selections=6,
            key="comparacion_distritos"
        )

        if comparacion_distritos:
            tabla_comparacion = (
                distribucion_f.groupby("MES")[comparacion_distritos]
                .sum(min_count=1)
                .reindex([m for m in MESES if m in distribucion_f["MES"].unique()])
            )
            fig_lineas = go.Figure()
            for i, distrito in enumerate(comparacion_distritos):
                valores = tabla_comparacion[distrito]
                fig_lineas.add_trace(go.Scatter(
                    x=[MESES_ES.get(m, m.title()) for m in tabla_comparacion.index],
                    y=valores,
                    mode="lines+markers+text",
                    name=distrito,
                    line=dict(color=PALETTE[i % len(PALETTE)], width=3, shape="spline"),
                    marker=dict(size=8),
                    text=["🌳" if pd.notna(v) else "" for v in valores],
                    textposition="top center",
                    connectgaps=False,
                    hovertemplate=distrito + "<br>%{x}<br>Árboles: %{y:,.0f}<extra></extra>"
                ))
            fig_lineas.update_layout(
                title="Evolución mensual por distrito",
                xaxis_title="Mes",
                yaxis_title="Árboles registrados",
                yaxis=dict(gridcolor=GRID),
                hovermode="x unified"
            )
            estilo_figura(fig_lineas, 440)
            st.plotly_chart(
                fig_lineas,
                use_container_width=True,
                config={"displayModeBar": True, "scrollZoom": True}
            )
        else:
            st.info("Selecciona al menos un distrito para realizar la comparación.")

        st.dataframe(
            ranking_df.sort_values("ÁRBOLES", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Selecciona al menos un distrito, año y mes con registros.")

# ------------------------------------------------------------
# DATOS Y DESCARGAS
# ------------------------------------------------------------
with tab_datos:
    st.subheader("Consulta y descarga de datos")
    opcion_tabla = st.radio(
        "Seleccionar tabla",
        ["Programa de arborización", "Distribución por distrito"],
        horizontal=True
    )

    if opcion_tabla == "Programa de arborización":
        tabla = programa_f.copy()
        busqueda = st.text_input("Buscar en la tabla del programa", placeholder="Escribe un año o dato...")
        if busqueda:
            mascara = tabla.astype(str).apply(
                lambda col: col.str.contains(busqueda, case=False, na=False)
            ).any(axis=1)
            tabla = tabla[mascara]
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        archivo_descarga = tabla.to_csv(index=False).encode("utf-8-sig")
        nombre_archivo = "programa_arborizacion_filtrado.csv"
    else:
        tabla = distribucion_f.copy()
        busqueda = st.text_input("Buscar un mes o distrito", placeholder="Escribe un mes o distrito...")
        if busqueda:
            mascara = tabla.astype(str).apply(
                lambda col: col.str.contains(busqueda, case=False, na=False)
            ).any(axis=1)
            tabla = tabla[mascara]
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        archivo_descarga = tabla.to_csv(index=False).encode("utf-8-sig")
        nombre_archivo = "distribucion_distritos_filtrada.csv"

    st.download_button(
        "⬇️ Descargar tabla filtrada en CSV",
        data=archivo_descarga,
        file_name=nombre_archivo,
        mime="text/csv"
    )

st.caption(
    "Fuente: archivos CSV de SERPAR Lima proporcionados para el proyecto. "
    "Los gráficos y métricas se actualizan con los filtros seleccionados."
)
