from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
import os

def generate_pdf(patient_info, features, diagnosis, optic_disc_image):
    pdf_path = "output_images/Doctor_Report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Diabetic Retinopathy Report")

    # Patient Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, "Patient Information:")
    
    c.setFont("Helvetica", 11)
    y_pos = height - 120
    for key, value in patient_info.items():
        c.drawString(70, y_pos, f"{key}: {value}")
        y_pos -= 20

    # Diagnosis Result
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos - 20, "Diagnosis Result:")
    c.setFont("Helvetica", 11)
    c.drawString(70, y_pos - 40, f"The patient is classified as: {diagnosis}")
    y_pos -= 60

    # Features Table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "Clinical Features:")
    y_pos -= 20
    
    table_data = [["Feature", "Value"]]
    for key, value in features.items():
        table_data.append([key, str(value)])

    table = Table(table_data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y_pos - (len(features) * 20) - 40)
    y_pos -= (len(features) * 20) + 80

    # Optic Disc Image
    if os.path.exists(optic_disc_image):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "Optic Disc Localization:")
        y_pos -= 150
        c.drawImage(ImageReader(optic_disc_image), 200, y_pos, width=180, height=180)

    # Doctor's Signature (Left Aligned)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos - 100, "Doctor's Signature:")
    doctor_sign = "static/images/signature.png"
    if os.path.exists(doctor_sign):
        c.drawImage(ImageReader(doctor_sign), 50, y_pos - 130, width=120, height=50)

    c.save()
    print(f"PDF saved at: {pdf_path}")
    return pdf_path
