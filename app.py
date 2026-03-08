import streamlit as st
from fpdf import FPDF
import sqlite3
import pandas as pd
from datetime import datetime
import io

# 1. Database Functions
def init_db():
    conn = sqlite3.connect('school_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, f_name TEXT, 
                  s_class TEXT, roll_no TEXT, section TEXT, total INTEGER, obtained INTEGER, 
                  percentage REAL, grade TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(name, f_name, s_class, roll_no, section, total, obtained, percentage, grade):
    conn = sqlite3.connect('school_records.db')
    c = conn.cursor()
    c.execute("INSERT INTO results (name, f_name, s_class, roll_no, section, total, obtained, percentage, grade, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (name, f_name, s_class, roll_no, section, total, obtained, percentage, grade, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def delete_record(id):
    conn = sqlite3.connect('school_records.db')
    c = conn.cursor()
    c.execute("DELETE FROM results WHERE id=? ", (id,))
    conn.commit()
    conn.close()

# 2. PDF Styling Class
class ResultCard(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.theme_color = (120, 150, 170) # Grey-Blue theme

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
                self.image(self.logo_path, 12, 12, 25)
                self.set_xy(10, 38)
                self.set_font("Arial", 'B', 8)
                self.cell(35, 4, "ANNUAL REPORT CARD", ln=True, align='C')
                self.set_x(10)
                self.cell(35, 4, "Session 2025-2026", ln=True, align='C') # Updated session
            except: pass
        
        self.set_y(12)
        self.set_font("Arial", 'B', 13)
        self.cell(0, 7, "SCHOOL EDUCATION DEPARTMENT", ln=True, align='C')
        self.set_font("Arial", 'B', 18)
        self.cell(0, 10, "GOVT. HIGH SCHOOL BHUTTA MOHABBAT", ln=True, align='C') # Official School Name
        self.set_font("Arial", '', 11)
        self.cell(0, 7, "EMIS CODE: 39310025 | DISTRICT OKARA", ln=True, align='C')
        self.ln(15)

def get_grade_info(per):
    if per >= 80: return "A+", "Exceptional"
    elif per >= 70: return "A", "Excellent"
    elif per >= 60: return "B", "Very Good"
    elif per >= 50: return "C", "Good"
    elif per >= 40: return "D", "Fair"
    else: return "E", "Needs Improvement"

# 3. Streamlit App
init_db()
st.set_page_config(page_title="GHS Result System", layout="wide")
st.title("🏫 GHS Bhutta Mohabbat - Result Generator")

# Form
with st.expander("📝 Enter Student Details", expanded=True):
    uploaded_logo = st.file_uploader("Logo Upload Karen", type=['png','jpg','jpeg'])
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Student Name")
        f_name = c2.text_input("Father Name")
        
        c3, c4, c5 = st.columns(3)
        s_class = c3.text_input("Class", value="8")
        roll_no = c4.text_input("Roll No")
        section = c5.text_input("Section", value="A")
        
        st.write("---")
        all_subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
        marks_data = {}
        cols = st.columns(4)
        for i, sub in enumerate(all_subs):
            with cols[i % 4]:
                if st.checkbox(sub, value=True):
                    t = st.number_input(f"Total ({sub})", 50, key=f"t_{sub}")
                    o = st.number_input(f"Obtained ({sub})", 0, key=f"o_{sub}")
                    marks_data[sub] = [t, o]
        submit = st.form_submit_button("Generate PDF & Save Record")

if submit and name and roll_no:
    t_m = sum([m[0] for m in marks_data.values()])
    o_m = sum([m[1] for m in marks_data.values()])
    perc = (o_m / t_m * 100) if t_m > 0 else 0
    grade, remarks = get_grade_info(perc)
    
    save_to_db(name, f_name, s_class, roll_no, section, t_m, o_m, perc, grade)
    
    # PDF Rendering
    pdf = ResultCard(logo_path=uploaded_logo)
    pdf.add_page()
    
    # Student Info Bar - ROW 1
    pdf.set_fill_color(120, 150, 170)
    pdf.set_text_color(255,255,255)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 10, f" NAME: {name.upper()}", fill=True, border=1)
    pdf.cell(90, 10, f" FATHER: {f_name.upper()}", fill=True, border=1, ln=True)
    
    # Student Info Bar - ROW 2 (Class, Roll, Section)
    pdf.set_fill_color(230, 235, 240) # Light grey-blue for sub-info
    pdf.set_text_color(0,0,0)
    pdf.cell(63, 8, f" Class: {s_class}", fill=True, border=1)
    pdf.cell(63, 8, f" Roll No: {roll_no}", fill=True, border=1)
    pdf.cell(64, 8, f" Section: {section}", fill=True, border=1, ln=True)
    
    # Table Header
    pdf.ln(5)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(90, 10, " SUBJECT", border=1, fill=True, align='C')
    pdf.cell(50, 10, " TOTAL MARKS", border=1, fill=True, align='C')
    pdf.cell(50, 10, " OBTAINED", border=1, fill=True, align='C', ln=True)
    
    pdf.set_text_color(0,0,0)
    for s, m in marks_data.items():
        pdf.cell(90, 8, f" {s}", border=1)
        pdf.cell(50, 8, f"{m[0]}", border=1, align='C')
        pdf.cell(50, 8, f"{m[1]}", border=1, align='C', ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 12, f"Total: {o_m}/{t_m} | Percentage: {perc:.1f}% | Grade: {grade} ({remarks})", border=1, align='C', ln=True)
    
    # Signatures shifted slightly down
    pdf.set_y(265)
    pdf.cell(95, 5, "____________________", align='C')
    pdf.cell(95, 5, "____________________", ln=True, align='C')
    pdf.cell(95, 5, "CLASS TEACHER", align='C')
    pdf.cell(95, 5, "SENIOR HEAD MASTER (SAFDAR JAVED)", ln=True, align='C')

    st.success("Result Generated Successfully!")
    st.download_button("Download PDF", data=bytes(pdf.output()), file_name=f"{roll_no}_{name}.pdf")

# 4. Database Section with Excel Export
st.write("---")
st.subheader("📁 Saved Records")
conn = sqlite3.connect('school_records.db')
df = pd.read_sql_query("SELECT * FROM results ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("🟢 Export All Records to Excel", data=buffer.getvalue(), file_name="School_Records.xlsx")
    
    for idx, row in df.iterrows():
        c_a, c_b, c_c = st.columns([5, 2, 1])
        c_a.write(f"**{row['name']}** (Roll: {row['roll_no']}) | Class: {row['s_class']}")
        if c_c.button("Delete", key=f"d_{row['id']}"):
            delete_record(row['id'])
            st.rerun()
