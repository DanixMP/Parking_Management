from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

def generate_daily_report_pdf(date_str, summary: dict, entries_df, exits_df, out_path: str):
    """
    summary شامل کلیدهای زیر باشد:
      total_entries, total_exits, active_end, total_revenue, avg_duration
    entries_df و exits_df هم DataFrame های همان روز هستند.
    """
    c = canvas.Canvas(out_path, pagesize=A4)
    w, h = A4

    y = h - 25 * mm

    # عنوان
    c.setFont("Helvetica-Bold", 16)
    c.drawString(25 * mm, y, f"Parking Daily Report - {date_str}")
    y -= 15 * mm

    # خلاصه آماری
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, y, "Summary:")
    y -= 8 * mm

    c.setFont("Helvetica", 11)
    lines = [
        f"Total entries: {summary.get('total_entries', 0)}",
        f"Total exits: {summary.get('total_exits', 0)}",
        f"Active cars at end of day: {summary.get('active_end', 0)}",
        f"Total revenue (Toman): {summary.get('total_revenue', 0)}",
        f"Average duration (min): {summary.get('avg_duration', 0):.1f}",
    ]
    for line in lines:
        c.drawString(30 * mm, y, line)
        y -= 6 * mm

    y -= 8 * mm

    # چند پلاک نمونه ورود
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, y, "Sample entries:")
    y -= 8 * mm

    c.setFont("Helvetica", 10)
    if entries_df is not None and not entries_df.empty:
        for _, row in entries_df.head(10).iterrows():
            c.drawString(
                30 * mm,
                y,
                f"{row['plate']}  -  in: {row['timestamp_in']}",
            )
            y -= 5 * mm
            if y < 30 * mm:
                c.showPage()
                y = h - 25 * mm
    else:
        c.drawString(30 * mm, y, "No entries.")
        y -= 5 * mm

    y -= 8 * mm

    # چند پلاک نمونه خروج
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, y, "Sample exits:")
    y -= 8 * mm

    c.setFont("Helvetica", 10)
    if exits_df is not None and not exits_df.empty:
        for _, row in exits_df.head(10).iterrows():
            c.drawString(
                30 * mm,
                y,
                f"{row['plate']}  -  out: {row['timestamp_out']}  -  dur: {row['duration_minutes']} min  -  cost: {row['cost']}",
            )
            y -= 5 * mm
            if y < 30 * mm:
                c.showPage()
                y = h - 25 * mm
    else:
        c.drawString(30 * mm, y, "No exits.")
        y -= 5 * mm

    c.showPage()
    c.save()