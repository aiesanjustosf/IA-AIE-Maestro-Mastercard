import os
import re
import streamlit as st
from backend import extract_resumen_from_bytes, build_report_pdf, format_money

APP_TITLE = "IA AIE - Control Tarjeta Maestro/Mastercard Débito/Crédito Credicoop"
PAGE_ICON = "logo_aie.png"   # mismo archivo sirve como favicon y logo
MAX_MB    = 50

st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout="centered")

# Encabezado con logo y título
left, right = st.columns([1, 3])
with left:
    if os.path.exists(PAGE_ICON):
        st.image(PAGE_ICON, width=80)   # Logo al costado
with right:
    st.title(APP_TITLE)
    st.caption("Procesar resúmenes automáticos Maestro/Mastercard del Banco Credicoop")

st.markdown('<hr style="margin:8px 0 20px 0;">', unsafe_allow_html=True)

pdf_file = st.file_uploader("📄 PDF de Maestro/Mastercard Credicoop", type=["pdf"])

if st.button("Procesar y generar informe") and pdf_file is not None:
    size_mb = len(pdf_file.getvalue()) / (1024 * 1024)
    if size_mb > MAX_MB:
        st.error(f"El archivo supera {MAX_MB} MB.")
    else:
        with st.spinner("Procesando..."):
            # 1) Usar backend para extraer resumen
            resumen = extract_resumen_from_bytes(pdf_file.getvalue())

            # 2) Ocultar fila '-IVA ...' si existiera
            mask_menos_iva = resumen["Concepto"].str.contains(
                r"^\s*[−-]\s*IVA\b", flags=re.IGNORECASE, regex=True
            )
            resumen_filtrado = resumen.loc[~mask_menos_iva].reset_index(drop=True)

            # 3) Mostrar con separador de miles
            df_display = resumen_filtrado.copy()
            col_monto = "Monto Total" if "Monto Total" in df_display.columns else "Monto"
            if col_monto in df_display.columns:
                df_display[col_monto] = df_display[col_monto].apply(format_money)

            st.subheader("Resumen de importes")
            st.dataframe(df_display, use_container_width=True)

            # 4) Generar PDF
            out_path = "IA_AIE_Resumen_de_Importes_Maestro.pdf"
            build_report_pdf(resumen_filtrado, out_path, titulo="Resumen de importes")
            with open(out_path, "rb") as f:
                st.download_button(
                    "⬇️ Descargar informe PDF", f, file_name=out_path, mime="application/pdf"
                )

            try:
                os.remove(out_path)
            except OSError:
                pass

