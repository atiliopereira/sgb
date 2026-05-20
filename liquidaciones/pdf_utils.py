import os
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

LOGO_PATH = os.path.join(
    os.path.dirname(__file__), "static", "liquidaciones", "images", "logo_sgb.png"
)


def numero_a_letras(numero):
    """Convierte un número a su representación en letras en español (Guaraníes)"""
    # Conversión básica para guaraníes
    # Esta es una implementación simplificada

    unidades = [
        "",
        "uno",
        "dos",
        "tres",
        "cuatro",
        "cinco",
        "seis",
        "siete",
        "ocho",
        "nueve",
    ]
    decenas = [
        "",
        "diez",
        "veinte",
        "treinta",
        "cuarenta",
        "cincuenta",
        "sesenta",
        "setenta",
        "ochenta",
        "noventa",
    ]
    centenas = [
        "",
        "ciento",
        "doscientos",
        "trescientos",
        "cuatrocientos",
        "quinientos",
        "seiscientos",
        "setecientos",
        "ochocientos",
        "novecientos",
    ]

    especiales = {
        11: "once",
        12: "doce",
        13: "trece",
        14: "catorce",
        15: "quince",
        16: "dieciséis",
        17: "diecisiete",
        18: "dieciocho",
        19: "diecinueve",
        21: "veintiuno",
        22: "veintidós",
        23: "veintitrés",
        24: "veinticuatro",
        25: "veinticinco",
        26: "veintiséis",
        27: "veintisiete",
        28: "veintiocho",
        29: "veintinueve",
    }

    def convertir_grupo(n):
        if n == 0:
            return ""
        elif n in especiales:
            return especiales[n]
        elif n < 10:
            return unidades[n]
        elif n < 20:
            return decenas[1]
        elif n < 30:
            return especiales.get(n, "veinti" + unidades[n % 10])
        elif n < 100:
            u = n % 10
            d = n // 10
            if u == 0:
                return decenas[d]
            return decenas[d] + " y " + unidades[u]
        elif n < 1000:
            c = n // 100
            resto = n % 100
            if n == 100:
                return "cien"
            if resto == 0:
                return centenas[c]
            return centenas[c] + " " + convertir_grupo(resto)
        return ""

    if numero == 0:
        return "cero"

    # Convertir a entero si es Decimal
    if isinstance(numero, Decimal):
        numero = int(numero)

    numero = int(numero)

    # Dividir en grupos de miles
    millones = numero // 1000000
    miles = (numero % 1000000) // 1000
    unidades_simples = numero % 1000

    resultado = []

    if millones > 0:
        if millones == 1:
            resultado.append("un millón")
        else:
            resultado.append(convertir_grupo(millones) + " millones")

    if miles > 0:
        if miles == 1:
            resultado.append("mil")
        else:
            resultado.append(convertir_grupo(miles) + " mil")

    if unidades_simples > 0:
        resultado.append(convertir_grupo(unidades_simples))

    return ", ".join(resultado) if resultado else "cero"


