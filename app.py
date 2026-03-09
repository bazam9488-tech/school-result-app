import streamlit as st
from fpdf import FPDF
import datetime

# --- School Details ---
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
    def __init__(self, logo_file=None):
        super().__init__()
        self.logo_file = logo_file

    def header(self):
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287) 
        
        # Logo Logic
        if self.logo_file:
            self.image(self.logo_file, 10, 8, 25)
            
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'SCHOOL EDUCATION DEPARTMENT', ln=True, align='C')
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, SCHOOL_NAME, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'EMIS CODE: {EMIS_CODE}', ln=True, align='C')
        self.ln(10)

def generate_pdf(data, logo):
    pdf = PDF(logo_file=logo)
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
    
    # Metrics Box
    pdf.ln(10)
    pdf.set_font('Arial', '', 8)
    cols = ["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]
    vals = [f"{data['per']}%", data['pos'], data['perf'], data['grade']]
    for c in cols: pdf.cell(48, 5, c, 0, 0, 'L')
    pdf.ln(5)
    for v in vals: pdf.cell(46, 8, v, 1, 0, 'C'); pdf.cell(2, 8, "")

    # Quotes & Footer
    pdf.ln(25)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, '"Education is the most powerful weapon which you can use to change the world."', ln=True, align='C')
    pdf.cell(0, 5, '"The roots of education are bitter, but the fruit is sweet."', ln=True, align='C')

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

# --- Streamlit UI ---
st.set_page_config(page_title="Result Generator", layout="wide")
st.sidebar.title("App Settings")
logo_file = st.sidebar.file_uploader("Upload School Logo", type=['png', 'jpg', 'jpeg'])

st.title("📋 GHS Bhutta Mohabbat - Result System")

if 'pdf' not in st.session_state:
    st.session_state.pdf = None

with st.form("input_form"):
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Student Name")
    father = c2.text_input("Father Name")
    roll = c3.text_input("Roll No")
    
    c4, c5, c6 = st.columns(3)
    s_class = c4.text_input("Class", "8")
    section = c5.text_input("Section", "A")
    perf = c6.text_input("Manual Performance", "Excellent")
    
    pos = st.text_input("Position", "---")
    res_date = st.date_input("Result Declaration Date", datetime.date(2026, 3, 31))

    st.subheader("Select Subjects & Edit Marks")
    subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks_data = {}
    
    cols = st.columns(2)
    for i, s in enumerate(subs):
        with cols[i % 2]:
            st.write(f"**{s}**")
            cb, t_col, o_col = st.columns([1, 2, 2])
            is_active = cb.checkbox("Include", value=True, key=f"cb_{s}")
            if is_active:
                def_t = 75 if s == "Islamiat" else 50 #
                total_m = t_col.number_input("Total Marks", value=def_t, key=f"t_{s}")
                obt_m = o_col.number_input("Obtained", value=0, key=f"o_{s}")
                marks_data[s] = [total_m, obt_m]

    submitted = st.form_submit_button("Preview & Generate Data")

if submitted:
    if marks_data:
        t_sum = sum(v[0] for v in marks_data.values())
        o_sum = sum(v[1] for v in marks_data.values())
        per = round((o_sum / t_sum) * 100, 1) if t_sum > 0 else 0
        
        final_info = {
            "name": name, "father": father, "class": s_class, "roll": roll, 
            "section": section, "marks": marks_data, "t_total": t_sum, 
            "t_obt": o_sum, "per": per, "grade": get_auto_grade(per), 
            "perf": perf, "pos": pos, "date": res_date.strftime("%d-%m-%Y")
        }
        st.session_state.pdf = generate_pdf(final_info, logo_file)
        st.session_state.st_name = name
        st.success(f"{name} ka data process ho gaya! Niche se PDF download karein.")

# Download Button Outside Form
if st.session_state.pdf:
    st.download_button(
        label="📥 Download PDF Result Card",
        data=st.session_state.pdf,
        file_name=f"{st.session_state.st_name}_Result.pdf",
        mime="application/pdf"
    )
