import os
import io
import re
from fpdf import FPDF
from app.models.research import ResearchReport
from app.utils.logging import get_logger

logger = get_logger("export_service")


class PDFReport(FPDF):
    """Custom FPDF class with standard header and footer for research reports."""

    def __init__(self, title: str):
        super().__init__()
        self.report_title = title

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Deep Research AI - {self.report_title[:50]}", border=0, align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Verifiable Research Report", border=0, align="C")


class ExportService:
    """Service to export research reports into Markdown and PDF formats."""

    @staticmethod
    def generate_markdown_bytes(report: ResearchReport) -> bytes:
        """Converts report to Markdown bytes for download."""
        return report.full_markdown.encode("utf-8")

    @staticmethod
    def generate_pdf_bytes(report: ResearchReport) -> bytes:
        """Generates a styled, publication-ready PDF document from the report."""
        pdf = PDFReport(title=report.title)
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        width = pdf.epw  # Effective page width in FPDF2

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(20, 30, 55)
        pdf.multi_cell(width, 8, ExportService._clean_text_for_pdf(report.title))
        pdf.ln(5)

        # Executive Summary
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(width, 7, "Executive Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(width, 5, ExportService._clean_text_for_pdf(report.executive_summary))
        pdf.ln(5)

        # Key Findings
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(width, 7, "Key Findings", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        for kf in report.key_findings:
            pdf.multi_cell(width, 5, f"- {ExportService._clean_text_for_pdf(kf)}")
        pdf.ln(5)

        # Detailed Analysis
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(width, 7, "Detailed Analysis", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(width, 5, ExportService._clean_text_for_pdf(report.detailed_analysis))
        pdf.ln(5)

        # Conflicting Evidence & Limitations
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(width, 7, "Conflicting Evidence & Limitations", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(width, 5, ExportService._clean_text_for_pdf(report.conflicting_evidence_and_limitations))
        pdf.ln(5)

        # Conclusion
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(width, 7, "Conclusion", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(width, 5, ExportService._clean_text_for_pdf(report.conclusion))
        pdf.ln(5)

        # References
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(width, 7, "References & Cited Sources", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        for ref in report.references:
            date_str = f" ({ref.published_date})" if ref.published_date else ""
            ref_line = f"[{ref.id}] {ref.title} - {ref.domain}{date_str} - {ref.url}"
            pdf.multi_cell(width, 4, ExportService._clean_text_for_pdf(ref_line))
            pdf.ln(2)

        return bytes(pdf.output())

    @staticmethod
    def _clean_text_for_pdf(text: str) -> str:
        """Strips markdown headers/formatting and breaks long unbreakable strings for FPDF text rendering."""
        if not text:
            return ""
        # Strip markdown headers (##, ###) and bold (*, **)
        text = re.sub(r"#{1,6}\s*", "", text)
        text = re.sub(r"\*{1,2}", "", text)

        # Break any uninterrupted continuous token longer than 40 characters (e.g. long URLs) with space
        words = text.split(" ")
        cleaned_words = []
        for word in words:
            if len(word) > 40 and not "\n" in word:
                chunks = [word[i:i+35] for i in range(0, len(word), 35)]
                cleaned_words.append(" ".join(chunks))
            else:
                cleaned_words.append(word)
        text = " ".join(cleaned_words)

        # Replace non-latin1 characters for standard FPDF fonts
        text = text.encode("latin-1", "replace").decode("latin-1")
        return text
