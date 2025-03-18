import base64
from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO

import pdfkit

from .exceptions import ExportError
from .schemas import SurveyAnalysisResult

REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Image,
        Table,
        TableStyle,
    )
    from reportlab.platypus.flowables import KeepTogether
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    REPORTLAB_AVAILABLE = True
except ImportError:

    class DummyClass:
        pass

    SimpleDocTemplate = DummyClass
    ParagraphStyle = DummyClass
    A4 = (595.27, 841.89)
    inch = 72.0


try:
    import pandas as pd
except ImportError:
    pd = None


class Exporter(ABC):
    """Base class for all exporters."""

    def __init__(self, analysis_result: SurveyAnalysisResult):
        """Initialize with analysis results."""
        self.analysis_result = analysis_result

    @abstractmethod
    def export(self) -> BytesIO:
        """Export to a specific format."""
        pass


class PDFExporter(Exporter):
    """Export analysis results to PDF format."""

    def export(self) -> BytesIO:
        """Export to PDF."""
        if not REPORTLAB_AVAILABLE:
            raise ExportError(
                "ReportLab package is not installed. Please install it with 'pip install reportlab'."
            )

        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                leftMargin=1 * inch,
                rightMargin=1 * inch,
                topMargin=1 * inch,
                bottomMargin=1 * inch,
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Title"],
                fontSize=16,
                spaceAfter=0.5 * inch,
            )

            heading1_style = ParagraphStyle(
                "Heading1",
                parent=styles["Heading1"],
                fontSize=14,
                spaceAfter=0.2 * inch,
                spaceBefore=0.3 * inch,
            )

            heading2_style = ParagraphStyle(
                "Heading2",
                parent=styles["Heading2"],
                fontSize=12,
                spaceAfter=0.1 * inch,
                spaceBefore=0.2 * inch,
            )

            normal_style = ParagraphStyle(
                "CustomNormal",
                parent=styles["Normal"],
                fontSize=10,
                spaceBefore=0.1 * inch,
                spaceAfter=0.1 * inch,
            )

            story = []

            title_text = f"Survey Analysis Report: {self.analysis_result.survey_title}"
            story.append(Paragraph(title_text, title_style))

            story.append(Paragraph("Survey Overview", heading1_style))

            summary_data = [
                ["Total Responses:", f"{self.analysis_result.total_responses}"],
                ["Completion Rate:", f"{self.analysis_result.completion_rate:.1%}"],
            ]

            summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )

            story.append(summary_table)
            story.append(Spacer(1, 0.3 * inch))

            story.append(Paragraph("Question Analysis", heading1_style))

            for question in self.analysis_result.questions:

                question_elements = []

                q_text = question.summary.question_text
                question_elements.append(Paragraph(q_text, heading2_style))

                meta_text = f"Type: {question.summary.question_type}, Responses: {question.summary.response_count}"
                question_elements.append(Paragraph(meta_text, normal_style))

                question_elements.append(Spacer(1, 0.2 * inch))

                if hasattr(question, "chart_image") and question.chart_image:

                    try:
                        img_data = base64.b64decode(question.chart_image)
                        img = Image(BytesIO(img_data))

                        img.drawHeight = 3.5 * inch
                        img.drawWidth = 5 * inch
                        question_elements.append(img)
                    except Exception as e:
                        question_elements.append(
                            Paragraph(f"Error rendering chart: {str(e)}", normal_style)
                        )

                question_elements.append(Spacer(1, 0.2 * inch))

                question_elements.append(Paragraph("Key Insights:", heading2_style))

                if question.insights:
                    for insight in question.insights:
                        question_elements.append(Paragraph(insight, normal_style))
                else:
                    question_elements.append(
                        Paragraph("No specific insights available.", normal_style)
                    )

                story.append(KeepTogether(question_elements))

                story.append(Spacer(1, 0.5 * inch))

            doc.build(story)

            buffer.seek(0)
            return buffer

        except Exception as e:
            raise ExportError(f"Failed to export PDF: {str(e)}")


