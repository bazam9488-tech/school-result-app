import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="GHS Bhutta Mohabbat Result System",
    layout="wide",
)

SUBJECTS = [
    "English",
    "Urdu",
    "Mathematics",
    "Islamiat",
    "Science",
    "Social Study",
    "Computer",
    "Tarjuma-tu-Quran",
]

# ---------------- DATA MODEL ----------------

@dataclass
class StudentData:
    school_name: str
    emis: str
    district: str
    session: str
    logo: Optional[bytes]
    student_name: str
    father_name: str
    student_class: str
    roll: str
    section: str
    position: str
    performance: str
    remarks: str
    marks_data: Dict[str, Dict[str, int]]
    date: str


# ---------------- BUSINESS LOGIC ----------------

def get_grade_info(percentage: float) -> Tuple[str, str]:
    if percentage >= 80:
        return "A+", "Excellent"
    if percentage >= 70:
        return "A", "Very Good"
    if percentage >= 60:
        return "B", "Good"
    if percentage >= 50:
        return "C", "Satisfactory"
    if percentage >= 40:
        return "D", "Fair"
    return "F", "Poor"


# ---------------- PDF BUILDER ----------------

class ReportCardPDF:

    def __init__(self, data: StudentData):
        self.data = data
        self.buffer = io.BytesIO()
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)
        self.width, self.height = A4

    def draw_border(self):
        c = self.canvas
        c.setStrokeColor(colors.HexColor("#7B96AC"))
        c.setLineWidth(2)
        c.rect(15, 15, self.width - 30, self.height - 30)
        c.setLineWidth(1)
        c.rect(20, 20, self.width - 40, self.height - 40)

    def draw_header(self):
        c = self.canvas
        d = self.data

        c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2 + 30, self.height - 45,
                            "SCHOOL EDUCATION DEPARTMENT")

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(self.width / 2 + 30,
                            self.height - 62,
                            d.school_name.upper())

        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(
            self.width / 2 + 30,
            self.height - 75,
            f"EMIS CODE: {d.emis} | DISTRICT {d.district.upper()}",
        )

        c.setFillColor(colors.HexColor("#7B96AC"))
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2,
                            self.height - 115,
                            "STUDENT REPORT CARD")

        self._draw_logo()

    def _draw_logo(self):
        if not self.data.logo:
            return
        try:
            img = Image.open(self.data.logo)
            reader = ImageReader(img)
            self.canvas.drawImage(
                reader, 45, self.height - 105,
                width=65, height=65, mask="auto"
            )
        except Exception:
            pass

    def draw_student_info(self):
        c = self.canvas
        d = self.data

        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#7B96AC")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ])

        t1 = Table([[f"NAME: {d.student_name.upper()}",
                     f"FATHER NAME: {d.father_name.upper()}"]],
                   colWidths=[275, 240])
        t1.setStyle(style)
        t1.wrapOn(c, 40, self.height - 160)
        t1.drawOn(c, 40, self.height - 160)

        t2 = Table([[f"CLASS: {d.student_class}",
                     f"ROLL NO: {d.roll}",
                     f"SECTION: {d.section}"]],
                   colWidths=[175, 175, 165])
        t2.setStyle(style)
        t2.wrapOn(c, 40, self.height - 180)
        t2.drawOn(c, 40, self.height - 180)

    def draw_marks(self):
        c = self.canvas

        y_table = self.height - 215
        c.setFillColor(colors.HexColor("#333333"))
        c.rect(40, y_table, 515, 25, fill=1)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(150, y_table + 8, "SUBJECT")
        c.drawString(350, y_table + 8, "TOTAL MARKS")
        c.drawString(460, y_table + 8, "OBTAINED")

        y_row = y_table - 22
        total_max = total_obt = 0

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)

        for sub, info in self.data.marks_data.items():
            c.rect(40, y_row, 515, 22)
            c.line(330, y_row, 330, y_row + 22)
            c.line(440, y_row, 440, y_row + 22)

            c.drawString(45, y_row + 7, sub)
            c.drawCentredString(385, y_row + 7, str(info["total"]))
            c.drawCentredString(495, y_row + 7, str(info["obt"]))

            total_max += info["total"]
            total_obt += info["obt"]
            y_row -= 22

        return total_max, total_obt, y_row

    def draw_summary(self, total_max, total_obt, y_row):
        c = self.canvas

        percentage = (total_obt / total_max * 100) if total_max else 0
        grade, _ = get_grade_info(percentage)

        values = [
            f"{percentage:.1f}%",
            self.data.position,
            self.data.performance,
            grade,
        ]

        labels = ["PERCENTAGE", "POSITION",
                  "PERFORMANCE", "FINAL GRADE"]

        box_w = 515 / 4
        y_summary = y_row - 40

        for i, label in enumerate(labels):
            c.rect(40 + i * box_w, y_summary, box_w, 30)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(
                40 + i * box_w + box_w / 2,
                y_summary + 18,
                f"{label}: {values[i]}",
            )

        return y_summary

    def draw_remarks(self, y_position):
        c = self.canvas

        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y_position - 30, "TEACHER REMARKS")

        c.rect(40, y_position - 80, 515, 45)

        text_obj = c.beginText(45, y_position - 60)
        text_obj.setFont("Helvetica", 9)
        text_obj.textLines(self.data.remarks)
        c.drawText(text_obj)

    def finalize(self):
        self.canvas.showPage()
        self.canvas.save()
        self.buffer.seek(0)
        return self.buffer

    def build(self):
        self.draw_border()
        self.draw_header()
        self.draw_student_info()
        total_max, total_obt, y = self.draw_marks()
        y_sum = self.draw_summary(total_max, total_obt, y)
        self.draw_remarks(y_sum)
        return self.finalize()


