import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import io
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="PDF Result Card Generator", layout="centered")

def get_grade(percentage):
    """Enhanced grading scale."""
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B"
    elif percentage >= 60: return "C"
    elif percentage >= 50: return "D"
    else: return "F (Fail)"

def generate_pdf(data):
    """
    Generates a professional PDF result card.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 1. Page Border
    p.setStrokeColor(colors.black)
    p.rect(20, 20, width - 40, height - 40, stroke=1, fill=0)

    # 2. Header Section
    p.setFillColor(colors.HexColor("#1F497D")) # Professional Dark Blue
    p.rect(20, height - 120, width - 40, 100, fill=1)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2, height - 60, data['school_name'].upper())
    
    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 90, "ANNUAL PROGRESS REPORT - 2026")

    # 3. Student Information
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    
    curr_y = height - 160
    p.drawString(50, curr_y, f"Student Name: {data['name']}")
    p.drawString(350, curr_y, f"Class: {data['class']}")
    
    curr_y -= 25
    p.drawString(50, curr_y, f"Roll Number: {data['roll']}")
    p.drawString(350, curr_y, f"Date: {datetime.date.today().strftime('%B %d, %s')}")

    # 4. Marks Table
    table_data = [["Subject", "Maximum Marks", "Obtained Marks", "Grade"]]
    for sub, marks in data['subjects'].items():
        table_data.append([sub, "100", str(marks), get_grade(marks)])

    # Table Styling
    table = Table(table_data, colWidths=[200, 100, 100, 100])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D3D3D3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    # Calculate table position
    table_width, table_height = table.wrap(0, 0)
    table.drawOn(p, 50, curr_y - table_height - 30)

    # 5. Result Summary
    summary_y = curr_y - table_height - 80
    total_marks = sum(data['subjects'].values())
    max_total = len(data['subjects']) * 100
    percentage = (total_marks / max_total) * 100
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, summary_y, f"Total Marks: {total_marks} / {max_total}")
    p.drawString(50, summary_y - 20, f"Percentage: {percentage:.2f}%")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, summary_y - 45, f"Final Result: {'PASSED' if percentage >= 40 else 'FAILED'}")

    # 6. Teacher Comments Section
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, summary_y - 90, "Teacher's Remarks:")
    p.setFont("Helvetica-Oblique", 11)
    
    # Box for comments
    p.rect(50, summary_y - 160, width - 100, 60)
    p.drawString(60, summary_y - 110, data['comments'])

    # 7. Footer / Signatures
    # Bottom Left: Class Teacher
    p.line(50, 70, 200, 70)
    p.setFont("Helvetica", 10)
    p.drawString(75, 55, "Class Teacher")

    # Bottom Right: Senior Headmaster
    p.line(width - 200, 70, width - 50, 70)
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(width - 50, 55, "Safdar Javed")
    p.setFont("Helvetica", 9)
    p.drawRightString(width - 50, 42, "Senior Headmaster")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- STREAMLIT UI ---
def main():
    st.title("📄 PDF School Result Generator")
    st.info("Generates a formal A4 PDF report with automated grading and signatures.")

    with st.sidebar:
        st.header("School Details")
        school_name = st.text_input("School Name", "Government High School Bhutta Mohabbat")
        
        st.header("Subjects Configuration")
        subject_input = st.text_area("List Subjects (one per line)", 
                                     "English\nMathematics\nPhysics\nChemistry\nUrdu\nComputer Science")
        subjects = [s.strip() for s in subject_input.split('\n') if s.strip()]

    # Student Data Input
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Student Name", placeholder="e.g. Ali Ahmed")
        roll = st.text_input("Roll Number", placeholder="e.g. 1025")
    with col2:
        student_class = st.text_input("Class", placeholder="e.g. 10th-A")
        
    st.subheader("Marks Entry")
    marks_data = {}
    m_cols = st.columns(3)
    for i, sub in enumerate(subjects):
        with m_cols[i % 3]:
            marks_data[sub] = st.number_input(f"{sub}", 0, 100, 50, key=sub)

    comments = st.text_area("Teacher's Remarks", "Excellent performance and hard-working student.")

    if st.button("Generate & Preview PDF", type="primary"):
        if not name or not roll:
            st.warning("Please fill in the Student Name and Roll Number.")
        else:
            data_payload = {
                "school_name": school_name,
                "name": name,
                "roll": roll,
                "class": student_class,
                "subjects": marks_data,
                "comments": comments
            }
            
            pdf_bytes = generate_pdf(data_payload)
            
            # Download Button
            st.success("PDF Generated Successfully!")
            st.download_button(
                label="📥 Download Result Card (PDF)",
                data=pdf_bytes,
                file_name=f"Result_{name}_{roll}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
