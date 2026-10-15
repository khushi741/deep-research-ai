from app.models.research import ResearchReport, Citation
from app.services.export_service import ExportService


def test_markdown_export():
    report = ResearchReport(
        title="Test Report",
        executive_summary="Summary text",
        methodology="Methodology text",
        key_findings=["Finding 1", "Finding 2"],
        detailed_analysis="Analysis text [1]",
        evidence_and_citations="Evidence text",
        conflicting_evidence_and_limitations="Limitations text",
        unanswered_questions="Questions text",
        conclusion="Conclusion text",
        references=[
            Citation(id=1, url="https://example.com/source", title="Example Source", domain="example.com")
        ],
        full_markdown="# Test Report\n\nExecutive Summary text"
    )

    md_bytes = ExportService.generate_markdown_bytes(report)
    assert isinstance(md_bytes, bytes)
    assert b"Test Report" in md_bytes


def test_pdf_export():
    report = ResearchReport(
        title="Test PDF Report",
        executive_summary="Summary text for PDF generation testing.",
        methodology="Methodology text",
        key_findings=["Finding 1", "Finding 2"],
        detailed_analysis="Analysis narrative with inline citation [1].",
        evidence_and_citations="Evidence text",
        conflicting_evidence_and_limitations="Limitations text",
        unanswered_questions="Questions text",
        conclusion="Conclusion text",
        references=[
            Citation(id=1, url="https://example.com/pdf-source", title="PDF Source", domain="example.com")
        ],
        full_markdown="# Test Report"
    )

    pdf_bytes = ExportService.generate_pdf_bytes(report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500  # Valid PDF binary length
    assert pdf_bytes.startswith(b"%PDF")