# ---------------- STREAMLIT UI ----------------

def main():

    st.title("GHS Bhutta Mohabbat - Result Card Generator")

    with st.sidebar:
        st.header("Setup")
        school = st.text_input("School Name",
                               "Govt. High School Bhutta Mohabbat")
        emis = st.text_input("EMIS Code", "39310025")
        dist = st.text_input("District", "Okara")
        sess = st.text_input("Session", "2025-2026")
        logo = st.file_uploader("Upload Logo", ["png", "jpg", "jpeg"])

    st.subheader("Student Details")

    col1, col2, col3 = st.columns(3)
    s_name = col1.text_input("Student Name")
    f_name = col2.text_input("Father Name")
    s_class = col3.text_input("Class")
    roll = col1.text_input("Roll No")
    sec = col2.text_input("Section")
    pos = col3.text_input("Position")

    st.subheader("Performance & Remarks")

    performance_options = [
        "Excellent",
        "Very Good",
        "Good",
        "Satisfactory",
        "Needs Improvement",
        "Custom",
    ]

    perf_choice = st.selectbox("Performance Indicator",
                               performance_options)

    if perf_choice == "Custom":
        performance = st.text_input("Write Custom Performance")
    else:
        performance = perf_choice

    remarks = st.text_area(
        "Teacher Remarks",
        "Shows good learning attitude and participation.",
        height=120,
    )

    st.subheader("Marks")

    marks_data = {}

    for sub in SUBJECTS:
        c1, c2, c3 = st.columns([1, 1, 1])
        if c1.checkbox(sub, value=True):
            total = c2.number_input(f"Total {sub}", 1, 100, 50, key=f"t{sub}")
            obt = c3.number_input(f"Obtained {sub}", 0, total, 40, key=f"o{sub}")
            marks_data[sub] = {"total": total, "obt": obt}

    if st.button("Generate & Download PDF"):

        if not marks_data:
            st.error("Select at least one subject.")
            return

        data = StudentData(
            school, emis, dist, sess, logo,
            s_name, f_name, s_class,
            roll, sec, pos,
            performance,
            remarks,
            marks_data,
            "31-03-2026",
        )

        pdf = ReportCardPDF(data).build()

        st.download_button(
            "Download PDF",
            pdf,
            f"Result_{s_name}.pdf",
            "application/pdf",
        )


if __name__ == "__main__":
    main()
