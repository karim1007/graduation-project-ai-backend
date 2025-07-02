import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(r"C:\Users\Mohammed\OneDrive - Nile University\Desktop\grad\interview_agent\Emaraty.mp4")
ret, frame = cap.read()
cap.release()

cv2.imwrite("test_frame.jpg", frame)

if ret:
    result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
    print("DeepFace Output:", result)
else:
    print("❌ Could not read frame.")
