import streamlit as st
from fpdf import FPDF

# PDF Generation Function
class ResultCard(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 14)
        self.cell(0, 8, "SCHOOL EDUCATION DEPARTMENT", ln=True, align='C')
        self.set_font("Arial", 'B', 18)
        self.cell(0, 10, "GOVT. HIGH SCHOOL BHUTTA MOHABBAT", ln=True, align='C')
        self.set_font("Arial", '', 12)
        self.cell(0, 8, "EMIS CODE: 39310025 | DISTRICT OKARA", ln=True, align='C')
        self.ln(10)

st.title("GHS Bhutta Mohabbat - Result Generator")

# --- Input Form ---
with st.form("student_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Student Name")
        s_class = st.text_input("Class", value="8")
    with col2:
        f_name = st.text_input("Father Name")
        roll_no = st.text_input("Roll No")
    
    st.write("### Enter Marks")
    subjects = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks_data = {}
    
    for sub in subjects:
        c1, c2 = st.columns(2)
        with c1:
            total = st.number_input(f"Total ({sub})", value=50, key=f"t_{sub}")
        with c2:
            obt = st.number_input(f"Obtained ({sub})", value=0, key=f"o_{sub}")
        marks_data[sub] = [total, obt]
        
    submitted = st.form_submit_button("Generate PDF")

if submitted:
    pdf = ResultCard()
    pdf.add_page()
    
    # Student Info Table
    pdf.set_fill_color(120, 150, 170)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 10, f" NAME: {name}", fill=True)
    pdf.cell(95, 10, f" FATHER NAME: {f_name}", fill=True, ln=True)
    
    # Marks Table
    pdf.ln(5)
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(90, 10, " SUBJECT", border=1, fill=True)
    pdf.cell(50, 10, " TOTAL", border=1, fill=True, align='C')
    pdf.cell(50, 10, " OBTAINED", border=1, fill=True, align='C', ln=True)
    
    pdf.set_text_color(0,0,0)
    t_max, t_obt = 0, 0
    for s, m in marks_data.items():
        pdf.cell(90, 8, f" {s}", border=1)
        pdf.cell(50, 8, f"{m[0]}", border=1, align='C')
        pdf.cell(50, 8, f"{m[1]}", border=1, align='C', ln=True)
        t_max += m[0]
        t_obt += m[1]
    
    # Footer
    pdf.ln(10)
    pdf.cell(0, 10, f"Total: {t_obt}/{t_max} | Percentage: {(t_obt/t_max)*100:.1f}%", ln=True)
    pdf.cell(0, 10, "SENIOR HEAD MASTER (SAFDAR JAVED)", align='R')
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    st.download_button("Download Result Card", data=pdf_output, file_name=f"{name}_Result.pdf")
