import streamlit as st
from fpdf import FPDF
import pandas as pd
from datetime import date

# 1. PDF Generation Class - Modified for Borders
class ResultCard(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.theme_color = (120, 150, 170) # Grey-Blue from image

    def draw_page_border(self):
        # Setting border parameters (margins from edge)
        m = 8 # Outer margin
        self.set_line_width(1.0) # Thick line
        self.set_draw_color(self.theme_color[0], self.theme_color[1], self.theme_color[2])
        
        # 1. Outer Rectangle (A4 is 210x297mm)
        self.rect(m, m, self.w - 2*m, self.h - 2*m, 'D')

        # 2. Inner Thin Rectangle for 'Stylish' effect
        m_inner = m + 2.0
        self.set_line_width(0.2)
        self.rect(m_inner, m_inner, self.w - 2*m_inner, self.h - 2*m_inner, 'D')
        
        # Reset line drawing to default for other elements
        self.set_line_width(0.2)
        self.set_draw_color(0,0,0)

    def header(self):
        # Draw borders first on every page
        self.draw_page_border()

        # Logo and Title Positioning adjusted for borders
        self.set_y(15) # Start content slightly lower

        if self.logo_path:
            try:
                # Logo position (x, y, width)
                self.image(self.logo_path, 15, 15, 25) 
            except: pass
        
        # School Details (Center Aligned)
        self.set_font("Arial", 'B', 12)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, "SCHOOL EDUCATION DEPARTMENT", ln=True, align='C')
        self.set_font("Arial", 'B', 18)
        self.set_text_color(0, 0, 0)
        self.cell(0, 9, "GOVT. HIGH SCHOOL BHUTTA MOHABBAT", ln=True, align='C')
        self.set_font("Arial", '', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, "EMIS CODE: 39310025 | DISTRICT OKARA", ln=True, align='C')
        self.ln(10)

# 2. Logic Functions (Unchanged)
def get_grade_and_remarks(percentage):
    if percentage >= 80: return "A+", "Exceptional Performance"
    elif percentage >= 70: return "A", "Excellent"
    elif percentage >= 60: return "B", "Very Good"
    elif percentage >= 50: return "C", "Good"
    elif percentage >= 40: return "D", "Fair"
    else: return "E", "Needs Improvement"

# 3. Session State for History (Unchanged)
if 'history' not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="GHS Result System", page_icon=":mortar_board:", layout="wide")
st.title("GHS Bhutta Mohabbat - Advanced Result System")

# Logo Upload (Optional)
uploaded_logo = st.file_uploader("Upload School Logo (Optional)", type=['jpg', 'png', 'jpeg'])

# --- Input Form ---
with st.form("result_form", clear_on_submit=False):
    st.subheader("1. Student Personal Information")
    c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1])
    with c1: name = st.text_input("Student Name")
    with c2: f_name = st.text_input("Father Name")
    with c3: s_class = st.text_input("Class", value="8")
    with c4: roll_no = st.text_input("Roll No")
    with c5: section = st.text_input("Section", value="A")

    st.subheader("2. Select Subjects & Enter Marks")
    all_subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks_input = {}
    
    # Checkbox option for each subject in columns
    col_a, col_b = st.columns(2)
    for i, sub in enumerate(all_subs):
        current_col = col_a if i % 2 == 0 else col_b
        with current_col:
            is_selected = st.checkbox(sub, value=True, key=f"check_{sub}")
            if is_selected:
                m_c1, m_c2 = st.columns([1,1])
                with m_c1: t_m = st.number_input(f"Total", value=50, key=f"t_{sub}", min_value=1)
                with m_c2: o_m = st.number_input(f"Obtained", value=0, key=f"o_{sub}", min_value=0)
                marks_input[sub] = [t_m, o_m]

    generate_btn = st.form_submit_button("Generate & Save Result Card")

