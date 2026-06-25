"""
QR code generation, visitor badge, and PDF pass utilities.
"""

import qrcode
import io
import os
import base64
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz

LAGOS_TZ = pytz.timezone("Africa/Lagos")


def generate_qr_code(data: str, size: int = 200) -> bytes:
    """Generate QR code PNG bytes for given data string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a2744", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def qr_to_base64(data: str) -> str:
    """Return base64-encoded QR PNG for embedding in HTML."""
    return base64.b64encode(generate_qr_code(data)).decode()


def decode_qr_from_image(image_bytes: bytes) -> str | None:
    """Try to decode a QR code from uploaded image bytes using pyzbar."""
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
        import numpy as np
        import cv2
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        decoded = pyzbar_decode(img)
        if decoded:
            return decoded[0].data.decode("utf-8")
    except Exception:
        pass
    return None


def generate_visitor_badge(visitor: dict) -> bytes:
    """
    Generate a professional visitor badge as PNG bytes.
    Returns PNG image bytes.
    """
    W, H = 520, 720
    img = Image.new("RGB", (W, H), color="#f8fafc")
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([0, 0, W, 130], fill="#1a2744")
    # Accent strip
    draw.rectangle([0, 130, W, 140], fill="#22c55e")

    # Try to load a font, fall back to default
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_med   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_tiny  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font_title = font_large = font_med = font_small = font_tiny = ImageFont.load_default()

    # Header text
    draw.text((W // 2, 35), "VISITOR PASS", fill="white", font=font_title, anchor="mm")
    draw.text((W // 2, 70), "Smart Visitor Management System", fill="#94a3b8", font=font_small, anchor="mm")
    draw.text((W // 2, 100), "AUTHORIZED ENTRY", fill="#22c55e", font=font_med, anchor="mm")

    # Photo area
    photo_box = [30, 155, 170, 295]
    draw.rectangle(photo_box, fill="#e2e8f0", outline="#cbd5e1", width=2)
    photo_loaded = False
    if visitor.get("photo_path") and os.path.exists(visitor["photo_path"]):
        try:
            ph = Image.open(visitor["photo_path"]).convert("RGB")
            ph = ph.resize((140, 140), Image.LANCZOS)
            img.paste(ph, (30, 155))
            photo_loaded = True
        except Exception:
            pass
    if not photo_loaded:
        draw.text((100, 225), "PHOTO", fill="#94a3b8", font=font_med, anchor="mm")

    # Status badge
    status = visitor.get("status", "Pending")
    status_colors = {
        "Approved": "#22c55e", "Pending": "#f59e0b",
        "Rejected": "#ef4444", "Checked Out": "#3b82f6"
    }
    sc = status_colors.get(status, "#6b7280")
    draw.rectangle([185, 155, 490, 185], fill=sc, outline=sc)
    draw.text((337, 170), status.upper(), fill="white", font=font_large, anchor="mm")

    # Visitor info
    y = 200
    info_pairs = [
        ("Visitor No:", visitor.get("visitor_number", "")),
        ("Name:", visitor.get("full_name", "")),
        ("Host:", visitor.get("person_to_visit", "")),
        ("Department:", visitor.get("department", "")),
        ("Purpose:", visitor.get("purpose", "")),
        ("Date:", visitor.get("entry_date", "")),
        ("Entry Time:", visitor.get("entry_time", "")),
    ]
    for label, value in info_pairs:
        draw.text((185, y), label, fill="#64748b", font=font_small)
        draw.text((280, y), str(value)[:30], fill="#1a2744", font=font_small)
        y += 22

    # Divider
    draw.rectangle([20, 310, W - 20, 312], fill="#e2e8f0")

    # QR Code
    qr_data = visitor.get("barcode_id", visitor.get("visitor_number", "N/A"))
    qr_bytes = generate_qr_code(qr_data, size=160)
    qr_img = Image.open(io.BytesIO(qr_bytes)).resize((160, 160), Image.LANCZOS)
    img.paste(qr_img, (W // 2 - 80, 325))

    draw.text((W // 2, 495), "Scan to Verify", fill="#64748b", font=font_small, anchor="mm")
    draw.text((W // 2, 515), qr_data, fill="#1a2744", font=font_tiny, anchor="mm")

    # ID info
    draw.rectangle([20, 535, W - 20, 537], fill="#e2e8f0")
    draw.text((W // 2, 555), f"ID: {visitor.get('id_type','N/A')}  •  {visitor.get('id_number','N/A')}", fill="#64748b", font=font_small, anchor="mm")

    # Footer
    draw.rectangle([0, 590, W, H], fill="#1a2744")
    draw.text((W // 2, 620), "This pass must be worn visibly at all times", fill="#94a3b8", font=font_tiny, anchor="mm")
    draw.text((W // 2, 640), "Report to Security on exit • Unauthorized duplication prohibited", fill="#64748b", font=font_tiny, anchor="mm")
    now_str = datetime.now(LAGOS_TZ).strftime("%d %b %Y %H:%M")
    draw.text((W // 2, 660), f"Generated: {now_str} WAT", fill="#475569", font=font_tiny, anchor="mm")
    draw.rectangle([0, 680, W, H], fill="#22c55e")
    draw.text((W // 2, 693), "Smart VMS  •  Cardstel Solutions Limited", fill="#1a2744", font=font_tiny, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(150, 150))
    return buf.getvalue()


def generate_visitor_pdf(visitor: dict) -> bytes:
    """Generate a PDF visitor pass using reportlab."""
    from reportlab.lib.pagesizes import A6
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A6, leftMargin=8*mm, rightMargin=8*mm,
                            topMargin=6*mm, bottomMargin=6*mm)
    styles = getSampleStyleSheet()
    navy = colors.HexColor("#1a2744")
    green = colors.HexColor("#22c55e")
    light = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle("title", parent=styles["Title"],
        fontSize=14, textColor=colors.white, alignment=TA_CENTER,
        spaceAfter=2, fontName="Helvetica-Bold")
    sub_style   = ParagraphStyle("sub", parent=styles["Normal"],
        fontSize=7, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    label_style = ParagraphStyle("label", parent=styles["Normal"],
        fontSize=7, textColor=colors.HexColor("#64748b"), fontName="Helvetica-Bold")
    value_style = ParagraphStyle("value", parent=styles["Normal"],
        fontSize=7, textColor=navy, fontName="Helvetica")

    story = []

    # Header block
    header_data = [[
        Paragraph("VISITOR PASS", title_style),
    ]]
    header_table = Table(header_data, colWidths=[105*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), navy),
        ("TOPPADDING",  (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(header_table)

    # Status strip
    status = visitor.get("status", "Pending")
    status_col = {"Approved": "#22c55e", "Pending": "#f59e0b",
                  "Rejected": "#ef4444", "Checked Out": "#3b82f6"}.get(status, "#6b7280")
    st_style = ParagraphStyle("st", parent=styles["Normal"],
        fontSize=9, textColor=colors.white, alignment=TA_CENTER, fontName="Helvetica-Bold")
    st_data = [[Paragraph(status.upper(), st_style)]]
    st_table = Table(st_data, colWidths=[105*mm])
    st_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor(status_col)),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 3*mm))

    # Info table
    fields = [
        ("Visitor No", visitor.get("visitor_number", "")),
        ("Full Name",  visitor.get("full_name", "")),
        ("Host",       visitor.get("person_to_visit", "")),
        ("Department", visitor.get("department", "")),
        ("Purpose",    visitor.get("purpose", "")),
        ("ID Type",    visitor.get("id_type", "")),
        ("ID Number",  visitor.get("id_number", "")),
        ("Entry Date", visitor.get("entry_date", "")),
        ("Entry Time", visitor.get("entry_time", "")),
    ]
    rows_data = [[Paragraph(k, label_style), Paragraph(str(v), value_style)] for k, v in fields]
    info_table = Table(rows_data, colWidths=[30*mm, 73*mm])
    info_table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [light, colors.white]),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,-1), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 4*mm))

    # QR code
    qr_data = visitor.get("barcode_id", visitor.get("visitor_number", "N/A"))
    qr_bytes = generate_qr_code(qr_data)
    qr_img_buf = io.BytesIO(qr_bytes)
    qr_rl = RLImage(qr_img_buf, width=28*mm, height=28*mm)
    qr_table = Table([[qr_rl]], colWidths=[105*mm])
    qr_table.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "CENTER")]))
    story.append(qr_table)

    qr_note = ParagraphStyle("qrn", parent=styles["Normal"], fontSize=6,
                              textColor=colors.HexColor("#64748b"), alignment=TA_CENTER)
    story.append(Paragraph(f"Scan to verify  •  {qr_data}", qrn := qr_note))
    story.append(Spacer(1, 3*mm))

    # Footer
    footer_data = [[Paragraph(
        "Wear this pass visibly at all times. Report to Security on exit.",
        ParagraphStyle("ft", parent=styles["Normal"], fontSize=6,
                       textColor=colors.white, alignment=TA_CENTER))]]
    ft_table = Table(footer_data, colWidths=[105*mm])
    ft_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), navy),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(ft_table)

    doc.build(story)
    return buf.getvalue()
