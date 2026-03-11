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
import pandas as pd
import datetime

st.set_page_config(page_title="GHS Bhutta Mohabbat Result System", layout="wide")

# --- Database ---
conn = sqlite3.connect("students.db", check_same_thread=False)
c = conn.cursor()
# Tables
c.execute('''CREATE TABLE IF NOT EXISTS students
             (roll INTEGER PRIMARY KEY, name TEXT, father TEXT, class TEXT, section TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS marks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              roll INTEGER, subject TEXT, total INTEGER, obtained INTEGER, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS teachers
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE, assigned_class TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS admin
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE,
              password TEXT)''')
# Create default admin if not exists
c.execute("SELECT * FROM admin")
if not c.fetchall():
    c.execute("INSERT INTO admin (username,password) VALUES (?,?)", ("admin","admin123"))
conn.commit()

# --- Helper Functions ---
def get_grade_info(percentage):
    if percentage >= 80: return "A+", "Excellent"
    elif percentage >= 70: return "A", "Very Good"
    elif percentage >= 60: return "B", "Good"
    elif percentage >= 50: return "C", "Satisfactory"
    elif percentage >= 40: return "D", "Fair"
    else: return "F", "Poor"

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

role = st.selectbox("Login as", ["Admin","Teacher"])
if role == "Admin":
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login as Admin"):
        c.execute("SELECT * FROM admin WHERE username=? AND password=?",(username,password))
        if c.fetchone():
            st.success("Logged in as Admin ✅")
            # Admin Panel
            tab1,tab2,tab3 = st.tabs(["Teacher Management","Student Management","Marks Overview"])
            
            # ----- Teacher Management -----
            with tab1:
                st.header("Teachers")
                t_name = st.text_input("Teacher Name")
                t_class = st.text_input("Assigned Class")
                if st.button("Add Teacher"):
                    if t_name and t_class:
                        c.execute("INSERT OR IGNORE INTO teachers (name,assigned_class) VALUES (?,?)",(t_name,t_class))
                        conn.commit()
                        st.success(f"Teacher {t_name} added with class {t_class}")
                df_t = pd.read_sql("SELECT * FROM teachers",conn)
                st.dataframe(df_t)
            
            # ----- Student Management -----
            with tab2:
                st.header("Students")
                s_name = st.text_input("Student Name")
                s_father = st.text_input("Father Name")
                s_class = st.text_input("Class")
                s_section = st.text_input("Section")
                s_roll = st.number_input("Roll Number", min_value=1, step=1)
                if st.button("Add Student"):
                    c.execute("INSERT OR IGNORE INTO students (roll,name,father,class,section) VALUES (?,?,?,?,?)",
                              (s_roll,s_name,s_father,s_class,s_section))
                    conn.commit()
                    st.success(f"Student {s_name} added")
                df_s = pd.read_sql("SELECT * FROM students",conn)
                st.dataframe(df_s)
                
                # Delete or Print PDF per student
                st.subheader("Student Actions")
                for idx,row in df_s.iterrows():
                    col1,col2,col3 = st.columns([2,1,1])
                    col1.write(f"{row['name']} (Roll {row['roll']})")
                    if col2.button("Print PDF", key=f"print_{row['roll']}"):
                        # Fetch marks
                        c.execute("SELECT subject,total,obtained FROM marks WHERE roll=?",(row['roll'],))
                        marks_rows = c.fetchall()
                        marks_dict = {r[0]:{"total":r[1],"obt":r[2]} for r in marks_rows}
                        pdf_data = {"school_name":"GHS Bhutta Mohabbat",
                                    "emis":"39310025",
                                    "district":"Okara",
                                    "session":"2025-2026",
                                    "logo":logo,
                                    "student_name":row['name'],
                                    "father_name":row['father'],
                                    "class":row['class'],
                                    "roll":row['roll'],
                                    "section":row['section'],
                                    "position":"---",
                                    "marks_data":marks_dict,
                                    "date":datetime.date.today().strftime("%d-%m-%Y")}
                        pdf_bytes = generate_pdf(pdf_data)
                        st.download_button(f"Download PDF ({row['name']})",pdf_bytes,f"Result_{row['name']}.pdf","application/pdf")
                    if col3.button("Delete", key=f"del_{row['roll']}"):
                        c.execute("DELETE FROM marks WHERE roll=?",(row['roll'],))
                        c.execute("DELETE FROM students WHERE roll=?",(row['roll'],))
                        conn.commit()
                        st.warning(f"{row['name']} deleted")
                        st.experimental_rerun()
            
            # ----- Marks Overview -----
            with tab3:
                st.header("Marks Overview")
                c.execute("SELECT s.name,s.roll,s.class,s.section,m.subject,m.total,m.obtained,m.date FROM students s LEFT JOIN marks m ON s.roll=m.roll ORDER BY s.class,s.roll")
                rows = c.fetchall()
                if rows:
                    df = pd.DataFrame(rows, columns=["Student","Roll","Class","Section","Subject","Total","Obtained","Date"])
                    df["Marks Added"] = df["Obtained"].apply(lambda x:"Yes" if x else "No")
                    st.dataframe(df)
                else:
                    st.info("No marks data yet.")
        else:
            st.error("Invalid credentials")
