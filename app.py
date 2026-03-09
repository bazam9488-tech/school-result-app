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
    """Percentage ke mutabiq automatic grade nikalne ka logic"""
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
        # Result Card ka Border
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287) 
        
        # Logo Logic (Sidebar se upload hone wala logo)
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
    
    # Student Details Section (Slate Gray Bars)
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
    pdf.cell(10, 8, "")
    pdf.cell(90, 8, f" SECTION: {data['section']}", fill=True, ln=True)
    pdf.ln(10)

    # Marks Table Header
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(100, 8, ' SUBJECT', 1, 0, 'L', True)
    pdf.cell(45, 8, ' TOTAL MARKS', 1, 0, 'C', True)
    pdf.cell(50, 8, ' OBTAINED', 1, 1, 'C', True)

    # Subject Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for s, m in data['marks'].items():
        pdf.cell(100, 8, f" {s}", 1)
        pdf.cell(45, 8, str(m[0]), 1, 0, 'C')
        pdf.cell(50, 8, str(m[1]), 1, 1, 'C')

    # Grand Totals
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 8, ' GRAND TOTAL', 1)
    pdf.cell(45, 8, str(data['t_total']), 1, 0, 'C')
    pdf.cell(50, 8, str(data['t_obt']), 1, 1, 'C')
    
    # Grading & Performance Boxes
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
    pdf.cell(90, 0, '', 'T', 0)
    pdf.cell(20, 0, '')
    pdf.cell(85, 0, '', 'T', 1)
    pdf.cell(90, 10, 'CLASS TEACHER', 0, 0, 'C')
    pdf.cell(105, 10, f'SENIOR HEAD MASTER ({HEADMASTER})', 0, 1, 'R')
    
    pdf.set_font('Arial', '', 7)
    pdf.cell(0, 10, f"Result Declaration Date: {data['date']}", ln=True, align='R')

    return pdf.output()

# --- Streamlit Frontend ---
st.set_page_config(page_title="GHS Result Generator", layout="wide")

# Persistent data storage (Download error fix)
if 'pdf_blob' not in st.session_state:
    st.session_state.pdf_blob = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# Sidebar settings
st.sidebar.title("App Settings")
logo_upload = st.sidebar.file_uploader("Upload School Logo", type=['png', 'jpg', 'jpeg'])
logo_image = Image.open(logo_upload) if logo_upload else None

st.title("📋 GHS Bhutta Mohabbat - Result System")

with st.form("input_form"):
    # Student Personal Details
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Student Name", "AQIB")
    father = c2.text_input("Father Name", "ALI")
    roll = c3.text_input("Roll No", "15")
    
    c4, c5, c6 = st.columns(3)
    s_class = c4.text_input("Class", "8")
    section = c5.text_input("Section", "A")
    performance = c6.text_input("Performance (Manual Remarks)", "Excellent")
    
    position = st.text_input("Position (e.g. 1st, 2nd, ---)", "---")
    res_date = st.date_input("Declaration Date", datetime.date(2026, 3, 31))

    st.divider()
    st.subheader("Select Subjects & Edit Marks")
    
    all_subjects = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    selected_marks = {}
    
    # 2-column layout for subjects
    sc1, sc2 = st.columns(2)
    for i, s in enumerate(all_subjects):
        with (sc1 if i % 2 == 0 else sc2):
            st.write(f"**{s}**")
            chk, t_col, o_col = st.columns([1, 2, 2])
            is_active = chk.checkbox("On", value=True, key=f"active_{s}")
            if is_active:
                def_total = 75 if s == "Islamiat" else 50
                tm = t_col.number_input("Total Marks", value=def_total, key=f"tm_{s}")
                om = o_col.number_input("Obtained", value=0, key=f"om_{s}")
                selected_marks[s] = [tm, om]

    # Generate Button
    process_btn = st.form_submit_button("Step 1: Process Result Card")

# Logic to handle PDF generation (Outside the form to fix download button error)
if process_btn:
    if selected_marks:
        t_sum = sum(v[0] for v in selected_marks.values())
        o_sum = sum(v[1] for v in selected_marks.values())
        per = round((o_sum / t_sum) * 100, 1) if t_sum > 0 else 0
        
        final_info = {
            "name": name, "father": father, "class": s_class, "roll": roll, 
            "section": section, "marks": selected_marks, "t_total": t_sum, 
            "t_obt": o_sum, "per": per, "grade": get_auto_grade(per), 
            "perf": performance, "pos": position, "date": res_date.strftime("%d-%m-%Y")
        }
        
        st.session_state.pdf_blob = generate_pdf(final_info, logo_image)
        st.session_state.file_name = f"{name}_Result.pdf"
        st.success(f"Result for {name} generated! Now click the Download button below.")
    else:
        st.error("Please select at least one subject.")

# Step 2: Download Button (STRICTLY OUTSIDE THE FORM)
if st.session_state.pdf_blob:
    st.divider()
    st.download_button(
        label=f"📥 Step 2: Download {st.session_state.file_name}",
        data=st.session_state.pdf_blob,
        file_name=st.session_state.file_name,
        mime="application/pdf"
    )
