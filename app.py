import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import io

# --- School Branding Data ---
SCHOOL_NAME = "GOVT. HIGH SCHOOL BHUTTA MOHABBAT"
EMIS_CODE = "39310025 | DISTRICT OKARA"
HEADMASTER = "SAFDAR JAVED"

def get_auto_grade(per):
    if per >= 80: return "A+"
    elif per >= 70: return "A"
    elif per >= 60: return "B"
    elif per >= 50: return "C"
    elif per >= 40: return "D"
    else: return "F"

class PDF(FPDF):
    def __init__(self, logo_image=None):
        super().__init__()
        self.logo_image = logo_image

    def header(self):
        # Result Card Border
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287) 
        
        # Logo Logic
        if self.logo_image:
            img_buffer = io.BytesIO()
            self.logo_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            self.image(img_buffer, 10, 8, 25)
            
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'SCHOOL EDUCATION DEPARTMENT', ln=True, align='C')
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, SCHOOL_NAME, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'EMIS CODE: {EMIS_CODE}', ln=True, align='C')
        self.ln(10)

def generate_pdf(data, logo):
    pdf = PDF(logo_image=logo)
    pdf.add_page()
    
    # Student Info Section
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

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for s, m in data['marks'].items():
        pdf.cell(100, 8, f" {s}", 1)
        pdf.cell(45, 8, str(m[0]), 1, 0, 'C')
        pdf.cell(50, 8, str(m[1]), 1, 1, 'C')

    # Grand Total
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 8, ' GRAND TOTAL', 1)
    pdf.cell(45, 8, str(data['t_total']), 1, 0, 'C')
    pdf.cell(50, 8, str(data['t_obt']), 1, 1, 'C')
    
    # Bottom Metrics
    pdf.ln(10)
    pdf.set_font('Arial', '', 8)
    cols = ["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]
    vals = [f"{data['per']}%", data['pos'], data['perf'], data['grade']]
    for c in cols: pdf.cell(48, 5, c, 0, 0, 'L')
    pdf.ln(5)
    for v in vals: pdf.cell(46, 8, v, 1, 0, 'C'); pdf.cell(2, 8, "")

    # Educational Quotes
    pdf.ln(25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, '"Education is the most powerful weapon which you can use to change the world."', ln=True, align='C')
    pdf.cell(0, 5, '"The roots of education are bitter, but the fruit is sweet."', ln=True, align='C')

    # Signatures
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 0, '', 'T', 0, 'C')
    pdf.cell(20, 0, '')
    pdf.cell(85, 0, '', 'T', 1, 'C')
    pdf.cell(90, 10, 'CLASS TEACHER', 0, 0, 'C')
    pdf.cell(105, 10, f'SENIOR HEAD MASTER ({HEADMASTER})', 0, 1, 'R')
    
    pdf.set_font('Arial', '', 7)
    pdf.cell(0, 10, f"Result Declaration Date: {data['date']}", ln=True, align='R')

    return pdf.output()

# --- Streamlit Frontend ---
st.set_page_config(page_title="GHS Bhutta Result App", layout="wide")

# Persistent State
if 'pdf_blob' not in st.session_state:
    st.session_state.pdf_blob = None
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

# Sidebar for Logo
st.sidebar.title("App Settings")
logo_upload = st.sidebar.file_uploader("Upload School Logo", type=['png', 'jpg', 'jpeg'])
logo_image = Image.open(logo_upload) if logo_upload else None

st.title("📋 GHS Bhutta Mohabbat - Result Management System")

with st.form("master_input_form"):
    c1, c2, c3 = st.columns(3)
    s_name = c1.text_input("Student Name", "AQIB")
    f_name = c2.text_input("Father Name", "ALI")
    roll_no = c3.text_input("Roll No", "15")
    
    c4, c5, c6 = st.columns(3)
    grade_class = c4.text_input("Class", "8")
    section = c5.text_input("Section", "A")
    performance = c6.text_input("Manual Performance", "Excellent")
    
    position = st.text_input("Position", "---")
    res_date = st.date_input("Result Declaration Date", datetime.date(2026, 3, 31))

    st.subheader("Select Subjects & Edit Marks")
    subs_list = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks_map = {}
    
    # 2-column grid for subjects
    sc1, sc2 = st.columns(2)
    for i, s in enumerate(subs_list):
        current_col = sc1 if i % 2 == 0 else sc2
        with current_col:
            st.write(f"**{s}**")
            cb, tm_col, om_col = st.columns([1, 2, 2])
            is_checked = cb.checkbox("On", value=True, key=f"is_{s}")
            if is_checked:
                # Default total marks logic
                def_tm = 75 if s == "Islamiat" else 50
                tm_val = tm_col.number_input("Total Marks", value=def_tm, key=f"t_{s}")
                om_val = om_col.number_input("Obtained", value=0, key=f"o_{s}")
                marks_map[s] = [tm_val, om_val]

    # Form Submit
    process_trigger = st.form_submit_button("Generate Result Card")

# Logic after form submission (OUTSIDE THE FORM)
if process_trigger:
    if marks_map:
        t_grand = sum(v[0] for v in marks_map.values())
        o_grand = sum(v[1] for v in marks_map.values())
        percentage = round((o_grand / t_grand) * 100, 1) if t_grand > 0 else 0
        
        final_payload = {
            "name": s_name, "father": f_name, "class": grade_class, "roll": roll_no, 
            "section": section, "marks": marks_map, "t_total": t_grand, 
            "t_obt": o_grand, "per": percentage, "grade": get_auto_grade(percentage), 
            "perf": performance, "pos": position, "date": res_date.strftime("%d-%m-%Y")
        }
        
        st.session_state.pdf_blob = generate_pdf(final_payload, logo_image)
        st.session_state.student_name = s_name
        st.success(f"Result for {s_name} is ready! Grade: {get_auto_grade(percentage)}")
    else:
        st.error("Please select at least one subject.")

# Final Download Button (Permanently Fixed Outside Form)
if st.session_state.pdf_blob:
    st.download_button(
        label="📥 Download PDF Result Card",
        data=st.session_state.pdf_blob,
        file_name=f"{st.session_state.student_name}_Result.pdf",
        mime="application/pdf"
    )
