from interview_agent.technical_depth_analysis import run_exam_pipeline
from interview_agent.speech_to_text import transcribe_mp3
from interview_agent.emotion import analyze_emotional_state
from interview_agent.pixtral import analyze_with_pixtral_model
from interview_agent.sentiment_analysis import format_analysis_report
from interview_agent.sentiment_analysis import analyze_interview_advanced

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import re
import base64
import requests


def update_supabase_profile( payload: dict):
    url = "https://***REMOVED***/rest/v1/profiles?id=eq.353764fa-5193-42fb-b8f0-1bf31013bdf9"
    headers = {
        "apikey": "***REMOVED***",
        "Authorization": "Bearer ***REMOVED***",
        "Content-Type": "application/json"
    }
    new_payload = {"video_analysis": payload}

    response = requests.patch(url, headers=headers, json=new_payload)
    if response.status_code == 201:
        return "Profile updated successfully." 
    else:
        return f"Failed to update profile: {response.status_code}"

def encode_pdf_to_base64(pdf_path):
    """
    Reads a PDF file from the given path and returns its Base64-encoded string.
    
    :param pdf_path: Path to the PDF file.
    :return: Base64-encoded string of the PDF content.
    """
    try:
        with open(pdf_path, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")
        return encoded_string
    except Exception as e:
        print(f"Error encoding PDF: {e}")
        return None

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for (page_num, page_state) in enumerate(self._saved_page_states):
            self.__dict__.update(page_state)
            self.draw_page_number(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_num, total_pages):
        self.setFont("Helvetica", 9)
        self.setFillColor(grey)
        self.drawRightString(A4[0] - 40, 30, f"Page {page_num} of {total_pages}")
        # Add a subtle footer line
        self.setStrokeColor(HexColor("#E0E0E0"))
        self.setLineWidth(0.5)
        self.line(40, 50, A4[0] - 40, 50)

def generate_pdf_report(analysis_data: dict, filename: str = None) -> str:
    """
    Generate a beautiful and professional PDF report using reportlab from interview analysis results.

    Args:
        analysis_data (dict): Dictionary with 'sentiment_analysis' and 'pixtral_insights' keys.
        filename (str, optional): Output PDF filename. If None, timestamp will be used.

    Returns:
        str: Path to the generated PDF file.
    """
    if not filename:
        filename = f"interview_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(os.getcwd(), filename)

    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        rightMargin=50, 
        leftMargin=50,
        topMargin=80, 
        bottomMargin=70
    )

    # Enhanced styles
    styles = getSampleStyleSheet()
    
    # Custom styles for professional look
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=HexColor("#2C3E50"),
        fontName="Helvetica-Bold"
    )
    
    subtitle_style = ParagraphStyle(
        name="CustomSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=40,
        textColor=HexColor("#7F8C8D"),
        fontName="Helvetica"
    )
    
    section_header_style = ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HexColor("#34495E"),
        fontName="Helvetica-Bold",
        borderWidth=2,
        borderColor=HexColor("#3498DB"),
        borderPadding=8,
        backColor=HexColor("#F8F9FA")
    )
    
    subsection_style = ParagraphStyle(
        name="Subsection",
        parent=styles["Heading3"],
        fontSize=13,
        leading=16,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HexColor("#2980B9"),
        fontName="Helvetica-Bold"
    )
    
    body_style = ParagraphStyle(
        name="CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor=HexColor("#2C3E50"),
        fontName="Helvetica"
    )
    
    highlight_style = ParagraphStyle(
        name="Highlight",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=8,
        leftIndent=20,
        rightIndent=20,
        borderWidth=1,
        borderColor=HexColor("#E74C3C"),
        borderPadding=10,
        backColor=HexColor("#FDF2F2"),
        textColor=HexColor("#C0392B")
    )

    content = []

    # Header with logo space and title
    content.append(Paragraph("COMPREHENSIVE INTERVIEW ANALYSIS REPORT", title_style))
    
    # Subtitle with timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
    content.append(Paragraph(f"Generated on {timestamp}", subtitle_style))
    
    # Executive Summary Box
    exec_summary_data = [
        ["EXECUTIVE SUMMARY", ""],
        ["Analysis Type:", "Comprehensive Video Interview Assessment"],
        ["Components:", "• Sentiment Analysis\n• Emotional State Recognition\n• Behavioral Insights"],
        ["Processing Date:", timestamp],
        ["Status:", "Complete"]
    ]
    
    exec_table = Table(exec_summary_data, colWidths=[2*inch, 4*inch])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#34495E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, HexColor("#BDC3C7")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    content.append(exec_table)
    content.append(Spacer(1, 30))

    # Section 1: Sentiment Analysis
    content.append(Paragraph("1. SENTIMENT & COMMUNICATION ASSESSMENT", section_header_style))
    content.append(Spacer(1, 10))
    
    # Parse and format sentiment analysis
    sentiment_text = analysis_data.get('sentiment_analysis', '')
    formatted_sentiment = format_analysis_text(sentiment_text, body_style, subsection_style, highlight_style)
    content.extend(formatted_sentiment)
    
    content.append(Spacer(1, 20))

    # Section 2: Pixtral Insights
    content.append(Paragraph("2. EMOTIONAL & BEHAVIORAL VIDEO INSIGHTS", section_header_style))
    content.append(Spacer(1, 10))
    
    # Parse and format pixtral insights
    pixtral_text = analysis_data.get('pixtral_insights', '')
    formatted_pixtral = format_analysis_text(pixtral_text, body_style, subsection_style, highlight_style)
    content.extend(formatted_pixtral)
    
    content.append(Spacer(1, 30))
    
    # Footer section
    # content.append(Paragraph("ANALYSIS METHODOLOGY", section_header_style))
    # methodology_text = """
    # This comprehensive analysis employs advanced machine learning models to evaluate multiple dimensions of interview performance:
    
    # • <b>Speech-to-Text Transcription:</b> High-accuracy audio processing for complete dialogue capture
    # • <b>Sentiment Analysis:</b> Natural language processing to assess emotional tone and communication patterns
    # • <b>Emotional State Recognition:</b> Computer vision analysis of facial expressions and body language
    # • <b>Behavioral Insights:</b> Multi-modal assessment combining audio and visual cues for comprehensive evaluation
    
    # All analyses are performed using state-of-the-art AI models to provide objective, data-driven insights.
    # """
    # content.append(Paragraph(methodology_text, body_style))

    # Build PDF with custom canvas for page numbers
    doc.build(content, canvasmaker=NumberedCanvas)
    return output_path

