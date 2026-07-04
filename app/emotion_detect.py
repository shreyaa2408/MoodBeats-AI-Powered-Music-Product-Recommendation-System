


# from deepface import DeepFace
# import cv2

# def detect_emotion():
#     print("🟡 Emotion detection started...")

#     cap = cv2.VideoCapture(0)
#     detected_emotion = "neutral"

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("❌ Failed to read from webcam.")
#             break

#         try:
#             result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
#             detected_emotion = result[0]['dominant_emotion']
#             print("✅ Detected emotion:", detected_emotion)
#             break
#         except Exception as e:
#             print("❌ Error in detection:", e)
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     return detected_emotion

from deepface import DeepFace
import cv2
import time
from collections import Counter

def detect_emotion():
    print("🟡 Starting emotion detection...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera could not be opened.")
        return "neutral"

    emotions = []
    frames_to_capture = 10
    min_confidence = 50

    try:
        for i in range(frames_to_capture):
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame capture failed.")
                continue

            try:
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = result[0]['dominant_emotion']
                confidence = result[0]['emotion'][dominant_emotion]

                print(f"Frame {i+1}: {dominant_emotion} ({confidence:.2f}%)")

                if confidence >= min_confidence:
                    emotions.append(dominant_emotion)

                time.sleep(0.2)  # Small delay between captures

            except Exception as e:
                print("❌ Error in DeepFace analyze:", e)
                continue

    finally:
        cap.release()
        cv2.destroyAllWindows()

    if emotions:
        # Return the most frequent emotion from captured ones
        final_emotion = Counter(emotions).most_common(1)[0][0]
        print("✅ Final detected emotion:", final_emotion)
        return final_emotion
    else:
        print("⚠️ No confident emotion detected.")
        return "neutral"
