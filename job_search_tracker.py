from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

PAGE_W, PAGE_H = letter

ACCENT = colors.HexColor("#2F6FED")      # muted blue accent
TEXT = colors.HexColor("#111827")        # near-black
MUTED = colors.HexColor("#6B7280")       # gray labels
LINE = colors.HexColor("#E5E7EB")        # light dividers
CARD_BG = colors.white

def wrap_text(c, text, x, y, w, font_name="Helvetica", font_size=9, leading=12, max_lines=999):
    c.setFont(font_name, font_size)
    words = (text or "").split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if stringWidth(test, font_name, font_size) <= w:
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

    return y - (len(lines) - 1) * leading

def label_value(c, label, value, x, y, w, label_fs=7.5, value_fs=9):
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", label_fs)
    c.drawString(x, y, label.upper())
    c.setFillColor(TEXT)
    y2 = y - 12
    wrap_text(c, value or "", x, y2, w, font_name="Helvetica", font_size=value_fs, leading=12, max_lines=3)
    return y2 - 26

def draw_card(c, x, y_top, w, h, idx):
    r = 10
    # card background
    c.setFillColor(CARD_BG)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(x, y_top - h, w, h, r, stroke=1, fill=1)

    pad = 14
    x0 = x + pad
    y0 = y_top - pad

    # Header row
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x0, y0, f"Application #{idx}")

    # Thin divider
    c.setStrokeColor(LINE)
    c.line(x0, y0 - 10, x + w - pad, y0 - 10)

    # Content grid
    y = y0 - 26
    col_gap = 14
    col_w = (w - pad * 2 - col_gap) / 2

    # Top compact fields (two columns, two rows)
    y = label_value(c, "Status", "", x0, y, col_w)
    y_right = y0 - 26
    y_right = label_value(c, "Company", "", x0 + col_w + col_gap, y_right, col_w)

    y2 = y + 6
    y2 = label_value(c, "Job Title", "", x0, y2, col_w)
    y2_right = y_right + 6
    y2_right = label_value(c, "Date Applied", "", x0 + col_w + col_gap, y2_right, col_w)

    # Divider
    c.setStrokeColor(LINE)
    c.line(x0, y2 - 8, x + w - pad, y2 - 8)

    # Links / interviews row
    y3 = y2 - 24
    y3 = label_value(c, "Job Link (URL)", "", x0, y3, col_w)
    y3_right = y2 - 24
    y3_right = label_value(c, "Interview Dates", "", x0 + col_w + col_gap, y3_right, col_w)

    # Full-width fields
    y4 = min(y3, y3_right) - 10
    full_w = w - pad * 2

    c.setStrokeColor(LINE)
    c.line(x0, y4, x + w - pad, y4)
    y4 -= 18

    y4 = label_value(c, "Job Description", "", x0, y4, full_w)
    y4 = label_value(c, "Contact Person(s) + Contact Info", "", x0, y4, full_w)
    y4 = label_value(c, "Company Research Notes", "", x0, y4, full_w)

def main():
    out_path = "Job_Search_Tracker_Minimal_Portrait.pdf"
    c = canvas.Canvas(out_path, pagesize=letter)

    # Page title
    margin = 0.7 * inch
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, PAGE_H - margin, "Job Search Tracker")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(margin, PAGE_H - margin - 18, "Minimal portrait layout (cards). Fill by typing after exporting to a form tool, or print and write.")

    # Layout: 2 cards per page (clean + roomy). Increase to 3 if you want denser.
    card_w = PAGE_W - 2 * margin
    card_h = 3.4 * inch
    gap = 0.4 * inch

    y = PAGE_H - margin - 0.55 * inch
    idx = 1
    for _ in range(2):
        draw_card(c, margin, y, card_w, card_h, idx)
        idx += 1
        y -= (card_h + gap)

    c.showPage()

    # Second page with 2 more cards (optional; comment out if you want single-page)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, PAGE_H - margin, "Job Search Tracker (continued)")
    y = PAGE_H - margin - 0.55 * inch
    for _ in range(2):
        draw_card(c, margin, y, card_w, card_h, idx)
        idx += 1
        y -= (card_h + gap)

    c.save()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
