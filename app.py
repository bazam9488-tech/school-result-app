import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import io
import datetime

# --- Page Config ---
st.set_page_config(page_title="GHS Bhutta Mohabbat - Advanced System", layout="wide")

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

    # Logo Handling
    if data['logo'] is not None:
        try:
            logo_img = Image.open(data['logo'])
            # Convert to RGB if needed
            if logo_img.mode in ("RGBA", "P"):
                logo_img = logo_img.convert("RGB")
            
            # Temporary save for ReportLab
            temp_logo = io.BytesIO()
            logo_img.save(temp_logo, format='JPEG')
            temp_logo.seek(0)
            
            p.drawInlineImage(temp_logo, 40, height - 100, width=60, height=60)
        except Exception as e:
            st.error(f"Logo error: {e}")

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

    # Student Info Bars
    p.setFillColor(colors.HexColor("#7B96AC"))
    p.rect(40, height - 155, 270, 20, fill=1, stroke=1)
    p.rect(310, height - 155, 245, 20, fill=1, stroke=1)
    p.rect(40, height - 175, 175, 20, fill=1, stroke=1)
    p.rect(215, height - 175, 175, 20, fill=1, stroke=1)
    p.rect(390, height - 175, 165, 20, fill=1, stroke=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(45, height - 148, f"NAME: {data['student_name'].upper()}")
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
    
    grand_total_max = 0
    grand_total_obt = 0
    
    for sub, info in data['marks_data'].items():
        p.rect(40, y_row, 515, 22)
        p.line(330, y_row, 330, y_row + 22)
        p.line(440, y_row, 440, y_row + 22)
        p.drawString(45, y_row + 7, sub)
        p.drawCentredString(385, y_row + 7, str(info['total']))
        p.drawCentredString(495, y_row + 7, str(info['obt']))
        
        grand_total_max += info['total']
        grand_total_obt += info['obt']
        y_row -= 22

    # Grand Total Row
    p.setFont("Helvetica-Bold", 10)
    p.rect(40, y_row, 515, 22)
    p.drawString(45, y_row + 7, "GRAND TOTAL")
    p.drawCentredString(385, y_row + 7, str(grand_total_max))
    p.drawCentredString(495, y_row + 7, str(grand_total_obt))

    # Summary Section
    y_summary = y_row - 40
    perc = (grand_total_obt / grand_total_max * 100) if grand_total_max > 0 else 0
    grade, perf = get_grade_info(perc)
    box_w = 515 / 4
    labels = ["PERCENTAGE", "POSITION", "PERFORMANCE", "FINAL GRADE"]
    values = [f"{perc:.1f}%", data['position'], perf, grade]
    
    for i in range(4):
        p.rect(40 + (i * box_w), y_summary, box_w, 30)
        p.setFont("Helvetica", 8)
        p.drawCentredString(40 + (i * box_w) + (box_w/2), y_summary + 18, f"{labels[i]}: {values[i]}")

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

# --- Streamlit UI ---
def main():
    st.title("GHS Bhutta Mohabbat - Result Generator")

    with st.sidebar:
        st.header("School Customization")
        school_name = st.text_input("School Name", "Govt. High School Bhutta Mohabbat")
        emis = st.text_input("EMIS Code", "39310025")
        district = st.text_input("District", "Okara")
        session = st.text_input("Session", "2025-2026")
        logo_file = st.file_uploader("Upload School Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

    # Student Info
    st.subheader("Student Personal Details")
    c1, c2, c3 = st.columns(3)
    s_name = c1.text_input("Student Name", "Kharu")
    f_name = c2.text_input("Father Name", "Danu")
    s_class = c3.text_input("Class", "8")
    
    c4, c5, c6 = st.columns(3)
    roll = c4.text_input("Roll No", "23")
    section = c5.text_input("Section", "A")
    pos = c6.text_input("Position", "---")

    # Subject and Marks Management
    st.subheader("Subject Selection & Marks Entry")
    default_subs = ["English", "Urdu", "Mathematics", "Islamiat", "Science", "Social Study", "Computer", "Tarjuma-tu-Quran"]
    
    final_marks_data = {}
    
    # Use columns for layout
    cols = st.columns(1) # We can list them one by one for clarity
    for sub in default_subs:
        col_check, col_total, col_obt = st.columns([1, 1, 1])
        is_selected = col_check.checkbox(f"Include {sub}", value=True)
        if is_selected:
            t_marks = col_total.number_input(f"Total Marks ({sub})", 1, 100, 50, key=f"t_{sub}")
            o_marks = col_obt.number_input(f"Obtained ({sub})", 0, t_marks, 40, key=f"o_{sub}")
            final_marks_data[sub] = {"total": t_marks, "obt": o_marks}

    if st.button("Generate Result PDF"):
        if not final_marks_data:
            st.warning("Please select at least one subject!")
        else:
            data = {
                "school_name": school_name, "emis": emis, "district": district, "session": session,
                "logo": logo_file, "student_name": s_name, "father_name": f_name,
                "class": s_class, "roll": roll, "section": section, "position": pos,
                "marks_data": final_marks_data, "date": "31-03-2026"
            }
            pdf_out = generate_pdf(data)
            st.success("PDF Ready!")
            st.download_button("📥 Download Result Card", pdf_out, f"Result_{s_name}.pdf", "application/pdf")

if __name__ == "__main__":
    main()