class ExcelExporter(Exporter):
    """Exports survey analysis to Excel."""

    def export(self) -> BytesIO:
        """
        Export the analysis to an Excel file.

        Returns:
            BytesIO object containing the Excel file
        """
        try:
            buffer = BytesIO()

            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:

                self._create_summary_sheet(writer)

                for i, question in enumerate(self.analysis_result.questions):
                    sheet_name = f"Q{i+1}"
                    self._create_question_sheet(question, sheet_name, writer)

            buffer.seek(0)
            return buffer
        except Exception as e:
            raise ExportError(f"Failed to export Excel file: {str(e)}")

    def _create_summary_sheet(self, writer):
        """Create the summary sheet with general information."""
        summary_data = {
            "Survey ID": [self.analysis_result.survey_id],
            "Survey Title": [self.analysis_result.survey_title],
            "Total Responses": [self.analysis_result.total_responses],
            "Completion Rate": [f"{self.analysis_result.completion_rate:.1%}"],
            "Average Time": [self.analysis_result.average_time_to_complete or "N/A"],
            "Report Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        }

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        questions_data = []
        for i, question in enumerate(self.analysis_result.questions):
            summary = question.summary
            questions_data.append(
                {
                    "Question #": i + 1,
                    "Question Text": summary.question_text,
                    "Type": summary.question_type,
                    "Responses": summary.response_count,
                    "Sheet Name": f"Q{i+1}",
                }
            )

        questions_df = pd.DataFrame(questions_data)
        questions_df.to_excel(writer, sheet_name="Summary", startrow=8, index=False)

        workbook = writer.book
        worksheet = writer.sheets["Summary"]

        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#D7E4BC", "border": 1}
        )

        for col_num, value in enumerate(summary_df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        for col_num, value in enumerate(questions_df.columns.values):
            worksheet.write(8, col_num, value, header_format)

    def _create_question_sheet(self, question, sheet_name, writer):
        """Create a sheet for an individual question."""
        summary = question.summary

        info_data = {
            "Property": ["Question Text", "Question Type", "Total Responses"],
            "Value": [
                summary.question_text,
                summary.question_type,
                summary.response_count,
            ],
        }

        info_df = pd.DataFrame(info_data)
        info_df.to_excel(writer, sheet_name=sheet_name, index=False)

        if summary.question_type in ["radio", "dropdown"]:
            self._add_single_choice_data(summary, sheet_name, writer)
        elif summary.question_type == "checkbox":
            self._add_multiple_choice_data(summary, sheet_name, writer)
        elif summary.question_type == "text":
            self._add_text_data(summary, sheet_name, writer)

    def _add_single_choice_data(self, summary, sheet_name, writer):
        """Add single choice question data."""
        option_counts = summary.option_counts or {}

        if not option_counts:
            return

        data = {
            "Option": list(option_counts.keys()),
            "Count": list(option_counts.values()),
            "Percentage": [
                f"{count/summary.response_count*100:.1f}%"
                for count in option_counts.values()
            ],
        }

        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet_name, startrow=4, index=False)

    def _add_multiple_choice_data(self, summary, sheet_name, writer):
        """Add multiple choice question data."""
        option_counts = summary.option_counts or {}

        if not option_counts:
            return

        sorted_options = sorted(option_counts.items(), key=lambda x: x[1], reverse=True)

        data = {
            "Option": [item[0] for item in sorted_options],
            "Count": [item[1] for item in sorted_options],
            "Percentage of Respondents": [
                f"{item[1]/summary.response_count*100:.1f}%" for item in sorted_options
            ],
        }

        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet_name, startrow=4, index=False)

    def _add_text_data(self, summary, sheet_name, writer):
        """Add text question data."""
        text_responses = summary.text_responses or []

        if not text_responses:
            empty_df = pd.DataFrame({"No text responses received": []})
            empty_df.to_excel(writer, sheet_name=sheet_name, startrow=4, index=False)
            return

        data = {
            "Response #": list(range(1, len(text_responses) + 1)),
            "Text Response": text_responses,
        }

        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet_name, startrow=4, index=False)
