import streamlit as st
from fpdf import FPDF
import pandas as pd

# --- Design & Branding (As per your image) ---
SCHOOL_NAME = "GOVT. HIGH SCHOOL BHUTTA MOHABBAT" #
EMIS_CODE = "39310025 | DISTRICT OKARA" #
HEADMASTER = "SAFDAR JAVED" #

class PDF(FPDF):
    def header(self):
        self.rect(5, 5, 200, 287) # Main Border
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'SCHOOL EDUCATION DEPARTMENT', ln=True, align='C')
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, SCHOOL_NAME, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'EMIS CODE: {EMIS_CODE}', ln=True, align='C')
        self.ln(10)

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    
    # Header Blue Bars
    pdf.set_fill_color(112, 128, 144) # Slate Gray
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 8, f" NAME: {data['name'].upper()}", fill=True)
    pdf.cell(10, 8, "")
    pdf.cell(95, 8, f" FATHER NAME: {data['father'].upper()}", fill=True, ln=True)
    pdf.ln(2)
    pdf.cell(45, 8, f" CLASS: {data['class']}", fill=True)
    pdf.cell(5, 8, "")
    pdf.cell(45, 8, f" ROLL NO: {data['roll']}", fill=True)
    pdf.cell(5, 8, "")
    pdf.cell(95, 8, f" SECTION: {data['section']}", fill=True, ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(100, 8, ' SUBJECT', 1, 0, 'L', True)
    pdf.cell(45, 8, ' TOTAL MARKS', 1, 0, 'C', True)
    pdf.cell(50, 8, ' OBTAINED', 1, 1, 'C', True)

    # Subject Data
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for s, m in data['subjects'].items():
        pdf.cell(100, 8, f" {s}", 1)
        pdf.cell(45, 8, str(m[0]), 1, 0, 'C')
        pdf.cell(50, 8, str(m[1]), 1, 1, 'C')

    # Totals
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 8, ' GRAND TOTAL', 1)
    pdf.cell(45, 8, str(data['t_total']), 1, 0, 'C')
    pdf.cell(50, 8, str(data['t_obt']), 1, 1, 'C')
    
    # Performance Section (MANUAL)
    pdf.ln(10)
    pdf.set_font('Arial', '', 8)
    cols = ["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]
    vals = [f"{data['per']}%", data['pos'], data['perf'], data['grade']]
    
    for c in cols: pdf.cell(48, 5, c, 0, 0, 'L')
    pdf.ln(5)
    for v in vals: pdf.cell(46, 8, v, 1, 0, 'C'); pdf.cell(2, 8, "")

    # Footer Signatures
    pdf.ln(35)
    pdf.cell(90, 0, '', 'T', 0, 'C')
    pdf.cell(20, 0, '')
    pdf.cell(85, 0, '', 'T', 1, 'C')
    pdf.cell(90, 10, 'CLASS TEACHER', 0, 0, 'C')
    pdf.cell(105, 10, f'SENIOR HEAD MASTER ({HEADMASTER})', 0, 1, 'R')

    return pdf.output() # fpdf2 fixed version

# --- Streamlit Interface ---
st.title("GHS Bhutta Mohabbat Result System")

with st.form("result_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Student Name", "AQIB")
        father = st.text_input("Father Name", "ALI")
        s_class = st.text_input("Class", "8")
    with col2:
        roll = st.text_input("Roll No", "15")
        section = st.text_input("Section", "A")
        grade = st.text_input("Final Grade", "A+")

    st.divider()
    
    # Manual Performance Input
    perf = st.text_input("Enter Performance (e.g. Excellent, Good, Keep it up)", "Excellent")
    pos = st.text_input("Position", "---")
    
    st.subheader("Marks Entry")
    subjects = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks = {}
    m_cols = st.columns(4)
    for i, sub in enumerate(subjects):
        with m_cols[i % 4]:
            t = st.number_input(f"Total ({sub})", value=50 if sub != "Islamiat" else 75)
            o = st.number_input(f"Obtained ({sub})", value=0)
            marks[sub] = [t, o]

    if st.form_submit_button("Generate Report Card"):
        t_total = sum(m[0] for m in marks.values())
        t_obt = sum(m[1] for m in marks.values())
        per = round((t_obt / t_total) * 100, 2) if t_total > 0 else 0
        
        data = {
            "name": name, "father": father, "class": s_class, "roll": roll, 
            "section": section, "subjects": marks, "t_total": t_total, 
            "t_obt": t_obt, "per": per, "grade": grade, "perf": perf, "pos": pos
        }
        
        pdf_bytes = generate_pdf(data)
        st.success("Result Generated!")
        st.download_button("Download PDF", pdf_bytes, f"{name}_Result.pdf", "application/pdf")
