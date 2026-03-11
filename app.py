import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import io

# --- Page Config ---
st.set_page_config(page_title="GHS Bhutta Mohabbat Result System", layout="wide")

# --- Grade Calculation ---
def get_grade_info(percentage):
    if percentage >= 80: return "A+", "Excellent"
    elif percentage >= 70: return "A", "Very Good"
    elif percentage >= 60: return "B", "Good"
    elif percentage >= 50: return "C", "Satisfactory"
    elif percentage >= 40: return "D", "Fair"
    else: return "F", "Poor"

# --- PDF Generator ---
def generate_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Borders
    p.setStrokeColor(colors.HexColor("#7B96AC"))
    p.setLineWidth(2)
    p.rect(15, 15, width - 30, height - 30)
    p.setLineWidth(1)
    p.rect(20, 20, width - 40, height - 40)

    # Header
    p.setFont("Helvetica", 9)
    p.drawCentredString(width / 2 + 30, height - 45, "SCHOOL EDUCATION DEPARTMENT")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2 + 30, height - 62, data['school_name'].upper())
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width / 2 + 30, height - 75, f"EMIS CODE: {data['emis']} | DISTRICT {data['district'].upper()}")
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor("#7B96AC"))
    p.drawCentredString(width / 2, height - 115, "STUDENT REPORT CARD")

    # Logo
    if data['logo']:
        try:
            logo_reader = ImageReader(data['logo'])
            p.drawImage(logo_reader, 45, height - 105, width=65, height=65, mask='auto')
        except:
            pass

    # Session below logo
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(40, height - 130, f"Session {data['session']}")

    # Student Info
    info_data = [
        [f"NAME: {data['student_name'].upper()}", f"FATHER NAME: {data['father_name'].upper()}"],
        [f"CLASS: {data['class']}", f"ROLL NO: {data['roll']}", f"SECTION: {data['section']}"]
    ]
    t1 = Table(info_data[:1], colWidths=[275, 240])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7B96AC")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    t2 = Table(info_data[1:], colWidths=[175, 175, 165])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7B96AC")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    t1.wrapOn(p, 40, height - 160)
    t1.drawOn(p, 40, height - 160)
    t2.wrapOn(p, 40, height - 180)
    t2.drawOn(p, 40, height - 180)

    # Marks Table
    y_table = height - 215
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
    grand_total_max, grand_total_obt = 0, 0
    for sub, info in data['marks_data'].items():
        p.rect(40, y_row, 515, 22)
        p.line(330, y_row, 330, y_row + 22); p.line(440, y_row, 440, y_row + 22)
        p.drawString(45, y_row + 7, sub)
        p.drawCentredString(385, y_row + 7, str(info['total']))
        p.drawCentredString(495, y_row + 7, str(info['obt']))
        grand_total_max += info['total']; grand_total_obt += info['obt']
        y_row -= 22

    # Grand Total
    p.setFont("Helvetica-Bold", 10)
    p.rect(40, y_row, 515, 22)
    p.drawString(45, y_row + 7, "GRAND TOTAL")
    p.drawCentredString(385, y_row + 7, str(grand_total_max))
    p.drawCentredString(495, y_row + 7, str(grand_total_obt))

    # Result Summary
    y_summary = y_row - 40
    perc = (grand_total_obt / grand_total_max * 100) if grand_total_max > 0 else 0
    grade, perf = get_grade_info(perc)
    box_w = 515 / 4
    for i, label in enumerate(["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]):
        val = [f"{perc:.1f}%", data['position'], perf, grade][i]
        p.rect(40 + (i * box_w), y_summary, box_w, 30)
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(40 + (i * box_w) + (box_w/2), y_summary + 18, f"{label}: {val}")

    # Educational Quotes
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(width/2, 160, '"Education is the most powerful weapon which you can use to change the world."')
    p.drawCentredString(width/2, 140, '"The beautiful thing about learning is that no one can take it away from you."')

    # Signatures
    p.setFont("Helvetica-Bold", 9)
    p.line(80, 110, 210, 110); p.drawCentredString(145, 95, "CLASS TEACHER")
    p.line(width - 240, 110, width - 40, 110); p.drawCentredString(width - 140, 95, "SENIOR HEAD MASTER (SAFDAR JAVED)")
    p.setFont("Helvetica", 8); p.drawRightString(width - 40, 60, f"Result Declaration Date: {data['date']}")

    p.showPage(); p.save()
    buffer.seek(0)
    return buffer

# --- Streamlit App ---
def main():
    st.title("GHS Bhutta Mohabbat - Result Card Generator")

    with st.sidebar:
        st.header("Setup")
        school = st.text_input("School Name", "Govt. High School Bhutta Mohabbat")
        emis = st.text_input("EMIS Code", "39310025")
        dist = st.text_input("District", "Okara")
        sess = st.text_input("Session", "2025-2026")
        logo = st.file_uploader("Upload Logo", type=["jpg","png","jpeg"])

    st.subheader("Student Details")
    col1, col2, col3 = st.columns(3)
    s_name = col1.text_input("Student Name", "Faiz")
    f_name = col2.text_input("Father Name", "Sarwar")
    s_class = col3.text_input("Class", "9")
    roll = col1.text_input("Roll No", "12")
    sec = col2.text_input("Section", "A")
    pos = col3.text_input("Position", "---")
    perf = col3.text_input("Performance", "Good")  # Editable performance

    st.subheader("Marks & Subjects")
    subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    marks_data = {}
    for s in subs:
        c1, c2, c3 = st.columns([1,1,1])
        if c1.checkbox(f"Include {s}", value=True):
            t = c2.number_input(f"Total ({s})", 1, 100, 50, key=f"t{s}")
            o = c3.number_input(f"Obtained ({s})", 0, t, 40, key=f"o{s}")
            marks_data[s] = {"total": t, "obt": o}

    if st.button("Generate & Download PDF"):
        if not marks_data:
            st.error("Select at least one subject.")
        else:
            data = {
                "school_name": school, "emis": emis, "district": dist, "session": sess, "logo": logo,
                "student_name": s_name, "father_name": f_name, "class": s_class, "roll": roll, "section": sec,
                "position": pos, "marks_data": marks_data, "date": "31-03-2026"
            }
            pdf_bytes = generate_pdf(data)
            st.download_button("Download PDF", pdf_bytes, f"Result_{s_name}.pdf", "application/pdf")

if __name__ == "__main__":
    main()
