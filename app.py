import streamlit as st
from fpdf import FPDF
import sqlite3
import pandas as pd
from datetime import datetime
import io

# 1. Database Setup
def init_db():
    conn = sqlite3.connect('school_final_v2.db') # New name to reset table
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, f_name TEXT, 
                  s_class TEXT, roll_no TEXT, section TEXT, total INTEGER, obtained INTEGER, 
                  percentage REAL, grade TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(name, f_name, s_class, roll_no, section, total, obtained, percentage, grade):
    conn = sqlite3.connect('school_final_v2.db')
    c = conn.cursor()
    c.execute("INSERT INTO results (name, f_name, s_class, roll_no, section, total, obtained, percentage, grade, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (name, f_name, s_class, roll_no, section, total, obtained, percentage, grade, datetime.now().strftime("%d-%m-%Y")))
    conn.commit()
    conn.close()

# 2. PDF Styling Class
class ResultCard(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.theme_color = (120, 150, 170) # Grey-Blue theme from image

    def draw_border(self):
        self.set_line_width(0.8)
        self.set_draw_color(120, 150, 170)
        self.rect(5, 5, 200, 287) 
        self.set_line_width(0.2)
        self.rect(7, 7, 196, 283)

    def header(self):
        self.draw_border()
        if self.logo_path:
            try:
                self.image(self.logo_path, 12, 12, 23)
                self.set_xy(10, 36)
                self.set_font("Arial", 'B', 7)
                self.cell(28, 4, "ANNUAL REPORT CARD", ln=True, align='C')
                self.set_x(10)
                self.cell(28, 4, "Session 2025-2026", ln=True, align='C')
            except: pass
        
        self.set_y(10)
        self.set_font("Arial", 'B', 10)
        self.cell(0, 5, "SCHOOL EDUCATION DEPARTMENT", ln=True, align='C')
        self.set_font("Arial", 'B', 16)
        self.cell(0, 8, "GOVT. HIGH SCHOOL BHUTTA MOHABBAT", ln=True, align='C')
        self.set_font("Arial", '', 10)
        self.cell(0, 5, "EMIS CODE: 39310025 | DISTRICT OKARA", ln=True, align='C')
        
        self.set_y(32)
        self.set_font("Arial", 'B', 18)
        self.set_text_color(100, 120, 140)
        self.cell(0, 10, "STUDENT REPORT CARD", ln=True, align='L')
        self.set_font("Arial", 'B', 10)
        self.cell(0, 5, "ACADEMIC YEAR: 2025-26", ln=True, align='L')
        self.ln(5)

# 3. Streamlit Interface
init_db()
st.set_page_config(page_title="GHS Result System", layout="wide")

with st.expander("📝 Enter Student Data", expanded=True):
    uploaded_logo = st.file_uploader("Upload Logo", type=['png','jpg','jpeg'])
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Student Name")
        f_name = c2.text_input("Father Name")
        c3, c4, c5 = st.columns(3)
        s_class = c3.text_input("Class", value="8")
        roll_no = c4.text_input("Roll No")
        section = c5.text_input("Section", value="A")
        
        st.write("---")
        subjects = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
        marks_data = {}
        cols = st.columns(4)
        for i, sub in enumerate(subjects):
            with cols[i % 4]:
                if st.checkbox(sub, value=True):
                    t = st.number_input(f"Total ({sub})", 50, key=f"t_{sub}")
                    o = st.number_input(f"Obtained ({sub})", 0, key=f"o_{sub}")
                    marks_data[sub] = [t, o]
        submit = st.form_submit_button("Generate & Save")

if submit and name:
    t_m = sum([m[0] for m in marks_data.values()])
    o_m = sum([m[1] for m in marks_data.values()])
    perc = (o_m / t_m * 100) if t_m > 0 else 0
    grade = "A+" if perc >= 80 else "A" if perc >= 70 else "B" # Simple logic
    
    save_to_db(name, f_name, s_class, roll_no, section, t_m, o_m, perc, grade)
    
    pdf = ResultCard(logo_path=uploaded_logo)
    pdf.add_page()
    
    # --- Student Info Layout (Matching Image) ---
    pdf.set_fill_color(120, 150, 170)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial", 'B', 9)
    
    # Line 1: Name and Father Name
    pdf.cell(95, 8, f" NAME: {name.upper()}", fill=True, border='LBT')
    pdf.cell(95, 8, f" FATHER NAME: {f_name.upper()}", fill=True, border='RBT', ln=True)
    pdf.ln(1)
    
    # Line 2: Class, Roll No, Section (One Bar)
    pdf.cell(63.3, 8, f" CLASS: {s_class}", fill=True, border='LBT')
    pdf.cell(63.3, 8, f" ROLL NO: {roll_no}", fill=True, border='BT')
    pdf.cell(63.4, 8, f" SECTION: {section}", fill=True, border='RBT', ln=True)
    
    # Table
    pdf.ln(5)
    pdf.set_fill_color(60, 60, 60)
    pdf.cell(90, 10, " SUBJECT", border=1, fill=True, align='C')
    pdf.cell(50, 10, " TOTAL MARKS", border=1, fill=True, align='C')
    pdf.cell(50, 10, " OBTAINED", border=1, fill=True, align='C', ln=True)
    
    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial", '', 9)
    for s, m in marks_data.items():
        pdf.cell(90, 8, f" {s}", border=1)
        pdf.cell(50, 8, f"{m[0]}", border=1, align='C')
        pdf.cell(50, 8, f"{m[1]}", border=1, align='C', ln=True)

    # Grand Total
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(230, 235, 240)
    pdf.cell(90, 10, " GRAND TOTAL", border=1, fill=True)
    pdf.cell(50, 10, f"{t_m}", border=1, fill=True, align='C')
    pdf.cell(50, 10, f"{o_m}", border=1, fill=True, align='C', ln=True)

    # Performance Stats
    pdf.ln(5)
    w = 190 / 4
    pdf.set_font("Arial", '', 8)
    pdf.cell(w, 10, f"PERCENTAGE: {perc:.1f}%", border=1, align='C')
    pdf.cell(w, 10, f"POSITION: ---", border=1, align='C')
    pdf.cell(w, 10, f"PERFORMANCE: Excellent", border=1, align='C')
    pdf.cell(w, 10, f"FINAL GRADE: {grade}", border=1, align='C', ln=True)

    # Date and Signatures
    pdf.set_y(260)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Date of Issue: {datetime.now().strftime('%d-%m-%Y')}", ln=True, align='L')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(95, 5, "____________________", align='C')
    pdf.cell(95, 5, "____________________", ln=True, align='C')
    pdf.cell(95, 5, "CLASS TEACHER", align='C')
    pdf.cell(95, 5, "SENIOR HEAD MASTER (SAFDAR JAVED)", ln=True, align='C')

    st.success("Result Generated!")
    st.download_button("Download PDF", data=bytes(pdf.output()), file_name=f"{roll_no}_{name}.pdf")

# Data View
st.write("---")
conn = sqlite3.connect('school_final_v2.db')
df = pd.read_sql_query("SELECT * FROM results", conn)
st.dataframe(df)
