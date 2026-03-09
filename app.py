import streamlit as st
import pandas as pd
from fpdf import FPDF
import sqlite3
import plotly.express as px
import io

# --- Configuration & Branding ---
SCHOOL_NAME = "GOVT. HIGH SCHOOL BHUTTA MOHABBAT" #
EMIS_CODE = "39310025 | DISTRICT OKARA" #
HEADMASTER = "SAFDAR JAVED" #

# --- Database Functions ---
def init_db():
    conn = sqlite3.connect('ghs_bhutta.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, father TEXT, class TEXT, roll TEXT, section TEXT,
                    english INTEGER, urdu INTEGER, math INTEGER, islamiat INTEGER,
                    science INTEGER, s_study INTEGER, computer INTEGER, quran INTEGER,
                    total_obt INTEGER, percentage REAL, grade TEXT)''')
    conn.commit()
    conn.close()

def save_record(d):
    conn = sqlite3.connect('ghs_bhutta.db')
    df = pd.DataFrame([d])
    df.to_sql('results', conn, if_exists='append', index=False)
    conn.close()

# --- Logic: Grading & Positions ---
def get_grade(per):
    if per >= 80: return "A+", "Excellent"
    if per >= 70: return "A", "Very Good"
    if per >= 60: return "B", "Good"
    if per >= 50: return "C", "Satisfactory"
    return "F", "Poor"

# --- PDF Engine ---
class PDF(FPDF):
    def header(self):
        self.rect(5, 5, 200, 287)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 5, 'SCHOOL EDUCATION DEPARTMENT', ln=True, align='C')
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, SCHOOL_NAME, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'EMIS CODE: {EMIS_CODE}', ln=True, align='C')
        self.ln(10)

def generate_pdf(row, pos):
    pdf = PDF()
    pdf.add_page()
    
    # Student Info Header
    pdf.set_fill_color(112, 128, 144)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(90, 8, f" NAME: {row['name'].upper()}", fill=True)
    pdf.cell(10, 8, "")
    pdf.cell(95, 8, f" FATHER NAME: {row['father'].upper()}", fill=True, ln=True)
    pdf.ln(2)
    pdf.cell(45, 8, f" CLASS: {row['class']}", fill=True)
    pdf.cell(5, 8, "")
    pdf.cell(45, 8, f" ROLL NO: {row['roll']}", fill=True)
    pdf.cell(5, 8, "")
    pdf.cell(95, 8, f" SECTION: {row['section']}", fill=True, ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_fill_color(50, 50, 50)
    pdf.cell(100, 8, ' SUBJECT', 1, 0, 'L', True)
    pdf.cell(45, 8, ' TOTAL MARKS', 1, 0, 'C', True)
    pdf.cell(50, 8, ' OBTAINED', 1, 1, 'C', True)

    # Subject Data
    pdf.set_text_color(0, 0, 0)
    subs = {
        "English": [50, row['english']], "Urdu": [50, row['urdu']], 
        "Mathematics": [50, row['math']], "Islamiat": [75, row['islamiat']],
        "Science": [50, row['science']], "Social Study": [50, row['s_study']],
        "Computer": [50, row['computer']], "Tarjuma-tu-Quran": [50, row['quran']]
    }
    
    for s, m in subs.items():
        pdf.cell(100, 8, f" {s}", 1)
        pdf.cell(45, 8, str(m[0]), 1, 0, 'C')
        pdf.cell(50, 8, str(m[1]), 1, 1, 'C')

    # Totals
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(100, 8, ' GRAND TOTAL', 1)
    pdf.cell(45, 8, '425', 1, 0, 'C')
    pdf.cell(50, 8, str(row['total_obt']), 1, 1, 'C')
    
    # Metrics
    pdf.ln(10)
    grade, perf = get_grade(row['percentage'])
    pdf.set_font('Arial', '', 8)
    cols = ["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]
    vals = [f"{row['percentage']}%", str(pos), perf, grade]
    for c in cols: pdf.cell(48, 5, c, 0, 0, 'L')
    pdf.ln(5)
    for v in vals: pdf.cell(46, 8, v, 1, 0, 'C'); pdf.cell(2, 8, "")

    # Signatures
    pdf.ln(30)
    pdf.cell(90, 0, '', 'T', 0, 'C')
    pdf.cell(20, 0, '')
    pdf.cell(85, 0, '', 'T', 1, 'C')
    pdf.cell(90, 10, 'CLASS TEACHER', 0, 0, 'C')
    pdf.cell(105, 10, f'SENIOR HEAD MASTER ({HEADMASTER})', 0, 1, 'R')

    return pdf.output()

# --- Streamlit UI ---
st.set_page_config(page_title="GHS Master System", layout="wide")
init_db()

# Simple Security
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.sidebar.text_input("Enter Teacher Password", type="password")
    if st.sidebar.button("Login"):
        if pw == "ghs123": # Placeholder password
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Wrong Password")
    st.stop()

# Main App Tabs
tab1, tab2, tab3, tab4 = st.tabs(["➕ Single Entry", "📊 Bulk Upload", "📜 Records & Positions", "📈 Analytics"])

with tab1:
    with st.form("single_form"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Student Name")
        father = c2.text_input("Father Name")
        roll = c3.text_input("Roll No")
        
        st.write("### Marks Entry")
        m_cols = st.columns(4)
        m_vals = {}
        subjects = ["English", "Urdu", "Math", "Islamiat", "Science", "S_Study", "Computer", "Quran"]
        for i, s in enumerate(subjects):
            with m_cols[i % 4]:
                m_vals[s.lower()] = st.number_input(s, min_value=0, max_value=100, step=1)
        
        if st.form_submit_button("Save Student"):
            total_obt = sum(m_vals.values())
            per = round((total_obt / 425) * 100, 2)
            grd, _ = get_grade(per)
            data = {**{"name":name, "father":father, "class":"8", "roll":roll, "section":"A", "year":"2025-26", 
                      "total_obt":total_obt, "percentage":per, "grade":grd}, **m_vals}
            save_record(data)
            st.success("Record Saved!")

with tab2:
    st.info("Download the template, fill it, and upload back.")
    template = pd.DataFrame(columns=["name", "father", "roll", "section", "english", "urdu", "math", "islamiat", "science", "s_study", "computer", "quran"])
    st.download_button("Download Excel Template", template.to_csv(index=False), "template.csv")
    
    uploaded_file = st.file_uploader("Upload Filled Excel/CSV", type=['csv', 'xlsx'])
    if uploaded_file:
        up_df = pd.read_csv(uploaded_file)
        if st.button("Process Bulk Upload"):
            conn = sqlite3.connect('ghs_bhutta.db')
            for _, r in up_df.iterrows():
                t_obt = r['english']+r['urdu']+r['math']+r['islamiat']+r['science']+r['s_study']+r['computer']+r['quran']
                per = round((t_obt/425)*100, 2)
                grd, _ = get_grade(per)
                # Save each
                c = conn.cursor()
                c.execute("INSERT INTO results (name, father, class, roll, section, english, urdu, math, islamiat, science, s_study, computer, quran, total_obt, percentage, grade) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (r['name'], r['father'], "8", r['roll'], r['section'], r['english'], r['urdu'], r['math'], r['islamiat'], r['science'], r['s_study'], r['computer'], r['quran'], t_obt, per, grd))
            conn.commit()
            conn.close()
            st.success("All records uploaded successfully!")

with tab3:
    conn = sqlite3.connect('ghs_bhutta.db')
    df_all = pd.read_sql("SELECT * FROM results", conn)
    if not df_all.empty:
        # Calculate Positions
        df_all['position'] = df_all['total_obt'].rank(ascending=False, method='min').astype(int)
        st.dataframe(df_all[['position', 'roll', 'name', 'total_obt', 'percentage', 'grade']], use_container_width=True)
        
        st.divider()
        search_roll = st.text_input("Enter Roll No to Generate PDF")
        if search_roll:
            student = df_all[df_all['roll'] == search_roll]
            if not student.empty:
                s_row = student.iloc[0]
                pdf_file = generate_pdf(s_row, s_row['position'])
                st.download_button(f"Download PDF for {s_row['name']}", pdf_file, f"{s_row['name']}_Result.pdf")
    conn.close()

with tab4:
    if not df_all.empty:
        fig = px.bar(df_all, x="name", y="percentage", color="grade", title="Class Performance Overview")
        st.plotly_chart(fig, use_container_width=True)