if generate_btn and name and roll_no:
    # Calculations
    t_max = sum([m[0] for m in marks_input.values()])
    t_obt = sum([m[1] for m in marks_input.values()])
    per = (t_obt / t_max * 100) if t_max > 0 else 0
    grade, remarks = get_grade_and_remarks(per)

    # Save to Session History
    st.session_state.history.append({
        "Date": date.today().strftime("%Y-%m-%d"),
        "Name": name, "Class": f"{s_class}-{section}", "Roll No": roll_no, 
        "Obtained": t_obt, "Total": t_max, "Percentage": f"{per:.1f}%", "Grade": grade
    })

    # PDF Generation
    pdf = ResultCard(logo_path=uploaded_logo)
    pdf.add_page() # Header (which calls draw_page_border) runs here
    
    # Style Variables
    theme = pdf.theme_color
    content_width = pdf.w - 30 # Account for margins/border
    col_width = content_width / 2

    # Info Bar - Centered on page inside border
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(theme[0], theme[1], theme[2]) # Theme Blue
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col_width, 11, f" NAME: {name.upper()}", fill=True, border='TLB')
    pdf.cell(col_width, 11, f" FATHER NAME: {f_name.upper()}", fill=True, border='TRB', ln=True)
    
    pdf.set_fill_color(220, 230, 240) # Lighter theme blue for sub-info
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    sub_col = content_width / 3
    pdf.cell(sub_col, 8, f" Class: {s_class}", fill=True, border=1)
    pdf.cell(sub_col, 8, f" Roll No: {roll_no}", fill=True, border=1)
    pdf.cell(sub_col, 8, f" Section: {section}", fill=True, border=1, ln=True)
    
    # Marks Table Header
    pdf.ln(5)
    pdf.set_fill_color(50, 50, 50) # Dark grey header
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    
    table_w = content_width
    c_sub, c_tm, c_obt = table_w * 0.5, table_w * 0.25, table_w * 0.25
    
    pdf.cell(c_sub, 10, " SUBJECT", border=1, fill=True, align='C')
    pdf.cell(c_tm, 10, " TOTAL MARKS", border=1, fill=True, align='C')
    pdf.cell(c_obt, 10, " OBTAINED MARKS", border=1, fill=True, align='C', ln=True)
    
    # Marks Table Content
    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial", '', 10)
    alternate = False
    for s, m in marks_input.items():
        if alternate: pdf.set_fill_color(245, 245, 245) # Light alternate row color
        else: pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(c_sub, 9, f" {s}", border=1, fill=True)
        pdf.cell(c_tm, 9, f"{m[0]}", border=1, fill=True, align='C')
        pdf.cell(c_obt, 9, f"{m[1]}", border=1, fill=True, align='C', ln=True)
        alternate = not alternate

    # Grand Total Row
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(theme[0], theme[1], theme[2]) # Theme Blue
    pdf.set_text_color(255,255,255)
    pdf.cell(c_sub, 10, " GRAND TOTAL", border=1, fill=True)
    pdf.cell(c_tm, 10, f"{t_max}", border=1, fill=True, align='C')
    pdf.cell(c_obt, 10, f"{t_obt}", border=1, fill=True, align='C', ln=True)

    # Final Stats - Boxes styling
    pdf.ln(7)
    pdf.set_text_color(0,0,0)
    stat_w = content_width / 4
    pdf.cell(stat_w, 12, f"PERCENTAGE: {per:.1f}%", border=1, align='C')
    pdf.cell(stat_w, 12, f"POSITION: ---", border=1, align='C')
    pdf.cell(stat_w, 12, f"GRADE: {grade}", border=1, align='C')
    pdf.cell(stat_w, 12, f"REMARKS: {grade}", border=1, align='C', ln=True) # Changed from text remarks to Grade for brevity on mobile, you can change back to {remarks}

    # Footer - Signatures
    pdf.set_y(pdf.h - 40) # Position signatures near bottom
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(content_width/2, 5, "____________________", align='C')
    pdf.cell(content_width/2, 5, "____________________", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(content_width/2, 5, "CLASS TEACHER", align='C')
    pdf.cell(content_width/2, 5, "SENIOR HEAD MASTER (SAFDAR JAVED)", ln=True, align='C')

    # Output Fix for Streamlit/fpdf2
    pdf_bytes = pdf.output()
    st.success(f"{name} (Roll No: {roll_no}) ka result save aur generate ho gaya hai!")
    st.download_button(
        label="📄 Download Result Card (PDF)", 
        data=bytes(pdf_bytes), 
        file_name=f"{roll_no}_{name}_Result.pdf",
        mime="application/pdf"
    )
elif generate_btn:
    st.error("Student Name aur Roll Number lazmi likhen.")

# --- History Section (Saved Results) ---
if st.session_state.history:
    st.write("---")
    st.subheader("📁 Session History (Saved Results)")
    st.info("Ye data sirf is browser session mein save hai. Refresh karne par delete ho jayega.")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True) # Interactive table
