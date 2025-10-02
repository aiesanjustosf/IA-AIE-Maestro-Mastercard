# IA AIE - Control Tarjeta Maestro/Mastercard Débito/Crédito Credicoop

App Streamlit para resumir importes de liquidaciones Maestro/Mastercard (Banco Credicoop).

## Cubre
- **IVA 21%**: `IVA CRED.FISC.COMERCIO S/ARANC 21,00%` **y** `IVA S/DTO FIN ADQ CONT 21,00%` (base = IVA / 0,21).
- **IVA 10,5%**: `IVA CRED.FISC.COM.L.25063 S/DTO F.OTOR 10,50%` y (si aparece) `IVA S/COSTO FINANCIERO 10,50%` (base = IVA / 0,105).
- **Percepciones IVA RG 2408**: suma de **3,00%** y **1,50%**.
- **Retenciones**: IIBB, IVA, Ganancias.
- Oculta la fila **-IVA (21% en Débitos al Comercio)** si existiera.

## Archivos
- `app.py` — UI y exportación de PDF (logo al lado del título y como favicon).
- `backend.py` — extracción y sumatoria con regex adaptadas.
- `requirements.txt` — dependencias.
- `logo_aie.png` — favicon/logo (reemplazá por tu logo real).
- `.streamlit/config.toml` — tema de la app.

## Deploy
1. Subí estos archivos a un repo en GitHub.
2. En Streamlit Cloud: New app → elegí el repo → Main file: `app.py` → Deploy.

## Notas
- Si el banco cambia leyendas, ajustá las regex en `backend.py`.
