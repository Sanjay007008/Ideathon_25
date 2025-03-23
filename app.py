import os
import cv2
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
import jade

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "output_images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not allowed_file(file.filename):
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        localized_image_path = jade.process_image(file_path)

        patient_info = {
            "Patient Name": request.form.get("patient_name"),
        }

        features = {
            "Pregnancies": request.form.get("pregnancies"),
            "Glucose": request.form.get("glucose"),
            "Blood Pressure": request.form.get("blood_pressure"),
            "Skin Thickness": request.form.get("skin_thickness"),
            "Insulin": request.form.get("insulin"),
            "BMI": request.form.get("bmi"),
            "Diabetes Pedigree": request.form.get("diabetes_pedigree"),
        }

        diagnosis = "Diabetic" if float(request.form.get("glucose")) > 140 else "Non-Diabetic"
        pdf_path = generate_pdf(patient_info, features, diagnosis, localized_image_path)
        return send_file(pdf_path, as_attachment=True)

    return render_template("index.html")

def generate_pdf(patient_info, features, diagnosis, optic_disc_image):
    pdf_path = os.path.join(OUTPUT_FOLDER, "Doctor_Report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, height - 50, "Diabetic Retinopathy Report")

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

    c.save()
    return pdf_path

if __name__ == "__main__":
    app.run(debug=True)