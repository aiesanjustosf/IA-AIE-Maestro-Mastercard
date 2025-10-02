import re
import datetime
import pdfplumber
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# === Utilidades ===
def to_float(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))

def format_money(x: float) -> str:
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# === Extracción Maestro/Mastercard Credicoop ===
def extract_resumen_from_bytes(pdf_bytes: bytes) -> pd.DataFrame:
    tmp_path = "_aie_input.pdf"
    with open(tmp_path, "wb") as f:
        f.write(pdf_bytes)

    # 21%: IVA s/Arancel + IVA s/DTO FIN ADQ CONT
    rx_iva21 = re.compile(
        r"IVA\s*(?:CRED\.FISC\.COMERCIO\s*S/ARANC|S/DTO\s*FIN\s*ADQ\s*CONT)\s*21,00%[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})",
        re.IGNORECASE,
    )
    rx_arancel = re.compile(r"ARANCEL[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})", re.IGNORECASE)

    # 10,5%: IVA L.25063 s/DTO F.OTOR + (opcional) IVA s/Costo Financiero 10,50%
    rx_iva105_l25063 = re.compile(
        r"IVA\s*CRED\.FISC\.COM\.L\.25063\s*S/DTO\s*F\.OTOR\s*10,50%[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})",
        re.IGNORECASE,
    )
    rx_iva105_costo = re.compile(
        r"IVA\s*S/COSTO\s*FINANCIERO\s*10,50%[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})",
        re.IGNORECASE,
    )

    # Percepciones IVA RG 2408 3,00% y 1,50%
    rx_perc_iva_30 = re.compile(
        r"PERCEPCI[ÓO]N\s*IVA\s*(?:R\.?\s*G\.?|RG)\s*2408\s*3,00\s*%[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})",
        re.IGNORECASE,
    )
    rx_perc_iva_15 = re.compile(
        r"PERCEPCI[ÓO]N\s*IVA\s*(?:R\.?\s*G\.?|RG)\s*2408\s*1,50\s*%[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})",
        re.IGNORECASE,
    )

    # Retenciones
    rx_ret_iibb = re.compile(r"RETENCION\s*ING\.?BRUTOS[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})", re.IGNORECASE)
    rx_ret_iva  = re.compile(r"RETENCI[ÓO]N\s*IVA[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})", re.IGNORECASE)
    rx_ret_gcias= re.compile(r"RETENCI[ÓO]N\s*(IMP\.?\s*GANANCIAS|GANANCIAS)[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2})", re.IGNORECASE)

    tot_arancel = tot_iva21 = tot_iva105 = 0.0
    tot_perc_iva_30 = tot_perc_iva_15 = 0.0
    tot_ret_iibb = tot_ret_iva = tot_ret_gcias = 0.0

    with pdfplumber.open(tmp_path) as pdf:
        for page in pdf.pages:
            txt = (page.extract_text() or "").replace("−", "-")

            # 21%
            for m in rx_arancel.finditer(txt):
                tot_arancel += to_float(m.group(1))
            for m in rx_iva21.finditer(txt):
                tot_iva21 += to_float(m.group(1))

            # 10,5%
            for m in rx_iva105_l25063.finditer(txt):
                tot_iva105 += to_float(m.group(1))
            for m in rx_iva105_costo.finditer(txt):
                tot_iva105 += to_float(m.group(1))

            # Percepciones IVA
            for m in rx_perc_iva_30.finditer(txt):
                tot_perc_iva_30 += to_float(m.group(1))
            for m in rx_perc_iva_15.finditer(txt):
                tot_perc_iva_15 += to_float(m.group(1))

            # Retenciones
            for m in rx_ret_iibb.finditer(txt):
                tot_ret_iibb += to_float(m.group(1))
            for m in rx_ret_iva.finditer(txt):
                tot_ret_iva += to_float(m.group(1))
            for m in rx_ret_gcias.finditer(txt):
                # el importe está en el primer grupo numérico después del literal
                val = m.group(0)
                num = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", val)
                if num:
                    tot_ret_gcias += to_float(num.group(1))

    base21  = round(tot_iva21 / 0.21, 2) if tot_iva21 else 0.0
    base105 = round(tot_iva105 / 0.105, 2) if tot_iva105 else 0.0
    percep_total = round(tot_perc_iva_30 + tot_perc_iva_15, 2)

    resumen = pd.DataFrame({
        "Concepto": [
            "Base Neto 21% (Arancel + DTO)",
            "IVA 21% Total",
            "Base Neto 10,5% (DTO L.25063 + Costo)",
            "IVA 10,5% Total",
            "Percepciones IVA (RG 2408 Total)",
            "Retenciones IIBB",
            "Retenciones IVA",
            "Retenciones Ganancias",
        ],
        "Monto Total": [
            round(base21, 2),
            round(tot_iva21, 2),
            round(base105, 2),
            round(tot_iva105, 2),
            percep_total,
            round(tot_ret_iibb, 2),
            round(tot_ret_iva, 2),
            round(tot_ret_gcias, 2),
        ],
    })
    return resumen


# === PDF ===
def build_report_pdf(resumen_df: pd.DataFrame, out_path: str, titulo: str):
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal = styles["Normal"]
    h2 = styles["Heading2"]

    doc = SimpleDocTemplate(out_path, pagesize=A4)
    story = []

    story.append(Paragraph(titulo, title_style))
    story.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Resumen de importes", h2))

    data = [["Concepto", "Monto ($)"]]
    for _, row in resumen_df.iterrows():
        data.append([row["Concepto"], format_money(float(row["Monto Total"]))])

    tbl = Table(data, colWidths=[360, 140])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#222")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f7f7f7"), colors.white]),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("TOPPADDING", (0,0), (-1,0), 6),
    ]))
    story.append(tbl)

    doc.build(story)
    return out_path
