# IA AIE - Control Tarjeta Maestro/Mastercard Débito/Crédito Credicoop

App Streamlit para resumir importes de liquidaciones Maestro/Mastercard (Banco Credicoop).

## Qué hace
- Extrae y suma: **Arancel**, **IVA 21% sobre arancel**, **Retenciones IIBB**, **Retenciones IVA**, **Retenciones Ganancias**, **Percepciones IVA (RG 2408 3,00%)**.
- **Oculta** la fila “−IVA (21% en Débitos al Comercio)” si existiera.
- Muestra números con **punto** como miles y **coma** como decimales.
- Genera un PDF con el título **Resumen de importes**.

## Estructura
- `app.py` — UI y exportación de PDF.
- `backend.py` — extracción y suma de importes (regex adaptadas a Credicoop Maestro/Mastercard).
- `requirements.txt` — dependencias.
- `logo_aie.png` — favicon/logo (placeholder, podés reemplazar por tu logo).
- `.streamlit/config.toml` — (opcional) tema de la app.

## Deploy (Streamlit Cloud)
1. Crear repo nuevo (por ej. `ia-aie-maestro-credicoop`).
2. Subir estos archivos.
3. En Streamlit Cloud: **New app** → elegí el repo → Main file path: `app.py` → Deploy.

## Nota
Si el banco cambia el texto de líneas (ej. otro RG de percepción), habrá que ajustar las regex en `backend.py`.
