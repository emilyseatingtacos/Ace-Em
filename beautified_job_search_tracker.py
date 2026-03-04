from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = LETTER

# Minimal palette
ACCENT = colors.HexColor("#2563EB")   # calm blue
TEXT = colors.HexColor("#111827")     # near-black
MUTED = colors.HexColor("#6B7280")    # gray labels
LINE = colors.HexColor("#E5E7EB")     # light dividers
BG = colors.white


def wrap_text(c, text, x, y, w, font="Helvetica", size=9, leading=12, max_lines=6):
    c.setFont(font, size)
    words = (text or "").split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if stringWidth(test, font, size) <= w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)

    lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * leading, ln)
    return y - (len(lines) * leading)


def field_block(c, label, x, y, w, h):
    # label
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x, y + h - 10, label.upper())

    # input line/area
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h - 16, 8, stroke=1, fill=0)


def draw_card(c, x, y_top, w, h, idx):
    r = 12
    c.setFillColor(BG)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(x, y_top - h, w, h, r, stroke=1, fill=1)

    pad = 14
    x0 = x + pad
    y0 = y_top - pad

    # Card header
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x0, y0, f"Application {idx}")

    # subtle accent dot
    c.setFillColor(ACCENT)
    c.circle(x + w - pad - 6, y0 + 3, 3, stroke=0, fill=1)

    # divider
    c.setStrokeColor(LINE)
    c.line(x0, y0 - 10, x + w - pad, y0 - 10)

    y = y0 - 28
    col_gap = 12
    col_w = (w - 2 * pad - col_gap) / 2

    # Row 1 (compact)
    field_block(c, "Status", x0, y - 34, col_w, 46)
    field_block(c, "Company", x0 + col_w + col_gap, y - 34, col_w, 46)

    # Row 2 (compact)
    y2 = y - 60
    field_block(c, "Job Title", x0, y2 - 34, col_w, 46)
    field_block(c, "Date Applied", x0 + col_w + col_gap, y2 - 34, col_w, 46)

    # Row 3
    y3 = y2 - 60
    field_block(c, "Job Link (URL)", x0, y3 - 34, col_w, 46)
    field_block(c, "Interview Dates", x0 + col_w + col_gap, y3 - 34, col_w, 46)

    # Full-width areas
    full_w = w - 2 * pad

    y4 = y3 - 80
    field_block(c, "Job Description", x0, y4 - 70, full_w, 90)

    y5 = y4 - 102
    field_block(c, "Contact Person(s) + Contact Info", x0, y5 - 54, full_w, 74)

    y6 = y5 - 88
    field_block(c, "Company Research Notes", x0, y6 - 78, full_w, 98)


def make_pdf(out_path="Beautified_Job_Search_Tracker_Portrait.pdf", cards_per_page=2, pages=2):
    c = canvas.Canvas(out_path, pagesize=LETTER)

    margin = 0.7 * inch
    title_y = PAGE_H - margin

    for p in range(pages):
        # Title
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, title_y, "Job Search Tracker")

        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(margin, title_y - 18, "Minimal portrait layout (application cards)")

        # Cards layout
        card_w = PAGE_W - 2 * margin
        available_h = PAGE_H - (margin + 0.9 * inch) - margin  # space under title to bottom margin
        gap = 0.35 * inch
        card_h = (available_h - gap * (cards_per_page - 1)) / cards_per_page

        y = PAGE_H - (margin + 0.9 * inch)
        base_idx = p * cards_per_page + 1

        for i in range(cards_per_page):
            draw_card(c, margin, y, card_w, card_h, base_idx + i)
            y -= card_h + gap

        c.showPage()

    c.save()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    make_pdf(
        out_path="Beautified_Job_Search_Tracker_Portrait.pdf",
        cards_per_page=2,  # change to 3 if you want denser pages
        pages=2,  # change to 1 if you only want one page
    )
