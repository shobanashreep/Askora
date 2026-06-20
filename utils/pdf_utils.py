from fpdf import FPDF


class DoubtNotebookPDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "My Doubt Notebook", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def create_pdf_from_chat(chat_history):

    pdf = DoubtNotebookPDF()
    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    for message in chat_history:

        role = "Student" if message["role"] == "user" else "AI Tutor"

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{role}:", ln=True)

        pdf.set_font("Arial", "", 11)

        if message["type"] == "image":
            pdf.multi_cell(0, 8, "[Image Uploaded]")
        else:

            content = str(message["content"])

            content = (
                content.replace("###", "")
                .replace("**", "")
                .replace("*", "")
            )

            safe_content = (
                content.encode("latin-1", "replace")
                .decode("latin-1")
            )

            pdf.multi_cell(0, 8, safe_content)

        pdf.ln(3)

    return bytes(pdf.output(dest="S"))