# app.py
import streamlit as st
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import io
import zipfile

# --- Page Config ---
st.set_page_config(page_title="GHS Bhutta Mohabbat Result System", layout="wide")

# --- Grade Calculation ---
def get_grade_info(percentage):
    if percentage >= 80: return "A+", "Excellent"
    elif percentage >= 70: return "A", "Very Good"
    elif percentage >= 60: return "B", "Good"
    elif percentage >= 50: return "C", "Satisfactory"
    elif percentage >= 40: return "D", "Fair"
    else: return "F", "Poor"

# --- PDF Generator (Old Result Card) ---
def generate_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Borders
    p.setStrokeColor(colors.HexColor("#7B96AC"))
    p.setLineWidth(2)
    p.rect(15, 15, width - 30, height - 30)
    p.setLineWidth(1)
    p.rect(20, 20, width - 40, height - 40)

    # Header
    p.setFont("Helvetica", 9)
    p.drawCentredString(width / 2 + 30, height - 45, "SCHOOL EDUCATION DEPARTMENT")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2 + 30, height - 62, data['school_name'].upper())
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width / 2 + 30, height - 75, f"EMIS CODE: {data['emis']} | DISTRICT {data['district'].upper()}")
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor("#7B96AC"))
    p.drawCentredString(width / 2, height - 115, "STUDENT REPORT CARD")

    # Logo
    if data['logo']:
        try:
            logo_reader = ImageReader(data['logo'])
            p.drawImage(logo_reader, 45, height - 105, width=65, height=65, mask='auto')
        except:
            pass

    # Session below logo
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, height - 130, f"Session {data['session']}")

    # Student Info
    info_data = [
        [f"NAME: {data['student_name'].upper()}", f"FATHER NAME: {data['father_name'].upper()}"],
        [f"CLASS: {data['class']}", f"ROLL NO: {data['roll']}", f"SECTION: {data['section']}"]
    ]
    t1 = Table(info_data[:1], colWidths=[275, 240])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7B96AC")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    t2 = Table(info_data[1:], colWidths=[175, 175, 165])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7B96AC")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    t1.wrapOn(p, 40, height - 160)
    t1.drawOn(p, 40, height - 160)
    t2.wrapOn(p, 40, height - 180)
    t2.drawOn(p, 40, height - 180)

    # Marks Table
    y_table = height - 215
    p.setFillColor(colors.HexColor("#333333"))
    p.rect(40, y_table, 515, 25, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(150, y_table + 8, "SUBJECT")
    p.drawString(350, y_table + 8, "TOTAL MARKS")
    p.drawString(460, y_table + 8, "OBTAINED")

    y_row = y_table - 22
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    grand_total_max, grand_total_obt = 0, 0
    for sub, info in data['marks_data'].items():
        p.rect(40, y_row, 515, 22)
        p.line(330, y_row, 330, y_row + 22); p.line(440, y_row, 440, y_row + 22)
        p.drawString(45, y_row + 7, sub)
        p.drawCentredString(385, y_row + 7, str(info['total']))
        p.drawCentredString(495, y_row + 7, str(info['obt']))
        grand_total_max += info['total']; grand_total_obt += info['obt']
        y_row -= 22

    # Grand Total
    p.setFont("Helvetica-Bold", 10)
    p.rect(40, y_row, 515, 22)
    p.drawString(45, y_row + 7, "GRAND TOTAL")
    p.drawCentredString(385, y_row + 7, str(grand_total_max))
    p.drawCentredString(495, y_row + 7, str(grand_total_obt))

    # Result Summary
    y_summary = y_row - 40
    perc = (grand_total_obt / grand_total_max * 100) if grand_total_max > 0 else 0
    grade, perf = get_grade_info(perc)
    box_w = 515 / 4
    for i, label in enumerate(["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]):
        val = [f"{perc:.1f}%", data['position'], data.get("performance", perf), grade][i]
        p.rect(40 + (i * box_w), y_summary, box_w, 30)
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(40 + (i * box_w) + (box_w/2), y_summary + 18, f"{label}: {val}")

    # Educational Quotes
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(width/2, 200, '"Education is the most powerful weapon which you can use to change the world."')
    p.drawCentredString(width/2, 180, '"The beautiful thing about learning is that no one can take it away from you."')

    # Signatures
    p.setFont("Helvetica-Bold", 9)
    p.line(80, 110, 210, 110); p.drawCentredString(145, 95, "CLASS TEACHER")
    p.line(width - 240, 110, width - 40, 110); p.drawCentredString(width - 140, 95, "SENIOR HEAD MASTER (SAFDAR JAVED)")
    p.setFont("Helvetica", 8); p.drawRightString(width - 40, 60, f"Result Declaration Date: {data['date']}")

    p.showPage(); p.save()
    buffer.seek(0)
    return buffer

# --- DATABASE SETUP ---
conn = sqlite3.connect("students.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS students
             (roll INTEGER PRIMARY KEY, name TEXT, father TEXT, class TEXT, section TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS marks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              roll INTEGER, subject TEXT, total INTEGER, obtained INTEGER, date TEXT)''')
conn.commit()

# --- Streamlit UI ---
st.title("GHS Bhutta Mohabbat Result System")
tab1, tab2 = st.tabs(["Single Student Result", "Daily/Bulk Marks"])
subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]

# --- Tab 1 ---
with tab1:
    st.header("Single Student Result Card")
    col1, col2, col3 = st.columns(3)
    school = col1.text_input("School Name", "Govt. High School Bhutta Mohabbat")
    emis = col2.text_input("EMIS Code", "39310025")
    dist = col3.text_input("District", "Okara")
    sess = st.text_input("Session", "2025-2026")
    logo = st.file_uploader("Upload Logo", type=["jpg","png","jpeg"])

    s_col1, s_col2, s_col3 = st.columns(3)
    s_name = s_col1.text_input("Student Name", "Faiz")
    f_name = s_col2.text_input("Father Name", "Sarwar")
    s_class = s_col3.text_input("Class", "9")
    roll = s_col1.text_input("Roll No", "12")
    sec = s_col2.text_input("Section", "A")
    pos = s_col3.text_input("Position", "---")
    perf = s_col3.text_input("Performance", "Good")

    st.subheader("Marks & Subjects")
    marks_data = {}
    for s in subs:
        c1, c2, c3 = st.columns([1,1,1])
        if c1.checkbox(f"Include {s}", value=True):
            t = c2.number_input(f"Total ({s})", 1, 100, 50, key=f"t{s}")
            o = c3.number_input(f"Obtained ({s})", 0, t, 40, key=f"o{s}")
            marks_data[s] = {"total": t, "obt": o}

    if st.button("Generate & Download PDF", key="single_pdf"):
        data = {"school_name": school, "emis": emis, "district": dist, "session": sess, "logo": logo,
                "student_name": s_name, "father_name": f_name, "class": s_class, "roll": roll, "section": sec,
                "position": pos, "performance": perf, "marks_data": marks_data, "date": "31-03-2026"}
        pdf_bytes = generate_pdf(data)
        st.download_button("Download PDF", pdf_bytes, f"Result_{s_name}.pdf", "application/pdf")

# --- Tab 2 ---
with tab2:
    st.header("Daily Marks Entry / Bulk PDF Generation")
    st.info("Use Roll No to select student or add new student if not exists")

    roll_input = st.text_input("Student Roll No")
    name_input = st.text_input("Student Name")
    father_input = st.text_input("Father Name")
    class_input = st.text_input("Class")
    section_input = st.text_input("Section")

    if st.button("Add/Update Student"):
        if roll_input and name_input:
            c.execute("INSERT OR REPLACE INTO students (roll, name, father, class, section) VALUES (?,?,?,?,?)",
                      (roll_input, name_input, father_input, class_input, section_input))
            conn.commit()
            st.success("Student info saved")

    st.subheader("Enter Marks for Today")
    today = st.date_input("Test Date")
    for s in subs:
        c1, c2, c3 = st.columns([1,1,1])
        total_marks = c2.number_input(f"Total ({s})", 1, 100, 50, key=f"b_t{s}")
        obtained_marks = c3.number_input(f"Obtained ({s})", 0, total_marks, 40, key=f"b_o{s}")
        if st.button(f"Save Marks ({s})", key=f"save_{s}"):
            if roll_input:
                c.execute("INSERT INTO marks (roll, subject, total, obtained, date) VALUES (?,?,?,?,?)",
                          (roll_input, s, total_marks, obtained_marks, str(today)))
                conn.commit()
                st.success(f"{s} marks saved for Roll {roll_input}")

    if st.button("Generate All Students PDFs"):
        c.execute("SELECT * FROM students")
        all_students = c.fetchall()
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
            for stu in all_students:
                roll, name, father, s_class, section = stu
                c.execute("SELECT subject, total, obtained FROM marks WHERE roll=?", (roll,))
                marks_rows = c.fetchall()
                marks_data = {r[0]: {"total": r[1], "obt": r[2]} for r in marks_rows}
                data = {"school_name": school, "emis": emis, "district": dist, "session": sess, "logo": logo,
                        "student_name": name, "father_name": father, "class": s_class, "roll": roll, "section": section,
                        "position": "---", "performance": "Good", "marks_data": marks_data, "date": "31-03-2026"}
                pdf_bytes = generate_pdf(data)
                zf.writestr(f"Result_{name}_{roll}.pdf", pdf_bytes.read())
        st.download_button("Download All PDFs (ZIP)", zip_buffer, "All_Results.zip")
