import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
import datetime

# --- Page Config ---
st.set_page_config(page_title="GHS Bhutta Mohabbat Result Generator", layout="centered")

def get_grade_info(percentage):
    if percentage >= 80: return "A+", "Excellent"
    elif percentage >= 70: return "A", "Very Good"
    elif percentage >= 60: return "B", "Good"
    elif percentage >= 50: return "C", "Satisfactory"
    elif percentage >= 40: return "D", "Fair"
    else: return "F", "Poor"

def generate_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Outer Borders
    p.setStrokeColor(colors.HexColor("#7B96AC"))
    p.setLineWidth(2)
    p.rect(15, 15, width - 30, height - 30)
    p.setLineWidth(1)
    p.rect(20, 20, width - 40, height - 40)

    # Header Section
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 45, "SCHOOL EDUCATION DEPARTMENT")
    
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 65, data['school_name'].upper())
    
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2, height - 80, f"EMIS CODE: {data['emis']} | DISTRICT {data['district'].upper()}")
    
    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(colors.HexColor("#7B96AC"))
    p.drawCentredString(width / 2, height - 110, "STUDENT REPORT CARD")

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, height - 125, f"Session {data['session']}")

    # Student Info Bars (Blue Background)
    p.setFillColor(colors.HexColor("#7B96AC"))
    p.rect(40, height - 155, 270, 20, fill=1, stroke=1)
    p.rect(310, height - 155, 245, 20, fill=1, stroke=1)
    p.rect(40, height - 175, 175, 20, fill=1, stroke=1)
    p.rect(215, height - 175, 175, 20, fill=1, stroke=1)
    p.rect(390, height - 175, 165, 20, fill=1, stroke=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(45, height - 148, f"NAME: {data['name'].upper()}")
    p.drawString(315, height - 148, f"FATHER NAME: {data['father_name'].upper()}")
    p.drawString(45, height - 168, f"CLASS: {data['class']}")
    p.drawString(220, height - 168, f"ROLL NO: {data['roll']}")
    p.drawString(395, height - 168, f"SECTION: {data['section']}")

    # Marks Table
    y_table = height - 210
    p.setFillColor(colors.HexColor("#333333"))
    p.rect(40, y_table, 515, 25, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(150, y_table + 8, "SUBJECT")
    p.drawString(350, y_table + 8, "TOTAL MARKS")
    p.drawString(460, y_table + 8, "OBTAINED")

    y_row = y_table - 22
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)
    
    total_max = 0
    total_obt = 0
    for sub, marks in data['subjects'].items():
        p.rect(40, y_row, 515, 22)
        p.line(330, y_row, 330, y_row + 22)
        p.line(440, y_row, 440, y_row + 22)
        p.drawString(45, y_row + 7, sub)
        p.drawCentredString(385, y_row + 7, "50")
        p.drawCentredString(495, y_row + 7, str(marks))
        total_max += 50
        total_obt += marks
        y_row -= 22

    # Grand Total
    p.setFont("Helvetica-Bold", 10)
    p.rect(40, y_row, 515, 22)
    p.drawString(45, y_row + 7, "GRAND TOTAL")
    p.drawCentredString(385, y_row + 7, str(total_max))
    p.drawCentredString(495, y_row + 7, str(total_obt))

    # Summary Section
    y_summary = y_row - 40
    perc = (total_obt / total_max) * 100
    grade, perf = get_grade_info(perc)
    box_w = 515 / 4
    for i, label in enumerate(["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]):
        p.rect(40 + (i * box_w), y_summary, box_w, 30)
        p.setFont("Helvetica", 8)
        val = f"{perc:.1f}%" if i==0 else (data['position'] if i==1 else (perf if i==2 else grade))
        p.drawCentredString(40 + (i * box_w) + (box_w/2), y_summary + 18, f"{label}: {val}")

    # Quotes
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width/2, 200, '"Education is the most powerful weapon which you can use to change the world."')
    p.drawCentredString(width/2, 180, '"The roots of education are bitter, but the fruit is sweet."')

    # Signatures
    p.setFont("Helvetica-Bold", 9)
    p.line(100, 110, 230, 110)
    p.drawCentredString(165, 95, "CLASS TEACHER")
    p.line(width - 230, 110, width - 100, 110)
    p.drawCentredString(width - 165, 95, "SENIOR HEAD MASTER (SAFDAR JAVED)")
    p.setFont("Helvetica", 8)
    p.drawRightString(width - 40, 60, f"Result Declaration Date: {data['date']}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- Streamlit Interface ---
def main():
    st.title("GHS Bhutta Mohabbat - Result Card System")
    
    with st.sidebar:
        st.header("School Info")
        school = st.text_input("School Name", "Govt. High School Bhutta Mohabbat")
        emis = st.text_input("EMIS Code", "39310025")
        district = st.text_input("District", "Okara")
        session = st.text_input("Session", "2025-2026")

    st.subheader("Student Details")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Name", "Kharu")
    father = c2.text_input("Father's Name", "Danu")
    s_class = c3.text_input("Class", "8")
    
    c4, c5, c6 = st.columns(3)
    roll = c4.text_input("Roll No", "23")
    section = c5.text_input("Section", "A")
    pos = c6.text_input("Position", "---")

    st.subheader("Marks (Out of 50)")
    subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks = {}
    cols = st.columns(4)
    for i, s in enumerate(subs):
        marks[s] = cols[i % 4].number_input(s, 0, 50, 40)

    if st.button("Generate Result Card"):
        data = {
            "school_name": school, "emis": emis, "district": district, "session": session,
            "name": name, "father_name": father, "class": s_class, "roll": roll,
            "section": section, "subjects": marks, "position": pos,
            "date": "31-03-2026"
        }
        pdf = generate_pdf(data)
        st.download_button("Download PDF", pdf, f"Result_{name}.pdf", "application/pdf")

if __name__ == "__main__":
    main()
