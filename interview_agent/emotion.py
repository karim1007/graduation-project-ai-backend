import cv2
from deepface import DeepFace
from collections import defaultdict
import json
from tqdm import tqdm
import os

def analyze_emotional_state(video_path, frame_interval=30):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    emotion_tally = defaultdict(int)

    frame_idx = 0
    pbar = tqdm(total=total_frames)

    # Snapshot placeholders
    fear_snapshot_taken = False
    peak_happy_score = -1
    peak_happy_frame = None
    peak_happy_img = None

    peak_stress_score = -1
    peak_stress_frame = None
    peak_stress_img = None

    os.makedirs("interview_agent/output/frames", exist_ok=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            try:
                analysis = DeepFace.analyze(
                    frame,
                    actions=['emotion'],
                    enforce_detection=False,
                    silent=True
                )
                emotion = analysis[0]['dominant_emotion']
                emotion_scores = analysis[0]['emotion']
                emotion_tally[emotion] += 1

                # 1. First frame where fear > 50%
                if not fear_snapshot_taken and emotion_scores.get("fear", 0) > 50:
                    cv2.imwrite(f"interview_agent/output/frames/fear_over_50_frame_{frame_idx}.jpg", frame)
                    fear_snapshot_taken = True

                # 2. Peak happy frame
                if emotion_scores.get("happy", 0) > peak_happy_score:
                    peak_happy_score = emotion_scores["happy"]
                    peak_happy_frame = frame_idx
                    peak_happy_img = frame.copy()

                # 3. Frame of highest stress mix
                stress_score = emotion_scores.get("fear", 0) + emotion_scores.get("angry", 0) + emotion_scores.get("sad", 0)
                if stress_score > peak_stress_score:
                    peak_stress_score = stress_score
                    peak_stress_frame = frame_idx
                    peak_stress_img = frame.copy()

            except Exception as e:
                print(f"Frame {frame_idx}: Error -> {e}")

        frame_idx += 1
        pbar.update(1)

    # Save peak emotion frames
    if peak_happy_img is not None:
        cv2.imwrite(f"interview_agent/output/frames/peak_happy_frame_{peak_happy_frame}.jpg", peak_happy_img)

    if peak_stress_img is not None:
        cv2.imwrite(f"interview_agent/output/frames/peak_stress_frame_{peak_stress_frame}.jpg", peak_stress_img)

    cap.release()
    pbar.close()

    total_detections = sum(emotion_tally.values())
    emotion_distribution = {
        emo: round((count / total_detections) * 100, 2)
        for emo, count in emotion_tally.items()
    }

    result = {
        "emotion_distribution": emotion_distribution,
        "confidence_inference": infer_confidence(emotion_distribution),
        "stress_inference": infer_stress(emotion_distribution),
        "snapshots": {
            "fear_over_50_frame": f"frame_{frame_idx}" if fear_snapshot_taken else "not_found",
            "peak_happy_frame": peak_happy_frame,
            "peak_stress_frame": peak_stress_frame
        }
    }

    os.makedirs("interview_agent/output", exist_ok=True)
    with open("interview_agent/output/confidence_stress_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ Analysis complete. Results and frames saved to: interview_agent/output/")

def infer_confidence(emotions):
    confident_emotions = emotions.get("happy", 0) + emotions.get("neutral", 0)
    unconfident_emotions = emotions.get("fear", 0) + emotions.get("sad", 0)

    if confident_emotions > 70:
        return "High confidence"
    elif unconfident_emotions > 40:
        return "Low confidence"
    else:
        return "Moderate confidence"

def infer_stress(emotions):
    stressed = emotions.get("fear", 0) + emotions.get("angry", 0) + emotions.get("sad", 0)
    relaxed = emotions.get("happy", 0) + emotions.get("neutral", 0)

    if stressed > 50:
        return "High stress"
    elif relaxed > 60:
        return "Relaxed"
    else:
        return "Mildly stressed"

if __name__ == "__main__":
    analyze_emotional_state(
        r"C:\Users\Mohammed\OneDrive - Nile University\Desktop\grad\interview_agent\Emaraty.mp4",
        frame_interval=5
    )
