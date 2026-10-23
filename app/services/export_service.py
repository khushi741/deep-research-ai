import os
import io
import re
from datetime import datetime
from fpdf import FPDF
from app.models.research import ResearchReport
from app.utils.logging import get_logger

logger = get_logger("export_service")


class ModernResearchPDF(FPDF):
    """
    Publication-grade Executive Research Report PDF generator.
    Implements corporate whitepaper typography, tinted callout boxes,
    styled section dividers, and clickable reference link cards.
    """

    def __init__(self, title: str, verification_badge: str = "Partial Evidence"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = title
        self.badge = verification_badge.upper()
        self.generated_date = datetime.now().strftime("%B %d, %Y")
        self.set_margins(left=18, top=18, right=18)

    def header(self):
        # Only render running header on page 2 and onwards
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(100, 116, 139)  # Slate 500
            clean_title = ExportService._clean_text_for_pdf(self.report_title)
            if len(clean_title) > 65:
                clean_title = clean_title[:62] + "..."
            self.cell(0, 6, f"DEEP RESEARCH AI  |  {clean_title.upper()}", border=0, align="L")
            self.set_font("Helvetica", "", 8)
            self.cell(0, 6, f"{self.generated_date} | {self.badge}", border=0, align="R")
            self.ln(7)

            # Subtle accent divider rule under header
            self.set_draw_color(226, 232, 240)  # Slate 200
            self.set_line_width(0.3)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

        self.set_font("Helvetica", "", 8)
        self.set_text_color(148, 163, 184)  # Slate 400
        self.cell(0, 8, f"AUTONOMOUS RESEARCH REPORT [{self.badge}]  -  DEEP RESEARCH AI", border=0, align="L")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", border=0, align="R")


class ExportService:
    """Service to export research reports into Markdown and professional publication-ready PDF formats."""

    @staticmethod
    def generate_markdown_bytes(report: ResearchReport) -> bytes:
        """Converts report to Markdown bytes for download."""
        return report.full_markdown.encode("utf-8")

    @staticmethod
    def generate_pdf_bytes(report: ResearchReport) -> bytes:
        """Generates a styled, publication-ready whitepaper PDF document from the report."""
        badge = getattr(report, "verification_badge", "Partial Evidence") or "Partial Evidence"
        pdf = ModernResearchPDF(title=report.title, verification_badge=badge)
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=18)

        width = pdf.epw  # Effective page width (approx 174mm on A4)

        # -------------------------------------------------------------
        # TOP BRAND BANNER (Page 1)
        # -------------------------------------------------------------
        pdf.set_fill_color(15, 23, 42)  # Dark Navy #0F172A
        pdf.rect(pdf.l_margin, pdf.get_y(), width, 10, style="F")

        pdf.set_xy(pdf.l_margin + 4, pdf.get_y() + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(52, 211, 153)  # Mint Green Accent
        pdf.cell(80, 6, "DEEP RESEARCH AI  *  AUTONOMOUS AGENT INTELLIGENCE", align="L")

        pdf.set_xy(pdf.w - pdf.r_margin - 85, pdf.get_y())
        pdf.set_font("Helvetica", "B", 8)
        
        # Color-coded badge
        if badge.upper() == "VERIFIED":
            pdf.set_text_color(52, 211, 153)  # Mint green
        elif "PARTIAL" in badge.upper():
            pdf.set_text_color(251, 191, 36)  # Amber
        else:
            pdf.set_text_color(248, 113, 113)  # Coral red

        pdf.cell(80, 6, f"DATE: {pdf.generated_date}  |  STATUS: {badge.upper()}", align="R")

        pdf.set_y(pdf.get_y() + 14)

        # -------------------------------------------------------------
        # REPORT TITLE BLOCK
        # -------------------------------------------------------------
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(15, 23, 42)  # Dark Slate
        clean_title = ExportService._clean_text_for_pdf(report.title)
        pdf.multi_cell(width, 7.5, clean_title, align="L")
        pdf.ln(3)

        # Decorative Emerald Horizontal Accent Line
        pdf.set_draw_color(16, 185, 129)  # Emerald 500
        pdf.set_line_width(1.0)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 45, pdf.get_y())
        pdf.ln(5)

        # -------------------------------------------------------------
        # METADATA PILL ROW (Sources Count, Claims, Status)
        # -------------------------------------------------------------
        sources_count = len(report.references) if report.references else 0
        findings_count = len(report.key_findings) if report.key_findings else 0

        pdf.set_fill_color(241, 245, 249)  # Slate 100
        pdf.set_draw_color(203, 213, 225)  # Slate 300
        pdf.set_line_width(0.2)

        pill_width = (width - 6) / 3
        curr_y = pdf.get_y()

        # Pill 1: Sources
        pdf.rect(pdf.l_margin, curr_y, pill_width, 10, style="FD")
        pdf.set_xy(pdf.l_margin, curr_y + 1.5)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(pill_width, 4, f"{sources_count} Web Sources Evaluated", align="C")
        pdf.set_xy(pdf.l_margin, curr_y + 5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(pill_width, 4, "Real-time Multi-vector Search", align="C")

        # Pill 2: Findings
        pdf.rect(pdf.l_margin + pill_width + 3, curr_y, pill_width, 10, style="FD")
        pdf.set_xy(pdf.l_margin + pill_width + 3, curr_y + 1.5)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(pill_width, 4, f"{findings_count} Key Synthesized Claims", align="C")
        pdf.set_xy(pdf.l_margin + pill_width + 3, curr_y + 5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(pill_width, 4, "Verifiable Citation Mapping", align="C")

        # Pill 3: Model
        pdf.rect(pdf.l_margin + (pill_width * 2) + 6, curr_y, pill_width, 10, style="FD")
        pdf.set_xy(pdf.l_margin + (pill_width * 2) + 6, curr_y + 1.5)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(5, 150, 105)  # Emerald 600
        pdf.cell(pill_width, 4, "Google Gemini 3.8 Flash", align="C")
        pdf.set_xy(pdf.l_margin + (pill_width * 2) + 6, curr_y + 5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(pill_width, 4, "Autonomous Reasoning Engine", align="C")

        pdf.set_y(curr_y + 15)

        # -------------------------------------------------------------
        # 1. EXECUTIVE SUMMARY CALLOUT BOX
        # -------------------------------------------------------------
        ExportService._render_section_heading(pdf, "Executive Summary", width)

        exec_text = ExportService._clean_text_for_pdf(report.executive_summary)
        # Render callout box with light emerald tint and dark border
        pdf.set_fill_color(240, 253, 244)  # Emerald 50 tint #F0FDF4
        pdf.set_draw_color(16, 185, 129)  # Emerald 500
        pdf.set_line_width(0.8)

        box_start_y = pdf.get_y()
        # Estimate text height
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(30, 41, 59)  # Slate 800

        # Draw left accent line
        pdf.set_x(pdf.l_margin + 4)
        pdf.multi_cell(width - 6, 5.2, exec_text, border=0, align="L")
        box_end_y = pdf.get_y()

        # Draw left indicator bar
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(1.5)
        pdf.line(pdf.l_margin, box_start_y, pdf.l_margin, box_end_y)

        pdf.ln(6)

        # -------------------------------------------------------------
        # 2. KEY FINDINGS
        # -------------------------------------------------------------
        if report.key_findings:
            ExportService._render_section_heading(pdf, "Key Strategic Findings", width)

            for idx, kf in enumerate(report.key_findings, 1):
                clean_kf = ExportService._clean_text_for_pdf(kf)

                pdf.set_fill_color(248, 250, 252)  # Slate 50
                pdf.set_draw_color(226, 232, 240)  # Slate 200
                pdf.set_line_width(0.3)

                start_y = pdf.get_y()

                # Finding badge number
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(37, 99, 235)  # Blue 600
                pdf.cell(14, 5, f"[{idx:02d}]", align="L")

                # Finding text
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(30, 41, 59)
                pdf.multi_cell(width - 14, 5, clean_kf, align="L")
                pdf.ln(2.5)

            pdf.ln(4)

        # -------------------------------------------------------------
        # 3. DETAILED ANALYSIS BY TOPIC
        # -------------------------------------------------------------
        ExportService._render_section_heading(pdf, "In-Depth Research & Technical Analysis", width)

        detailed_text = ExportService._clean_text_for_pdf(report.detailed_analysis)
        paragraphs = [p.strip() for p in detailed_text.split("\n\n") if p.strip()]

        for p in paragraphs:
            # Check if paragraph looks like a sub-header (starts with ### or short title)
            if p.startswith("### ") or (len(p) < 60 and p.endswith(":")):
                sub_title = p.replace("### ", "").strip()
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(30, 58, 138)  # Deep Navy Blue
                pdf.multi_cell(width, 5.5, sub_title, align="L")
                pdf.ln(1)
            else:
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(30, 41, 59)
                pdf.multi_cell(width, 5.2, p, align="L")
                pdf.ln(3)

        pdf.ln(4)

        # -------------------------------------------------------------
        # 4. METHODOLOGY & EVIDENCE RELIABILITY
        # -------------------------------------------------------------
        if report.methodology or report.evidence_and_citations:
            ExportService._render_section_heading(pdf, "Research Methodology & Evidence Assessment", width)

            if report.methodology:
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(51, 65, 85)
                pdf.cell(width, 5, "Investigation Methodology:", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(71, 85, 105)
                pdf.multi_cell(width, 5, ExportService._clean_text_for_pdf(report.methodology), align="L")
                pdf.ln(3)

            if report.evidence_and_citations:
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(51, 65, 85)
                pdf.cell(width, 5, "Source Credibility & Evidence Verification:", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(71, 85, 105)
                pdf.multi_cell(width, 5, ExportService._clean_text_for_pdf(report.evidence_and_citations), align="L")
                pdf.ln(3)

            pdf.ln(3)

        # -------------------------------------------------------------
        # 5. CONFLICTING EVIDENCE & LIMITATIONS (Alert Box)
        # -------------------------------------------------------------
        if report.conflicting_evidence_and_limitations:
            ExportService._render_section_heading(pdf, "Conflicting Evidence & Gaps", width)

            pdf.set_fill_color(255, 251, 235)  # Amber 50 #FFFBEB
            pdf.set_draw_color(245, 158, 11)   # Amber 500
            pdf.set_line_width(0.3)

            alert_start_y = pdf.get_y()
            pdf.set_x(pdf.l_margin + 4)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(120, 53, 15)  # Amber 900
            pdf.multi_cell(
                width - 6, 
                4.8, 
                ExportService._clean_text_for_pdf(report.conflicting_evidence_and_limitations), 
                align="L"
            )
            alert_end_y = pdf.get_y()

            # Left amber accent bar
            pdf.set_draw_color(245, 158, 11)
            pdf.set_line_width(1.5)
            pdf.line(pdf.l_margin, alert_start_y, pdf.l_margin, alert_end_y)

            pdf.ln(6)

        # -------------------------------------------------------------
        # 6. CONCLUSION
        # -------------------------------------------------------------
        if report.conclusion:
            ExportService._render_section_heading(pdf, "Strategic Conclusion", width)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(width, 5.2, ExportService._clean_text_for_pdf(report.conclusion), align="L")
            pdf.ln(6)

        # -------------------------------------------------------------
        # 7. VERIFIED REFERENCES & SOURCES
        # -------------------------------------------------------------
        ExportService._render_section_heading(pdf, "References & Cited Web Sources", width, min_remaining_space=48)

        if report.references:
            for ref in report.references:
                # Ensure at least 26mm remaining space so reference card never gets split across page edge
                if pdf.get_y() > pdf.h - 26:
                    pdf.add_page()

                card_start_y = pdf.get_y()
                text_x = pdf.l_margin + 12
                text_width = width - 12

                # Number badge [1], [2]
                pdf.set_fill_color(37, 99, 235)  # Blue 600
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 8)
                pdf.rect(pdf.l_margin, card_start_y + 0.5, 9, 5.5, style="F")
                pdf.set_xy(pdf.l_margin, card_start_y + 0.8)
                pdf.cell(9, 5, f"{ref.id}", align="C")

                # Multi-cell Title (wraps naturally, never cuts off mid-word or with ellipsis!)
                pdf.set_xy(text_x, card_start_y)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(15, 23, 42)
                clean_ref_title = ExportService._clean_text_for_pdf(ref.title)
                pdf.multi_cell(text_width, 4.6, clean_ref_title, align="L", link=ref.url)

                # Meta line: Domain and Clean Formatted Publication Date
                clean_date = ""
                if ref.published_date:
                    raw_date = ref.published_date.split("T")[0] if "T" in ref.published_date else ref.published_date
                    clean_date = f"   |   Published: {raw_date}"

                pdf.set_x(text_x)
                pdf.set_font("Helvetica", "", 7.5)
                pdf.set_text_color(100, 116, 139)  # Slate 500
                pdf.multi_cell(text_width, 4.0, f"Source: {ref.domain}{clean_date}", align="L")

                # Complete URL (wraps cleanly over multiple lines, fully clickable, never cut off with '...')
                pdf.set_x(text_x)
                pdf.set_font("Helvetica", "", 7.5)
                pdf.set_text_color(37, 99, 235)  # Link Blue
                pdf.multi_cell(text_width, 3.8, f"URL: {ref.url}", align="L", link=ref.url)

                # Spacing and subtle divider rule between references
                pdf.ln(3)
                pdf.set_draw_color(241, 245, 249)  # Slate 100
                pdf.set_line_width(0.2)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + width, pdf.get_y())
                pdf.ln(3)
        else:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(width, 6, "No external web citations registered.", align="L")
            pdf.ln(4)

        return bytes(pdf.output())

    @staticmethod
    def _render_section_heading(pdf: FPDF, title: str, width: float, min_remaining_space: float = 38):
        """Renders an elegant section header with a colored accent indicator."""
        # Check if near page boundary to prevent orphan headings at bottom of page
        if pdf.get_y() > pdf.h - min_remaining_space:
            pdf.add_page()

        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)  # Slate 900

        # Small colored marker block
        marker_y = pdf.get_y() + 1
        pdf.set_fill_color(16, 185, 129)  # Emerald 500
        pdf.rect(pdf.l_margin, marker_y, 3, 5, style="F")

        pdf.set_x(pdf.l_margin + 5)
        pdf.cell(width - 5, 6, title, new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(2.5)

    @staticmethod
    def _clean_text_for_pdf(text: str) -> str:
        """Strips markdown headers/formatting, normalizes unicode, and breaks long words for FPDF."""
        if not text:
            return ""
        # Strip markdown headers (##, ###) and bold (*, **)
        text = re.sub(r"#{1,6}\s*", "", text)
        text = re.sub(r"\*{1,3}", "", text)
        text = re.sub(r"`{1,3}", "", text)

        # Break any uninterrupted continuous token longer than 40 characters (e.g. long URLs) with space
        words = text.split(" ")
        cleaned_words = []
        for word in words:
            if len(word) > 42 and not "\n" in word:
                chunks = [word[i:i+38] for i in range(0, len(word), 38)]
                cleaned_words.append(" ".join(chunks))
            else:
                cleaned_words.append(word)
        text = " ".join(cleaned_words)

        # Normalize special unicode symbols to clean ASCII/Latin-1
        replacements = {
            "\u2014": " - ",
            "\u2013": " - ",
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2022": "*",
            "\u2026": "...",
            "\u00a9": "(c)",
            "\u00ae": "(R)",
            "\u2122": "TM",
            "\u2192": "->",
        }
        for orig, rep in replacements.items():
            text = text.replace(orig, rep)

        # Replace non-latin1 characters for standard FPDF fonts
        text = text.encode("latin-1", "replace").decode("latin-1")
        return text
