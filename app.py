import streamlit as st
from fpdf import FPDF

# --- School Branding ---
SCHOOL_NAME = "GOVT. HIGH SCHOOL BHUTTA MOHABBAT" #
EMIS_CODE = "39310025 | DISTRICT OKARA" #
HEADMASTER = "SAFDAR JAVED" #

# --- Auto Grading Logic ---
def get_auto_grade(per):
    if per >= 80: return "A+"
    elif per >= 70: return "A"
    elif per >= 60: return "B"
    elif per >= 50: return "C"
    elif per >= 40: return "D"
    else: return "F"

class PDF(FPDF):
    def header(self):
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287) 
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
    
    # Student Info
    pdf.set_fill_color(112, 128, 144)
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

    # Selected Subjects Data
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for s, m in data['selected_marks'].items():
        pdf.cell(100, 8, f" {s}", 1)
        pdf.cell(45, 8, str(m[0]), 1, 0, 'C')
        pdf.cell(50, 8, str(m[1]), 1, 1, 'C')

    # Grand Total
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 8, ' GRAND TOTAL', 1)
    pdf.cell(45, 8, str(data['t_total']), 1, 0, 'C')
    pdf.cell(50, 8, str(data['t_obt']), 1, 1, 'C')
    
    # Auto Grade & Manual Performance
    pdf.ln(10)
    pdf.set_font('Arial', '', 8)
    cols = ["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]
    vals = [f"{data['per']}%", data['pos'], data['perf'], data['grade']]
    
    for c in cols: pdf.cell(48, 5, c, 0, 0, 'L')
    pdf.ln(5)
    for v in vals: pdf.cell(46, 8, v, 1, 0, 'C'); pdf.cell(2, 8, "")

    # Signatures
    pdf.ln(35)
    pdf.cell(90, 0, '', 'T', 0, 'C')
    pdf.cell(20, 0, '')
    pdf.cell(85, 0, '', 'T', 1, 'C')
    pdf.cell(90, 10, 'CLASS TEACHER', 0, 0, 'C')
    pdf.cell(105, 10, f'SENIOR HEAD MASTER ({HEADMASTER})', 0, 1, 'R')

    return pdf.output()

# --- Streamlit UI ---
st.set_page_config(page_title="Result Generator", layout="wide")
st.title("📊 GHS Bhutta Mohabbat - Result System")

with st.form("master_form"):
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Student Name")
    father = c2.text_input("Father Name")
    roll = c3.text_input("Roll No")
    
    c4, c5, c6 = st.columns(3)
    s_class = c4.text_input("Class", "8")
    section = c5.text_input("Section", "A")
    perf = c6.text_input("Manual Performance", "Excellent")
    
    pos = st.text_input("Position", "---")

    st.divider()
    st.subheader("Select Subjects & Enter Marks")
    
    all_subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    selected_marks = {}
    
    # Checkbox layout
    cols = st.columns(4)
    for i, s in enumerate(all_subs):
        with cols[i % 4]:
            is_selected = st.checkbox(s, value=True)
            if is_selected:
                def_total = 75 if s == "Islamiat" else 50 #
                tm = st.number_input(f"Total ({s})", value=def_total, key=f"t_{s}")
                om = st.number_input(f"Obtained ({s})", value=0, key=f"o_{s}")
                selected_marks[s] = [tm, om]

    if st.form_submit_button("Generate Report Card"):
        if not selected_marks:
            st.error("Kam az kam ek subject select karein!")
        else:
            t_total = sum(m[0] for m in selected_marks.values())
            t_obt = sum(m[1] for m in selected_marks.values())
            per = round((t_obt / t_total) * 100, 2) if t_total > 0 else 0
            
            # Auto grading logic
            auto_grade = get_auto_grade(per)
            
            final_data = {
                "name": name, "father": father, "class": s_class, "roll": roll, 
                "section": section, "selected_marks": selected_marks, "t_total": t_total, 
                "t_obt": t_obt, "per": per, "grade": auto_grade, "perf": perf, "pos": pos
            }
            
            pdf_bytes = generate_pdf(final_data)
            st.success(f"{name} ka Result (Grade: {auto_grade}) taiyar hai!")
            st.download_button("Download PDF", pdf_bytes, f"{name}_Result.pdf", "application/pdf")
