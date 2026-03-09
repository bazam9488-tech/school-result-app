import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- School Branding ---
SCHOOL_NAME = "GOVT. HIGH SCHOOL BHUTTA MOHABBAT"
EMIS_CODE = "39310025 | DISTRICT OKARA"
HEADMASTER = "SAFDAR JAVED"

def calculate_grade(per):
    """Automatic Grading Logic"""
    if per >= 80: return "A+"
    elif per >= 70: return "A"
    elif per >= 60: return "B"
    elif per >= 50: return "C"
    elif per >= 40: return "D"
    else: return "F"

class ReportPDF(FPDF):
    def __init__(self, logo_img=None):
        super().__init__()
        self.logo_img = logo_img

    def header(self):
        # Border
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287)
        
        # Logo Logic
        if self.logo_img:
            buf = io.BytesIO()
            self.logo_img.save(buf, format='PNG')
            buf.seek(0)
            self.image(buf, 10, 8, 25)
            
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'SCHOOL EDUCATION DEPARTMENT', ln=True, align='C')
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, SCHOOL_NAME, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'EMIS CODE: {EMIS_CODE}', ln=True, align='C')
        self.ln(10)

def generate_pdf_blob(data, logo):
    pdf = ReportPDF(logo_img=logo)
    pdf.add_page()
    
    # Student Info
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

    # Marks Table Header
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(100, 8, ' SUBJECT', 1, 0, 'L', True)
    pdf.cell(45, 8, ' TOTAL MARKS', 1, 0, 'C', True)
    pdf.cell(50, 8, ' OBTAINED', 1, 1, 'C', True)

    # Table Body
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for sub, m in data['marks'].items():
        pdf.cell(100, 8, f" {sub}", 1)
        pdf.cell(45, 8, str(m[0]), 1, 0, 'C')
        pdf.cell(50, 8, str(m[1]), 1, 1, 'C')

    # Grand Totals
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 8, ' GRAND TOTAL', 1)
    pdf.cell(45, 8, str(data['grand_total']), 1, 0, 'C')
    pdf.cell(50, 8, str(data['grand_obtained']), 1, 1, 'C')
    
    # Bottom Stats
    pdf.ln(10)
    pdf.set_font('Arial', '', 8)
    pdf.cell(48, 5, "PERCENTAGE:", 0, 0)
    pdf.cell(48, 5, "POSITION:", 0, 0)
    pdf.cell(48, 5, "PERFORMANCE:", 0, 0)
    pdf.cell(48, 5, "FINAL GRADE:", 0, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(46, 8, f"{data['percentage']}%", 1, 0, 'C')
    pdf.cell(2, 8, "")
    pdf.cell(46, 8, data['position'], 1, 0, 'C')
    pdf.cell(2, 8, "")
    pdf.cell(46, 8, data['performance'], 1, 0, 'C')
    pdf.cell(2, 8, "")
    pdf.cell(46, 8, data['grade'], 1, 1, 'C')

    # Quotes
    pdf.ln(25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, '"Education is the most powerful weapon which you can use to change the world."', ln=True, align='C')
    pdf.cell(0, 5, '"The roots of education are bitter, but the fruit is sweet."', ln=True, align='C')

    # Footer Signatures
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 0, '', 'T', 0)
    pdf.cell(20, 0, '')
    pdf.cell(85, 0, '', 'T', 1)
    pdf.cell(90, 10, 'CLASS TEACHER', 0, 0, 'C')
    pdf.cell(105, 10, f'SENIOR HEAD MASTER ({HEADMASTER})', 0, 1, 'R')
    
    pdf.set_font('Arial', '', 7)
    pdf.cell(0, 10, f"Result Declaration Date: {data['date']}", ln=True, align='R')

    return pdf.output()

# --- STREAMLIT UI ---
st.set_page_config(page_title="Result System GHS Bhutta", layout="wide")

# Persistent State Initialization
if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = "Result.pdf"

# Sidebar
st.sidebar.header("School Settings")
uploaded_logo = st.sidebar.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
logo_pil = Image.open(uploaded_logo) if uploaded_logo else None

st.title("📋 GHS Bhutta Mohabbat - Result System")

# The Form
with st.form("main_result_form"):
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Student Name", "AQIB")
    father = c2.text_input("Father Name", "ALI")
    roll = c3.text_input("Roll No", "15")
    
    c4, c5, c6 = st.columns(3)
    s_class = c4.text_input("Class", "8")
    section = c5.text_input("Section", "A")
    performance = c6.text_input("Performance (Manual)", "Excellent")
    
    position = st.text_input("Position", "---")
    res_date = st.date_input("Declaration Date", datetime.date(2026, 3, 31))

    st.subheader("Subjects, Selection & Marks Entry")
    subjects_list = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    
    final_marks = {}
    cols = st.columns(2)
    for i, s in enumerate(subjects_list):
        with cols[i % 2]:
            st.write(f"--- **{s}** ---")
            chk, t_col, o_col = st.columns([1, 2, 2])
            is_active = chk.checkbox("On", value=True, key=f"active_{s}")
            if is_active:
                def_total = 75 if s == "Islamiat" else 50 #
                tm = t_col.number_input("Total", value=def_total, key=f"tm_{s}")
                om = o_col.number_input("Obtained", value=0, key=f"om_{s}")
                final_marks[s] = [tm, om]

    generate_btn = st.form_submit_button("Step 1: Process Result")

# Logic after form submit
if generate_btn:
    if final_marks:
        total_sum = sum(v[0] for v in final_marks.values())
        obtained_sum = sum(v[1] for v in final_marks.values())
        percent = round((obtained_sum / total_sum) * 100, 1) if total_sum > 0 else 0
        auto_grade = calculate_grade(percent)
        
        payload = {
            "name": name, "father": father, "class": s_class, "roll": roll, 
            "section": section, "marks": final_marks, "grand_total": total_sum, 
            "grand_obtained": obtained_sum, "percentage": percent, 
            "grade": auto_grade, "performance": performance, "position": position,
            "date": res_date.strftime("%d-%m-%Y")
        }
        
        st.session_state.pdf_ready = generate_pdf_blob(payload, logo_pil)
        st.session_state.file_name = f"{name}_Result.pdf"
        st.success(f"Result Processed for {name}! Now click Download below.")
    else:
        st.error("Select at least one subject!")

# DOWNLOAD BUTTON (ALWAYS OUTSIDE FORM)
if st.session_state.pdf_ready:
    st.download_button(
        label="📥 Step 2: Download PDF Report Card",
        data=st.session_state.pdf_ready,
        file_name=st.session_state.file_name,
        mime="application/pdf"
    )
