import streamlit as st
from fpdf import FPDF

class ResultCard(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        # Logo add karne ka logic
        if self.logo_path:
            try:
                self.image(self.logo_path, 10, 10, 25) # Logo position (x, y, width)
            except:
                pass
        
        self.set_font("Arial", 'B', 14)
        self.cell(0, 8, "SCHOOL EDUCATION DEPARTMENT", ln=True, align='C')
        self.set_font("Arial", 'B', 18)
        self.cell(0, 10, "GOVT. HIGH SCHOOL BHUTTA MOHABBAT", ln=True, align='C')
        self.set_font("Arial", '', 12)
        self.cell(0, 8, "EMIS CODE: 39310025 | DISTRICT OKARA", ln=True, align='C')
        self.ln(10)

st.title("GHS Bhutta Mohabbat Result System")

# --- 1. Logo Upload ---
uploaded_logo = st.file_uploader("School Logo Upload Karen (Optional)", type=['jpg', 'png', 'jpeg'])

# --- 2. Student Information ---
with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Student Name")
        s_class = st.text_input("Class", value="8")
    with col2:
        f_name = st.text_input("Father Name")
        roll_no = st.text_input("Roll No")

    # --- 3. Subject Selection (Dynamic) ---
    st.write("### Subjects Select Karen")
    all_subjects = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran", "General Science", "Drawing"]
    
    # User yahan se select karega ke kaunse subjects dikhane hain
    selected_subjects = st.multiselect("Is class ke subjects select karen:", all_subjects, default=["English", "Urdu", "Mathematics"])
    
    marks_data = {}
    st.write("### Enter Marks")
    for sub in selected_subjects:
        c1, c2 = st.columns(2)
        with c1:
            total = st.number_input(f"Total ({sub})", value=50, key=f"t_{sub}")
        with c2:
            obt = st.number_input(f"Obtained ({sub})", value=0, key=f"o_{sub}")
        marks_data[sub] = [total, obt]

    generate_btn = st.form_submit_button("Result Card Banayen")

if generate_btn:
    # Error Fix: pdf.output() handling
    pdf = ResultCard(logo_path=uploaded_logo if uploaded_logo else None)
    pdf.add_page()
    
    # Student Info Table
    pdf.set_fill_color(120, 150, 170)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 10, f" NAME: {name.upper()}", fill=True)
    pdf.cell(95, 10, f" FATHER NAME: {f_name.upper()}", fill=True, ln=True)
    
    # Marks Table
    pdf.ln(5)
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(90, 10, " SUBJECT", border=1, fill=True)
    pdf.cell(50, 10, " TOTAL MARKS", border=1, fill=True, align='C')
    pdf.cell(50, 10, " OBTAINED", border=1, fill=True, align='C', ln=True)
    
    pdf.set_text_color(0,0,0)
    t_max, t_obt = 0, 0
    for s, m in marks_data.items():
        pdf.cell(90, 8, f" {s}", border=1)
        pdf.cell(50, 8, f"{m[0]}", border=1, align='C')
        pdf.cell(50, 8, f"{m[1]}", border=1, align='C', ln=True)
        t_max += m[0]
        t_obt += m[1]
    
    # Calculations
    per = (t_obt/t_max)*100 if t_max > 0 else 0
    
    # Grand Total Row
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, " GRAND TOTAL", border=1)
    pdf.cell(50, 10, f"{t_max}", border=1, align='C')
    pdf.cell(50, 10, f"{t_obt}", border=1, align='C', ln=True)
    
    # Performance Stats
    pdf.ln(5)
    pdf.cell(45, 12, f"PERCENTAGE: {per:.1f}%", border=1, align='C')
    pdf.cell(45, 12, "POSITION: ---", border=1, align='C')
    pdf.cell(45, 12, "PERFORMANCE: ---", border=1, align='C')
    pdf.cell(45, 12, "GRADE: ---", border=1, align='C', ln=True)

    # Footer
    pdf.ln(20)
    pdf.cell(95, 5, "____________________", align='C')
    pdf.cell(95, 5, "____________________", ln=True, align='C')
    pdf.cell(95, 5, "CLASS TEACHER", align='C')
    pdf.cell(95, 5, "SENIOR HEAD MASTER (SAFDAR JAVED)", ln=True, align='C')

    # FIXED: fpdf2 output format
    pdf_bytes = pdf.output() 
    st.download_button(
        label="Download Result Card (PDF)",
        data=bytes(pdf_bytes),
        file_name=f"{name}_Result.pdf",
        mime="application/pdf"
    )
