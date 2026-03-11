# app.py
import streamlit as st
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import io
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

# Default admin
c.execute("SELECT * FROM admin")
if not c.fetchall():
    c.execute("INSERT INTO admin (username,password) VALUES (?,?)", ("admin","admin123"))
conn.commit()

# --- Session State ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""

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
    if data.get('logo'):
        try:
            logo_reader = ImageReader(data['logo'])
            p.drawImage(logo_reader, 45, height - 105, width=65, height=65, mask='auto')
        except: pass

    # Session
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, height - 130, f"Session {data['session']}")

    # Student Info
    info_data = [
        [f"NAME: {data['student_name'].upper()}", f"FATHER NAME: {data['father_name'].upper()}"],
        [f"CLASS: {data['class']}", f"ROLL NO: {data['roll']}", f"SECTION: {data['section']}"]
    ]
    t1 = Table(info_data[:1], colWidths=[275, 240])
    t1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7B96AC")),
                            ('TEXTCOLOR',(0,0),(-1,-1),colors.white),
                            ('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),
                            ('FONTSIZE',(0,0),(-1,-1),9),
                            ('GRID',(0,0),(-1,-1),0.5,colors.white),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    t2 = Table(info_data[1:], colWidths=[175,175,165])
    t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#7B96AC")),
                            ('TEXTCOLOR',(0,0),(-1,-1),colors.white),
                            ('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),
                            ('FONTSIZE',(0,0),(-1,-1),9),
                            ('GRID',(0,0),(-1,-1),0.5,colors.white),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    t1.wrapOn(p,40,height-160); t1.drawOn(p,40,height-160)
    t2.wrapOn(p,40,height-180); t2.drawOn(p,40,height-180)

    # Marks Table
    y_table = height-215
    p.setFillColor(colors.HexColor("#333333"))
    p.rect(40,y_table,515,25,fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold",10)
    p.drawString(150,y_table+8,"SUBJECT")
    p.drawString(350,y_table+8,"TOTAL MARKS")
    p.drawString(460,y_table+8,"OBTAINED")
    y_row = y_table-22
    p.setFillColor(colors.black)
    p.setFont("Helvetica",10)
    grand_total_max,grand_total_obt=0,0
    for sub,info in data['marks_data'].items():
        p.rect(40,y_row,515,22)
        p.line(330,y_row,330,y_row+22); p.line(440,y_row,440,y_row+22)
        p.drawString(45,y_row+7,sub)
        p.drawCentredString(385,y_row+7,str(info['total']))
        p.drawCentredString(495,y_row+7,str(info['obt']))
        grand_total_max+=info['total']; grand_total_obt+=info['obt']
        y_row-=22

    # Grand Total
    p.setFont("Helvetica-Bold",10)
    p.rect(40,y_row,515,22)
    p.drawString(45,y_row+7,"GRAND TOTAL")
    p.drawCentredString(385,y_row+7,str(grand_total_max))
    p.drawCentredString(495,y_row+7,str(grand_total_obt))

    # Result Summary
    y_summary = y_row-40
    perc = (grand_total_obt/grand_total_max*100) if grand_total_max>0 else 0
    grade,perf = get_grade_info(perc)
    box_w = 515/4
    for i,label in enumerate(["PERCENTAGE","POSITION","PERFORMANCE","FINAL GRADE"]):
        val=[f"{perc:.1f}%",data['position'],data.get("performance",perf),grade][i]
        p.rect(40+(i*box_w),y_summary,box_w,30)
        p.setFont("Helvetica-Bold",8)
        p.drawCentredString(40+(i*box_w)+(box_w/2),y_summary+18,f"{label}: {val}")

    # Top 3 Students
    if "class_top3" in data:
        y_top = y_summary - 60
        p.setFont("Helvetica-Bold",10)
        p.drawString(40, y_top+12, "Class Top 3:")
        p.setFont("Helvetica",9)
        p.rect(40, y_top-50, 515, 50, fill=0)
        p.line(40+350, y_top-50, 40+350, y_top)
        p.line(40+450, y_top-50, 40+450, y_top)
        for idx, (name, total, pos) in enumerate(data['class_top3']):
            y_pos = y_top - (idx*15) - 15
            p.drawString(45, y_pos, f"{pos}. {name}")
            p.drawCentredString(405, y_pos, str(total))
            p.drawCentredString(495, y_pos, f"Pos {pos}")

    # Quotes & Signatures
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique",11)
    p.drawCentredString(A4[0]/2,200,'"Education is the most powerful weapon which you can use to change the world."')
    p.drawCentredString(A4[0]/2,180,'"The beautiful thing about learning is that no one can take it away from you."')
    p.setFont("Helvetica-Bold",9)
    p.line(80,110,210,110); p.drawCentredString(145,95,"CLASS TEACHER")
    p.line(A4[0]-240,110,A4[0]-40,110); p.drawCentredString(A4[0]-140,95,"SENIOR HEAD MASTER (SAFDAR JAVED)")
    p.setFont("Helvetica",8); p.drawRightString(A4[0]-40,60,f"Result Declaration Date: {data['date']}")

    p.showPage(); p.save()
    buffer.seek(0)
    return buffer

# --- UI Start ---
st.title("GHS Bhutta Mohabbat Result System")
role = st.selectbox("Login as",["Admin","Teacher"])
logo = st.file_uploader("Upload Logo (used in PDFs)", type=["jpg","png","jpeg"])
subs=["English","Urdu","Mathematics","Islamiat","Science","Social Study","Computer","Tarjuma-tu-Quran"]

# --- Admin Panel ---
if role == "Admin":
    if not st.session_state.admin_logged_in:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                st.session_state.admin_logged_in = True
                st.session_state.admin_username = username
                st.success("Logged in as Admin")
            else:
                st.error("Invalid credentials")
    else:
        st.subheader(f"Welcome Admin: {st.session_state.admin_username}")
        admin_tabs = st.tabs(["Manage Teachers", "Manage Students", "Logout"])

        # --- Manage Teachers ---
        with admin_tabs[0]:
            st.write("**Add Teacher**")
            t_name = st.text_input("Teacher Name")
            t_class = st.text_input("Assigned Class")
            if st.button("Add Teacher"):
                if t_name and t_class:
                    try:
                        c.execute("INSERT INTO teachers (name, assigned_class) VALUES (?,?)", (t_name, t_class))
                        conn.commit()
                        st.success(f"Teacher {t_name} added.")
                    except sqlite3.IntegrityError:
                        st.error("Teacher already exists.")
            st.write("**Existing Teachers**")
            c.execute("SELECT id,name,assigned_class FROM teachers")
            teachers = c.fetchall()
            for tid, name, tclass in teachers:
                col1, col2 = st.columns([3,1])
                col1.write(f"{name} | Class: {tclass}")
                if col2.button("Delete", key=f"del_teacher_{tid}"):
                    c.execute("DELETE FROM teachers WHERE id=?", (tid,))
                    conn.commit()
                    st.experimental_rerun()

        # --- Manage Students ---
        with admin_tabs[1]:
            st.write("**Add Student**")
            s_name = st.text_input("Student Name")
            s_father = st.text_input("Father Name")
            s_class = st.text_input("Class")
            s_section = st.text_input("Section")
            s_roll = st.number_input("Roll No", min_value=1, step=1)
            if st.button("Add Student"):
                try:
                    c.execute("INSERT INTO students (roll,name,father,class,section) VALUES (?,?,?,?,?)",
                              (s_roll, s_name, s_father, s_class, s_section))
                    conn.commit()
                    st.success(f"Student {s_name} added.")
                except sqlite3.IntegrityError:
                    st.error("Roll number already exists.")
            st.write("**Existing Students**")
            c.execute("SELECT roll,name,class,section FROM students")
            students = c.fetchall()
            for roll, name, sclass, section in students:
                col1, col2 = st.columns([3,1])
                col1.write(f"{roll} | {name} | Class {sclass}-{section}")
                if col2.button("Delete", key=f"del_student_{roll}"):
                    c.execute("DELETE FROM students WHERE roll=?", (roll,))
                    c.execute("DELETE FROM marks WHERE roll=?", (roll,))
                    conn.commit()
                    st.experimental_rerun()

        # --- Logout ---
        with admin_tabs[2]:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.session_state.admin_username = ""
                st.experimental_rerun()

# --- Teacher Panel ---
elif role == "Teacher":
    if not st.session_state.teacher_logged_in:
        st.subheader("Teacher Login")
        t_name = st.text_input("Teacher Name")
        if st.button("Login as Teacher"):
            c.execute("SELECT * FROM teachers WHERE name=?", (t_name,))
            if c.fetchone():
                st.session_state.teacher_logged_in = True
                st.session_state.teacher_name = t_name
                st.success(f"Logged in as {t_name}")
            else:
                st.error("Teacher not found.")
    else:
        st.subheader(f"Welcome Teacher: {st.session_state.teacher_name}")
        teacher_tabs = st.tabs(["Enter Marks", "View Results", "Logout"])

        # --- Enter Marks with Update ---
        with teacher_tabs[0]:
            c.execute("SELECT DISTINCT class,section FROM students")
            classes = [f"{cl}-{sec}" for cl,sec in c.fetchall()]
            selected_class = st.selectbox("Select Class-Section", classes)
            if selected_class:
                s_class,s_section = selected_class.split("-")
                c.execute("SELECT roll,name FROM students WHERE class=? AND section=?", (s_class,s_section))
                students_list = c.fetchall()
                selected_student = st.selectbox("Select Student", [f"{roll} | {name}" for roll,name in students_list])
                if selected_student:
                    roll = int(selected_student.split("|")[0].strip())
                    marks = {}
                    for sub in subs:
                        c.execute("SELECT obtained FROM marks WHERE roll=? AND subject=?", (roll,sub))
                        res = c.fetchone()
                        marks[sub] = st.number_input(f"{sub} Marks", min_value=0, max_value=100, step=1,
                                                     value=res[0] if res else 0)
                    if st.button("Save/Update Marks"):
                        today = datetime.date.today().strftime("%d-%m-%Y")
                        for sub,val in marks.items():
                            c.execute("SELECT id FROM marks WHERE roll=? AND subject=?", (roll,sub))
                            if c.fetchone():
                                c.execute("UPDATE marks SET obtained=?, total=?, date=? WHERE roll=? AND subject=?",
                                          (val,100,today,roll,sub))
                            else:
                                c.execute("INSERT INTO marks (roll,subject,total,obtained,date) VALUES (?,?,?,?,?)",
                                          (roll,sub,100,val,today))
                        conn.commit()
                        st.success("Marks saved/updated successfully.")

        # --- View Results with Position + Top3 ---
        with teacher_tabs[1]:
            c.execute("SELECT DISTINCT class,section FROM students")
            classes = [f"{cl}-{sec}" for cl,sec in c.fetchall()]
            selected_class = st.selectbox("Select Class-Section for Results", classes, key="result_class")
            if selected_class:
                s_class,s_section = selected_class.split("-")
                c.execute("SELECT roll,name FROM students WHERE class=? AND section=?", (s_class,s_section))
                students_list = c.fetchall()
                selected_student = st.selectbox("Select Student to View", [f"{roll} | {name}" for roll,name in students_list], key="result_student")
                if selected_student:
                    roll = int(selected_student.split("|")[0].strip())
                    c.execute("SELECT name,father,class,section FROM students WHERE roll=?", (roll,))
                    s = c.fetchone()
                    c.execute("SELECT subject,total,obtained FROM marks WHERE roll=?", (roll,))
                    marks_data = {sub: {'total': total,'obt':obt} for sub,total,obt in c.fetchall()}

                    # Position calculation
                    c.execute("SELECT roll,SUM(obtained) as total_obt FROM marks "
                              "JOIN students USING(roll) WHERE class=? AND section=? GROUP BY roll ORDER BY total_obt DESC",
                              (s_class,s_section))
                    rank_list = c.fetchall()
                    position = [idx+1 for idx,(r,t) in enumerate(rank_list) if r==roll][0]

                    # Top 3 for class
                    c.execute("""
                    SELECT students.name, SUM(marks.obtained) as total_obt
                    FROM marks JOIN students USING(roll)
                    WHERE students.class=? AND students.section=?
                    GROUP BY roll ORDER BY total_obt DESC LIMIT 3
                    """, (s_class, s_section))
                    top3 = c.fetchall()
                    top3_data = [(name, total, idx+1) for idx,(name,total) in enumerate(top3)]

                    if marks_data:
                        data = {
                            'school_name': 'GHS Bhutta Mohabbat',
                            'emis':'123456',
                            'district':'Sargodha',
                            'session':'2025-26',
                            'student_name': s[0],
                            'father_name': s[1],
                            'class
