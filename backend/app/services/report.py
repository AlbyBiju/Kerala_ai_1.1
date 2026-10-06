"""Cross-platform PDF report rendering.

WeasyPrint requires native GTK/cairo libraries that are often unavailable
(especially on Windows). PyMuPDF's Story API renders HTML+CSS to PDF with
no external system dependencies, so it is the primary renderer here, with
WeasyPrint as a fallback when installed.
"""
import os

import pymupdf
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.shipment import ShipmentSession
from app.models.document import Document
from app.models.discrepancy import Discrepancy
from app.models.checklist_item import ChecklistItem

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_html_to_pdf(html_out: str) -> bytes:
    """Render an HTML report string to PDF bytes via PyMuPDF Story (cross-platform)."""
    import tempfile

    story = pymupdf.Story(html=html_out)
    mediabox = pymupdf.paper_rect("a4")

    def rectfn(rect_num: int, filled: bool):
        # Constant A4 page with 36pt margins on every page
        return mediabox, mediabox + (36, 36, -36, -36), pymupdf.Identity

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        writer = pymupdf.DocumentWriter(tmp_path)
        story.write(writer, rectfn)
        writer.close()
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


async def generate_report_content(shipment_id: str, db: AsyncSession) -> tuple[str, bytes]:
    """
    Renders report HTML and produces a real PDF.
    Returns: (html_content, pdf_bytes)
    """
    stmt = select(ShipmentSession).where(ShipmentSession.id == shipment_id)
    res = await db.execute(stmt)
    shipment = res.scalar_one_or_none()
    if not shipment:
        raise ValueError(f"Shipment {shipment_id} not found")

    docs = (await db.execute(select(Document).where(Document.shipment_id == shipment_id))).scalars().all()
    discs = (await db.execute(select(Discrepancy).where(Discrepancy.shipment_id == shipment_id))).scalars().all()
    checklist = (await db.execute(select(ChecklistItem).where(ChecklistItem.shipment_id == shipment_id))).scalars().all()

    template = jinja_env.get_template("report.html")
    html_out = template.render(
        shipment=shipment,
        documents=docs,
        discrepancies=discs,
        checklist_items=checklist,
    )

    # Primary: PyMuPDF Story (cross-platform, no system deps)
    try:
        return html_out, render_html_to_pdf(html_out)
    except Exception:
        pass

    # Fallback: WeasyPrint if installed (Linux/Docker images with cairo)
    try:
        from weasyprint import HTML

        return html_out, HTML(string=html_out).write_pdf()
    except Exception:
        # Last resort: HTML bytes (endpoint labels it as HTML via magic-byte check)
        return html_out, html_out.encode("utf-8")
