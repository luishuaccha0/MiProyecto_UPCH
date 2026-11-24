# Arborización en Lima · Huella Verde

Dashboard académico en **Python / Streamlit** inspirado en las siete plantillas facilitadas. No requiere Node, JavaScript ni un proyecto frontend separado. Los estilos y los pictogramas se generan desde cadenas de Python. Los datos originales están incluidos, sin alteraciones.

## Ejecutar en Windows (PowerShell o terminal de VS Code)

1. Descomprime el ZIP y abre la carpeta `MiProyecto_UPCH_web` en VS Code.
2. En la terminal, ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Abre la dirección `Local URL` que Streamlit imprime (normalmente `http://localhost:8501`). En Linux/macOS usa `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt` y `.venv/bin/python -m streamlit run streamlit_app.py`.

## Integración con GitHub y Streamlit Community Cloud

Copia `streamlit_app.py`, `datos_app.py`, `requirements.txt`, `.streamlit/config.toml`, `.gitignore` y la carpeta `datos/` al repositorio `MiProyecto_UPCH`. Conserva las rutas y nombres. Los dos CSV ya existentes son idénticos a los incluidos; puedes mantener los originales. Añade los cuatro Excel. Revisa los cambios con `git status`, confirma y publica cuando estés conforme. Si utilizas Streamlit Community Cloud, configura `streamlit_app.py` como archivo de entrada en la rama correspondiente. No es necesario subir `.venv` ni `__pycache__`.

## Secciones

- **Dashboard:** indicadores históricos, ranking 2026, estimaciones ambientales y navegación.
- **Evolución anual:** gráfica de arbolado y comparación con metas inferidas, más tarjetas de cumplimiento.
- **Mensual:** elección de año y fuente, gráfico de área y contraste mensual entre fuentes.
- **Distritos:** tarjetas con pictogramas, búsqueda sin tildes, filtros, orden y detalle mensual interactivo.
- **Bosque virtual:** escala y periodo configurables; el icono final tenue representa el resto exacto.
- **Huella Verde:** población, plantaciones, CO₂ respiratorio, O₂ y captura potencial; comparación de distritos y plantaciones por cada mil habitantes; metodología y exportación CSV.
- **Control de calidad:** tabla comparativa de fuentes y descarga, disponible al final de cada sección.

## Criterios de datos

Los cinco grupos autorizados son cuatro libros Excel 2023–2026 y el repositorio con dos CSV (seis archivos físicos). El Excel independiente de población descartado no se usa. El CSV del programa aporta las cifras históricas y los porcentajes; el CSV distrital aporta 42 distritos en 2026; los Excel aportan 43 distritos y datos ambientales. Se conservan los totales por separado. El reparto distrital 2023 es estimado; la captura de CO₂ 2023 no está disponible. O₂ de 2023 corresponde a los árboles plantados en ese mes, mientras que 2024–2026 se refiere a la cohorte anual acumulada. Las metas inferidas se calculan usando los porcentajes redondeados, no son metas oficiales. Los ceros y vacíos se mantienen distintos; la población mensual no se suma a través del tiempo. CO₂ respiratorio es biogénico, no emisión fósil neta; las cifras ambientales son teóricas, no mediciones ni compensaciones verificadas.

## Verificaciones locales

`python -m unittest -v test_datos.py` valida la lectura, dimensiones, agregaciones, diferencias entre fuentes, valores vacíos y semántica de 2023. La interfaz usa Streamlit >= 1.45. La verificación de datos y sintaxis se realizó antes de empaquetar; la ejecución visual en un navegador depende de instalar Streamlit.
