from technical_depth_analysis import run_exam_pipeline
from speech_to_text import transcribe_mp3
from emotion import analyze_emotional_state
from pixtral import analyze_with_pixtral_model
from sentiment_analysis import format_analysis_report
from sentiment_analysis import analyze_interview_advanced

from fpdf import FPDF
from datetime import datetime


from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os

def generate_pdf_report(analysis_data: dict, filename: str = None) -> str:
    """
    Generate a professional PDF report using reportlab from interview analysis results.

    Args:
        analysis_data (dict): Dictionary with 'sentiment_analysis' and 'pixtral_insights' keys.
        filename (str, optional): Output PDF filename. If None, timestamp will be used.

    Returns:
        str: Path to the generated PDF file.
    """
    if not filename:
        filename = f"interview_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(os.getcwd(), filename)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()
    content = []

    # Title
    title_style = ParagraphStyle(name="TitleStyle", fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=20)
    content.append(Paragraph("Comprehensive Interview Analysis Report", title_style))

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content.append(Paragraph(f"Generated on: {timestamp}", styles["Normal"]))
    content.append(Spacer(1, 20))

    # Section 1: Sentiment Analysis
    section_title = ParagraphStyle(name="SectionTitle", fontSize=14, spaceAfter=10, leading=18)
    content.append(Paragraph("1. Sentiment & Communication Assessment", section_title))

    for line in analysis_data.get('sentiment_analysis', '').split('\n'):
        content.append(Paragraph(line.strip(), styles["Normal"]))
    content.append(Spacer(1, 15))

    # Section 2: Pixtral Insights
    content.append(Paragraph("2. Emotional & Behavioral Video Insights (Pixtral)", section_title))

    for line in analysis_data.get('pixtral_insights', '').split('\n'):
        content.append(Paragraph(line.strip(), styles["Normal"]))
    content.append(Spacer(1, 15))

    doc.build(content)

    return output_path



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

    pixtral_insights = analyze_with_pixtral_model("C:\\Users\\Mohammed\\OneDrive - Nile University\\Desktop\\grad\\interview_agent\\output")

    # Final result
    return  {
        "sentiment_analysis": report,
        "pixtral_insights": pixtral_insights
    }


if __name__ == "__main__":
    video_path = "interview_agent/Emaraty.mp4"
    result = analyze_video_workflow(video_path)

    print(result)
    pdf_path = generate_pdf_report(result)
    print(f"PDF report saved to: {pdf_path}")
