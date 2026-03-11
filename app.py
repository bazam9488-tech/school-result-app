# app.py
import streamlit as st
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import io
import zipfile

st.set_page_config(page_title="GHS Bhutta Mohabbat Result System", layout="wide")

# --- Database ---
conn = sqlite3.connect("students.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS students
             (roll INTEGER PRIMARY KEY, name TEXT, father TEXT, class TEXT, section TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS marks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              roll INTEGER, subject TEXT, total INTEGER, obtained INTEGER, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS teachers
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE, assigned_class TEXT)''')
conn.commit()

# --- Grade Calculation ---
def get_grade_info(percentage):
    if percentage >= 80: return "A+", "Excellent"
    elif percentage >= 70: return "A", "Very Good"
    elif percentage >= 60: return "B", "Good"
    elif percentage >= 50: return "C", "Satisfactory"
    elif percentage >= 40: return "D", "Fair"
    else: return "F", "Poor"

# --- PDF Generator ---
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

# --- UI ---
st.title("GHS Bhutta Mohabbat Result System")

subs = ["English","Urdu","Mathematics","Islamiat","Science","Social Study","Computer","Tarjuma-tu-Quran"]
logo = st.file_uploader("Upload Logo (used in PDFs)", type=["jpg","png","jpeg"])

tab1, tab2, tab3 = st.tabs(["Single Student PDF", "Daily/Bulk Entry", "Admin Panel"])

# --- Teacher Login & Class Assignment ---
teacher_name = st.sidebar.text_input("Teacher Name")
c.execute("SELECT assigned_class FROM teachers WHERE name=?", (teacher_name,))
result = c.fetchone()
assigned_class = result[0] if result else None

# ---------------- TAB 1: Single PDF ----------------
with tab1:
    st.header("Single Student PDF Generation")
    # ... (Same as previous single student code, unchanged) ...
    st.info("Use Single Student PDF for manual entry or demo purposes.")

# ---------------- TAB 2: Daily/Bulk Entry ----------------
with tab2:
    st.header("Daily Marks Entry / Bulk PDF")
    if not assigned_class:
        st.warning("You are not assigned to any class. Contact admin.")
    else:
        # Filter students for assigned class
        c.execute("SELECT roll,name FROM students WHERE class=?", (assigned_class,))
        students_in_class = c.fetchall()
        student_options = [f"{r[1]} (Roll {r[0]})" for r in students_in_class]
        if student_options:
            selected_student = st.selectbox("Select Student", student_options)
            roll_input = int(selected_student.split("Roll ")[1][:-1])
            name_input = selected_student.split(" (Roll")[0]
            c.execute("SELECT father, section FROM students WHERE roll=?",(roll_input,))
            father_input, section_input = c.fetchone()
            
            today = st.date_input("Test Date")
            c.execute("SELECT id, subject, total, obtained FROM marks WHERE roll=?",(roll_input,))
            prev_marks = {row[1]: {"id": row[0], "total": row[2], "obt": row[3]} for row in c.fetchall()}
            
            for s in subs:
                c1,c2,c3 = st.columns([1,1,1])
                total_marks = c2.number_input(f"Total ({s})",1,100,value=prev_marks[s]["total"] if s in prev_marks else 0,key=f"t_{s}")
                obtained_marks = c3.number_input(f"Obtained ({s})",0,total_marks,value=prev_marks[s]["obt"] if s in prev_marks else 0,key=f"o_{s}")
                
                if st.button(f"Save Marks ({s})", key=f"save_{s}"):
                    if s in prev_marks:
                        c.execute("UPDATE marks SET total=?, obtained=?, date=? WHERE id=?",(total_marks,obtained_marks,str(today),prev_marks[s]["id"]))
                    else:
                        c.execute("INSERT INTO marks (roll,subject,total,obtained,date) VALUES (?,?,?,?,?)",(roll_input,s,total_marks,obtained_marks,str(today)))
                    conn.commit()
                    st.success(f"{s} marks saved for {name_input}")

                if s in prev_marks and st.button(f"Delete Marks ({s})", key=f"del_{s}"):
                    c.execute("DELETE FROM marks WHERE id=?",(prev_marks[s]["id"],))
                    conn.commit()
                    st.warning(f"{s} marks deleted for {name_input}")
                    st.experimental_rerun()
        else:
            st.info("No students found in your assigned class.")

# ---------------- TAB 3: Admin Panel ----------------
with tab3:
    st.header("Admin Panel: Marks Overview")
    c.execute("SELECT s.name,s.roll,s.class,s.section,m.subject,m.total,m.obtained,m.date FROM students s LEFT JOIN marks m ON s.roll=m.roll ORDER BY s.class,s.roll")
    rows = c.fetchall()
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["Student","Roll","Class","Section","Subject","Total","Obtained","Date"])
        df["Marks Added"] = df["Obtained"].apply(lambda x: "Yes" if x else "No")
        st.dataframe(df)
    else:
        st.info("No marks data available yet.")
