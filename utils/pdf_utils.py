from datetime import datetime


from fpdf import FPDF


# ==========================================================
# Custom PDF Class
# ==========================================================

class AskoraPDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 16)

        self.cell(
            0,
            10,
            "Askora - AI Doubt Notebook",
            ln=True,
            align="C"
        )

        self.ln(3)

    def footer(self):
        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "I",
            8
        )

        self.cell(
            0,
            10,
            f"Page {self.page_no()}",
            align="C"
        )


# ==========================================================
# Safe Multi Cell Writer
# ==========================================================

def add_section(
    pdf,
    title,
    content
):
    """
    Add notebook section safely.
    """

    if not content:
        content = "N/A"

    pdf.set_font(
        "Helvetica",
        "B",
        12
    )

    pdf.cell(
        0,
        8,
        title,
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    pdf.multi_cell(
        0,
        7,
        str(content)
    )

    pdf.ln(2)


# ==========================================================
# Single Notebook Entry
# ==========================================================

def add_notebook_entry(
    pdf,
    entry,
    index
):
    """
    Add one notebook record.
    """

    pdf.set_font(
        "Helvetica",
        "B",
        13
    )

    pdf.cell(
        0,
        10,
        f"Doubt #{index}",
        ln=True
    )

    pdf.line(
        10,
        pdf.get_y(),
        200,
        pdf.get_y()
    )

    pdf.ln(4)

    add_section(
        pdf,
        "Subject",
        entry.get(
            "subject",
            ""
        )
    )

    add_section(
        pdf,
        "Difficulty",
        entry.get(
            "difficulty",
            ""
        )
    )

    add_section(
        pdf,
        "Question",
        entry.get(
            "question",
            ""
        )
    )

    add_section(
        pdf,
        "Explanation",
        entry.get(
            "explanation",
            ""
        )
    )

    add_section(
        pdf,
        "Practice Problem",
        entry.get(
            "practice_problem",
            ""
        )
    )

    add_section(
        pdf,
        "Quiz Score",
        entry.get(
            "quiz_score",
            ""
        )
    )

    add_section(
        pdf,
        "Timestamp",
        entry.get(
            "timestamp",
            ""
        )
    )

    pdf.ln(8)


# ==========================================================
# Create PDF Bytes
# ==========================================================

def generate_notebook_pdf(
    notebook_entries
):
    """
    Generate PDF in memory.

    Returns:
        bytes
    """

    pdf = AskoraPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # Cover Info

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    pdf.cell(
        0,
        8,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ln=True
    )

    pdf.cell(
        0,
        8,
        f"Total Doubts: {len(notebook_entries)}",
        ln=True
    )

    pdf.ln(10)

    if not notebook_entries:

        pdf.set_font(
            "Helvetica",
            "I",
            11
        )

        pdf.cell(
            0,
            10,
            "No notebook entries available.",
            ln=True
        )

    else:

        for idx, entry in enumerate(
            notebook_entries,
            start=1
        ):

            add_notebook_entry(
                pdf,
                entry,
                idx
            )

            if idx != len(
                notebook_entries
            ):
                pdf.add_page()

    # Convert to bytes

    pdf_output = pdf.output(dest="S")

    if isinstance(pdf_output, str):
        pdf_output = pdf_output.encode("latin-1")

    return bytes(pdf_output)


# ==========================================================
# Download Filename
# ==========================================================

def get_pdf_filename():
    """
    Standard filename.
    """

    return "Askora_Doubt_Notebook.pdf"


# ==========================================================
# Notebook Summary
# ==========================================================

def get_notebook_summary(
    notebook_entries
):
    """
    Optional analytics
    for dashboard cards.
    """

    total = len(notebook_entries)

    if total == 0:

        return {
            "total_doubts": 0,
            "avg_score": "0/0"
        }

    scores = []

    for entry in notebook_entries:

        score_text = entry.get(
            "quiz_score",
            "0/0"
        )

        try:

            score, total_q = score_text.split(
                "/"
            )

            scores.append(
                (
                    int(score),
                    int(total_q)
                )
            )

        except Exception:
            continue

    if not scores:

        avg_score = "0/0"

    else:

        total_correct = sum(
            s[0]
            for s in scores
        )

        total_questions = sum(
            s[1]
            for s in scores
        )

        avg_score = (
            f"{total_correct}/"
            f"{total_questions}"
        )

    return {
        "total_doubts": total,
        "avg_score": avg_score
    }