def generar_pdf_liquidacion(liquidacion, buffer=None):
    """Genera un PDF de la liquidación con el formato de SGB"""

    if buffer is None:
        buffer = BytesIO()

    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo para el encabezado
    style_header = ParagraphStyle(
        "CustomHeader",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    style_subheader = ParagraphStyle(
        "CustomSubHeader",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    style_address = ParagraphStyle(
        "CustomAddress",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.black,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName="Helvetica",
    )

    style_normal = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName="Helvetica",
    )

    style_bold = ParagraphStyle(
        "CustomBold",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName="Helvetica-Bold",
    )

    # Contenido del PDF
    story = []

    # Encabezado de la empresa - usar imagen si existe, sino texto
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=6.5 * inch, height=1.0 * inch)
        story.append(logo)
    else:
        story.append(Paragraph("AGENCIA ADUANERA SGB", style_header))
        story.append(Paragraph("GAVILAN BALOVIER & ASOCIADOS", style_subheader))
        story.append(Paragraph("DESPACHANTES DE ADUANAS", style_subheader))
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            Paragraph(
                "<b>ASUNCIÓN:</b> Montevideo 173 - Edif. Boquerón - 3er Piso Ofic. 302 - Telefax: 496 890 / 445 257",
                style_address,
            )
        )
        story.append(
            Paragraph(
                "<b>CIUDAD DEL ESTE:</b> Curupayty y Adrian Jara - Edif. Oriental - 2do Piso Ofic. 203 - Telefax: 061 511 229 / 501 553",
                style_address,
            )
        )
    story.append(Spacer(1, 0.2 * inch))

    # Línea separadora
    story.append(Spacer(1, 0.1 * inch))

    # Fecha
    meses_es = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }
    mes = meses_es[liquidacion.fecha.month]
    fecha_texto = f"Asunción, {liquidacion.fecha.strftime('%d')} de {mes} de {liquidacion.fecha.strftime('%Y')}"
    story.append(Paragraph(fecha_texto, style_normal))
    story.append(Spacer(1, 0.2 * inch))

    # Información del cliente y liquidación en dos columnas
    info_data = [
        [
            Paragraph("", style_normal),
            Paragraph("Liquidación Nº:", style_bold),
            Paragraph(liquidacion.numero_liquidacion or "S/N", style_normal),
        ],
        [
            Paragraph("Sr. (es)", style_normal),
            Paragraph("Proforma Nº:", style_bold),
            Paragraph(liquidacion.proforma or "S/N", style_normal),
        ],
        [
            Paragraph(f"<b>{liquidacion.cliente.nombre}</b>", style_normal),
            Paragraph("Orden de Compra Nº:", style_bold),
            Paragraph(liquidacion.orden_de_compra or "S/N", style_normal),
        ],
        [
            Paragraph("Presente:", style_normal),
            Paragraph("Despacho Nº:", style_bold),
            Paragraph(liquidacion.numero_despacho or "S/N", style_normal),
        ],
        [
            Paragraph("", style_normal),
            Paragraph("Clase:", style_bold),
            Paragraph(liquidacion.get_clase_display(), style_normal),
        ],
        [
            Paragraph("", style_normal),
            Paragraph("Factura Comercial Nº:", style_bold),
            Paragraph(liquidacion.numero_factura_comercial or "S/N", style_normal),
        ],
    ]

    info_table = Table(info_data, colWidths=[2.5 * inch, 1.5 * inch, 2 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (2, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(info_table)
    story.append(Spacer(1, 0.3 * inch))

    # Tabla de items
    items_liquidacion = liquidacion.liquidacionitem_set.all()
    has_retenciones = any(item.retencion for item in items_liquidacion)

    if has_retenciones:
        items_data = [["", "", "Sub-Total", "I.V.A.", "Retención", "Total"]]
    else:
        items_data = [["", "", "Sub-Total", "I.V.A.", "Total"]]

    style_item = ParagraphStyle(
        "ItemDesc",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        leading=11,
    )

    for item_liq in items_liquidacion:
        descripcion = Paragraph(item_liq.item or "", style_item)
        subtotal = f"{item_liq.monto:,.0f}".replace(",", ".")
        iva = f"{item_liq.iva:,.0f}".replace(",", ".") if item_liq.iva else ""
        total = f"{item_liq.subtotal:,.0f}".replace(",", ".")
        if has_retenciones:
            retencion = (
                f"{item_liq.retencion:,.0f}".replace(",", ".")
                if item_liq.retencion
                else ""
            )
            items_data.append([descripcion, "Gs.", subtotal, iva, retencion, total])
        else:
            items_data.append([descripcion, "Gs.", subtotal, iva, total])

    # Total
    total_subtotal = sum(item.monto or 0 for item in items_liquidacion)
    total_iva = sum(item.iva or 0 for item in items_liquidacion)
    total_retencion = sum(item.retencion or 0 for item in items_liquidacion)
    total_general = sum(item.subtotal or 0 for item in items_liquidacion)

    if has_retenciones:
        items_data.append(
            [
                "TOTAL",
                "Gs.",
                f"{total_subtotal:,.0f}".replace(",", "."),
                f"{total_iva:,.0f}".replace(",", "."),
                f"{total_retencion:,.0f}".replace(",", "."),
                f"{total_general:,.0f}".replace(",", "."),
            ]
        )
        # 7.4" usable: description gets the rest, numeric cols 1.3" each
        col_widths = [
            2.6 * inch,
            0.3 * inch,
            1.2 * inch,
            0.9 * inch,
            1.2 * inch,
            1.2 * inch,
        ]
    else:
        items_data.append(
            [
                "TOTAL",
                "Gs.",
                f"{total_subtotal:,.0f}".replace(",", "."),
                f"{total_iva:,.0f}".replace(",", "."),
                f"{total_general:,.0f}".replace(",", "."),
            ]
        )
        # 7.4" usable: description gets the rest, numeric cols 1.6" each
        col_widths = [
            2.6 * inch,
            0.3 * inch,
            1.6 * inch,
            1.3 * inch,
            1.6 * inch,
        ]

    items_table = Table(items_data, colWidths=col_widths)
    items_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.black),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
            ]
        )
    )

    story.append(items_table)
    story.append(Spacer(1, 0.1 * inch))

    # Total en letras
    total_letras = numero_a_letras(total_general)
    story.append(Paragraph(f"SON GUARANIES: {total_letras.title()}.-", style_bold))
    story.append(Spacer(1, 0.2 * inch))

    # Marca y detalle del contenido
    story.append(
        Paragraph("<b>MARCA - Nº DE BULTOS - DETALLE DEL CONTENIDO</b>", style_bold)
    )
    detalle_contenido = (
        liquidacion.detalle_de_contenido or "Mercadería según factura comercial"
    )
    story.append(Paragraph(f"01) {detalle_contenido}.-", style_normal))
    story.append(Spacer(1, 0.2 * inch))

    # Información adicional en dos columnas
    detalle_data = [
        [
            "Partida Arancelaria:",
            liquidacion.partida_arancelaria or "",
            "Factura:",
            f"{liquidacion.factura:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            if liquidacion.factura
            else "",
        ],
        [
            "Ad. Val.:",
            liquidacion.ad_valorem or "",
            "Flete:",
            f"{liquidacion.flete:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            if liquidacion.flete
            else "",
        ],
        [
            "Valor Imponible en " + liquidacion.moneda_valor_imponible + ":",
            f"{liquidacion.valor_imponible:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            if liquidacion.valor_imponible
            else "",
            "Seguro:",
            f"{liquidacion.seguro:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            if liquidacion.seguro
            else "",
        ],
        [
            "Equivalente a GS.:",
            f"{liquidacion.equivalente_gs:,.0f}".replace(",", ".")
            if liquidacion.equivalente_gs
            else "",
            "V.I.:",
            f"{liquidacion.valor_imponible:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            if liquidacion.valor_imponible
            else "",
        ],
        [
            "T.C. " + liquidacion.moneda_valor_imponible + ":",
            liquidacion.tipo_cambio or "",
            "",
            "",
        ],
        ["Origen / Procedencia:", liquidacion.procedencia or "", "", ""],
        [
            "Proveedor:",
            liquidacion.proveedor.nombre if liquidacion.proveedor else "",
            "",
            "",
        ],
    ]

    detalle_table = Table(
        detalle_data, colWidths=[2 * inch, 2.8 * inch, 1 * inch, 1.2 * inch]
    )
    detalle_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(detalle_table)
    story.append(Spacer(1, 0.4 * inch))

    # Firmas
    firmas_data = [
        ["Elaborado por:", "Verificado y Autorizado por:"],
        ["", ""],
        ["Ivan G. Gavilán", "Carmen Jiménez."],
        ["Despachante.", "Jefa de Operaciones."],
    ]

    firmas_table = Table(firmas_data, colWidths=[3 * inch, 3 * inch])
    firmas_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(firmas_table)

    # Construir el PDF
    doc.build(story)

    buffer.seek(0)
    return buffer
