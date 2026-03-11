from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm


# ==============================
# STUDENT DATA MODEL
# ==============================
class StudentData:
    def __init__(self):
        self.name = "Ali Khan"
        self.father = "Ahmed Khan"
        self.roll = "23"
        self.class_name = "8th"
        self.section = "A"
        self.session = "2025-2026"
        self.date = "10 March 2026"

        self.subjects = [
            ("English", 100, 85),
            ("Mathematics", 100, 92),
            ("Science", 100, 88),
            ("Urdu", 100, 81),
            ("Islamiat", 100, 90),
            ("Computer", 100, 95),
        ]


# ==============================
# REPORT CARD PDF CLASS
# ==============================
class ReportCardPDF:

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
        self.canvas = canvas.Canvas(filename, pagesize=A4)
        self.width, self.height = A4

    # --------------------------
    # BORDER
    # --------------------------
    def draw_border(self):
        c = self.canvas
        c.setLineWidth(2)
        c.rect(20, 20, self.width - 40, self.height - 40)

    # --------------------------
    # HEADER
    # --------------------------
    def draw_header(self):
        c = self.canvas

        # School title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(
            self.width / 2,
            self.height - 60,
            "SCHOOL REPORT CARD"
        )

        # Session below logo/title
        c.setFont("Helvetica-Bold", 10)
        c.drawString(
            40,
            self.height - 90,
            f"Session {self.data.session}"
        )

    # --------------------------
    # STUDENT INFO
    # --------------------------
    def draw_student_info(self):
        c = self.canvas
        c.setFont("Helvetica", 11)

        y = self.height - 130

        c.drawString(40, y, f"Student Name: {self.data.name}")
        c.drawString(300, y, f"Roll No: {self.data.roll}")

        y -= 20
        c.drawString(40, y, f"Father Name: {self.data.father}")
        c.drawString(
            300,
            y,
            f"Class: {self.data.class_name} - {self.data.section}"
        )

    # --------------------------
    # MARKS TABLE
    # --------------------------
    def draw_marks(self):
        c = self.canvas

        table_data = [["Subject", "Max Marks", "Obtained"]]

        total_max = 0
        total_obt = 0

        for sub, max_m, obt in self.data.subjects:
            table_data.append([sub, max_m, obt])
            total_max += max_m
            total_obt += obt

        table = Table(
            table_data,
            colWidths=[200, 120, 120]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))

        y_position = self.height - 320
        table.wrapOn(c, self.width, self.height)
        table.drawOn(c, 60, y_position)

        return total_max, total_obt, y_position

    # --------------------------
    # SUMMARY
    # --------------------------
    def draw_summary(self, total_max, total_obt, y):
        c = self.canvas

        percentage = (total_obt / total_max) * 100

        if percentage >= 80:
            grade = "A+"
        elif percentage >= 70:
            grade = "A"
        elif percentage >= 60:
            grade = "B"
        else:
            grade = "C"

        c.setFont("Helvetica-Bold", 12)

        y -= 40
        c.drawString(60, y, f"Total Marks: {total_obt} / {total_max}")
        y -= 20
        c.drawString(60, y, f"Percentage: {percentage:.2f}%")
        y -= 20
        c.drawString(60, y, f"Grade: {grade}")

        return y

    # --------------------------
    # REMARKS
    # --------------------------
    def draw_remarks(self, y):
        c = self.canvas

        c.setFont("Helvetica", 11)
        y -= 30

        c.drawString(60, y, "Teacher Remarks:")
        y -= 20

        c.setFont("Helvetica-Oblique", 11)
        c.drawString(
            60,
            y,
            "Excellent performance. Keep working hard!"
        )

    # --------------------------
    # EDUCATIONAL QUOTES
    # --------------------------
    def draw_quotes(self):
        c = self.canvas

        c.setFont("Helvetica-Oblique", 11)

        c.drawCentredString(
            self.width / 2,
            220,
            '"Education is the most powerful weapon which you can use to change the world."'
        )

        c.drawCentredString(
            self.width / 2,
            200,
            '"The beautiful thing about learning is that no one can take it away from you."'
        )

    # --------------------------
    # SIGNATURES
    # --------------------------
    def draw_signatures(self):
        c = self.canvas

        c.setFont("Helvetica-Bold", 10)

        # Class Teacher
        c.line(80, 110, 220, 110)
        c.drawCentredString(150, 95, "CLASS TEACHER")

        # Headmaster
        c.line(self.width - 240, 110, self.width - 40, 110)
        c.drawCentredString(
            self.width - 140,
            95,
            "SENIOR HEAD MASTER (SAFDAR JAVED)"
        )

        c.setFont("Helvetica", 9)
        c.drawRightString(
            self.width - 40,
            60,
            f"Result Declaration Date: {self.data.date}"
        )

    # --------------------------
    # FINALIZE
    # --------------------------
    def finalize(self):
        self.canvas.save()
        return self.filename

    # --------------------------
    # BUILD PDF
    # --------------------------
    def build(self):
        self.draw_border()
        self.draw_header()
        self.draw_student_info()

        total_max, total_obt, y = self.draw_marks()
        y_sum = self.draw_summary(total_max, total_obt, y)

        self.draw_remarks(y_sum)
        self.draw_quotes()
        self.draw_signatures()

        return self.finalize()


# ==============================
# RUN PROGRAM
# ==============================
if __name__ == "__main__":
    student = StudentData()
    pdf = ReportCardPDF("report_card.pdf", student)
    pdf.build()

    print("✅ Report Card Generated Successfully!")