def format_analysis_text(text: str, body_style, subsection_style, highlight_style):
    """
    Format analysis text with proper styling and structure.
    """
    if not text:
        return [Paragraph("No analysis data available.", body_style)]
    
    content = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a header/title (contains keywords or is all caps)
        if (line.isupper() and len(line) > 5) or any(keyword in line.lower() for keyword in ['analysis', 'summary', 'assessment', 'evaluation', 'insights']):
            content.append(Paragraph(line, subsection_style))
        # Check if line contains important metrics or scores
        elif any(keyword in line.lower() for keyword in ['score:', 'rating:', 'confidence:', 'probability:', 'level:']):
            content.append(Paragraph(line, highlight_style))
        # Check if line is a bullet point
        elif line.startswith(('•', '-', '*')) or re.match(r'^\d+\.', line):
            content.append(Paragraph(line, body_style))
        # Regular content
        else:
            content.append(Paragraph(line, body_style))
    
    return content

def analyze_video_workflow(video_path: str) -> dict:
    """
    Wrapper function to perform a complete analysis on a video.
    
    Workflow:
    1. Transcribe video audio using transcribe_mp3.
    2. Analyze sentiment from the transcribed text.
    3. Analyze emotional state from the video.
    
    Returns:
        dict: A dictionary containing the transcript, sentiment analysis, and emotional insights.
    """
    # Step 1: Transcription
    transcript = transcribe_mp3(video_path)
    
    # Step 2: Sentiment Analysis
    sentiment_result = analyze_interview_advanced(transcript)
    report = format_analysis_report(sentiment_result)
    # Step 3: Emotional State Analysis
    emotional_insights = analyze_emotional_state(video_path, 2)
    pixtral_insights = analyze_with_pixtral_model("interview_agent\\output")
    result = {
        "sentiment_analysis": report,
        "pixtral_insights": pixtral_insights
    }
    pdf_path = generate_pdf_report(result)
    
    encoded = encode_pdf_to_base64(pdf_path)
    os.remove(pdf_path)  # Clean up the PDF file after encoding
    # Final result
    update_supabase_profile(result)
    return {
        "sentiment_analysis": report,
        "pixtral_insights": pixtral_insights,
        "pdf_report_base64": encoded
    }

if __name__ == "__main__":
    video_path = "interview_agent/Emaraty.mp4"
    result = analyze_video_workflow(video_path)

    print("Analysis complete. Generating PDF report...")
    pdf_path = generate_pdf_report(result)
    print(f"Professional PDF report saved to: {pdf_path}")