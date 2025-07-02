import os
import json
import glob
from mistralai import Mistral

# === Configuration ===
MODEL_NAME = "pixtral-12b-2409"
API_KEY = "***REMOVED***"  # <<< REPLACE with your real API key

def load_confidence_stress_report(report_path: str) -> dict:
    with open(report_path, 'r') as f:
        return json.load(f)

def get_snapshot_images(frames_dir: str):
    return sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))

def format_messages(metadata: dict, image_paths: list) -> list:
    emotions = metadata.get("emotion_distribution", {})
    confidence = metadata.get("confidence_inference", "Unknown")
    stress = metadata.get("stress_inference", "Unknown")
    snapshots = metadata.get("snapshots", {})

    emotion_summary = "\n".join([f"- {k}: {v}%" for k, v in emotions.items()])
    snapshot_summary = [
        f"Total snapshot frames: {len(image_paths)}",
        f"Fear >50% Frame: {snapshots.get('fear_over_50_frame', 'Not detected')}",
        f"Peak Happy Frame: {snapshots.get('peak_happy_frame', 'Not detected')}",
        f"Peak Stress Frame: {snapshots.get('peak_stress_frame', 'Not detected')}"
    ]

    system_prompt = (
        "You are a behavioral analysis assistant. "
        "Your task is to summarize a candidate's performance during an interview "
        "based on emotion analysis snapshots and inferred emotional metrics."
    )

    user_prompt = f"""Emotion Distribution:
{emotion_summary}

Confidence Level: {confidence}
Stress Level: {stress}

Snapshot Summary:
{chr(10).join(snapshot_summary)}

Based on the above data, write a professional and concise evaluation of the candidate's emotional performance and behavioral indicators.
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

def analyze_with_pixtral_model(output_dir: str):
    # Paths
    report_path = os.path.join(output_dir, "confidence_stress_analysis.json")
    frames_dir = os.path.join(output_dir, "frames")

    if not os.path.exists(report_path) or not os.path.exists(frames_dir):
        print("❌ Required files not found.")
        return

    # Load data
    metadata = load_confidence_stress_report(report_path)
    image_paths = get_snapshot_images(frames_dir)
    messages = format_messages(metadata, image_paths)

    # Connect to Pixtral model via Mistral
    client = Mistral(api_key=API_KEY)
    response = client.chat.complete(model=MODEL_NAME, messages=messages)

    summary_text = response.choices[0].message.content.strip()

    # Save output
    output_path = os.path.join(output_dir, "pixtral_summary.txt")
    with open(output_path, "w") as f:
        f.write(summary_text)

    print(f"✅ Pixtral summary generated and saved to: {output_path}")

if __name__ == "__main__":
    analyze_with_pixtral_model("output")
