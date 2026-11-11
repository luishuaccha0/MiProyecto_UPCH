
import streamlit as st
import pandas as pd
import numpy as np
from datetime import time
import datetime

# TITULO
st.title("Mi primer Dashboard")
st.write("Bienvenido a mi aplicación")

# 4.1 SLIDER NUMERICO
st.header("1. Slider numerico")

num = st.slider("Selecciona un numero", 0, 100, step=1)

st.write("El numero ingresado es:", num)

# 4.2 SLIDER DE HORARIO
st.header("2. Slider de horario")

appointment = st.slider(
    "Programe la asesoria:",
    value=(time(11, 30), time(12, 45))
)

st.write("Horario seleccionado:", appointment)

# 4.3 SELECTOR DE FECHAS
st.header("3. Selector de fechas")

d = st.date_input(
    "Selecciona una fecha",
    datetime.date(2026, 11, 11)
)

st.write("Fecha seleccionada:", d)

# 4.4 LISTA DE SELECCION
st.header("4. Lista de seleccion")

option = st.selectbox(
    "Como deseas ser contactado?",
    ("Email", "Telefono", "WhatsApp")
)

st.write("Seleccionaste:", option)

# 4.5 GRAFICO DE LINEAS
st.header("5. Grafico de lineas")

n = st.slider(
    "Cantidad de datos",
    5, 100, step=1
)

chart_data = pd.DataFrame(
    np.random.randn(n),
    columns=["data"]
)

st.line_chart(chart_data)

# 4.6 MAPA
st.header("6. Mapa")

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=["lat", "lon"]
)

st.map(df)