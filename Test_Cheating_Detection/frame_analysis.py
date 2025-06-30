import cv2
import os
import json
import math
from ultralytics import YOLO
import mediapipe as mp

model = YOLO("yolov8l.pt")
classNames = model.names
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

def classify_image(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = model(image)

    people_count = 0
    communication_device_present = False

    for box in results[0].boxes:
        cls = int(box.cls[0])
        detected_class = classNames[cls]

        if detected_class == "person":
            people_count += 1
        elif detected_class in ["laptop", "remote", "cell phone", "tvmonitor"]:
            communication_device_present = True

    direction_looking = "at-system"

    if people_count == 1:
        pose_result = pose.process(image_rgb)

        if pose_result.pose_landmarks:
            nose = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            left_eye = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE]
            right_eye = pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE]

            h, w, _ = image.shape
            nose_coords = (int(nose.x * w), int(nose.y * h))
            left_eye_coords = (int(left_eye.x * w), int(left_eye.y * h))
            right_eye_coords = (int(right_eye.x * w), int(right_eye.y * h))

            # Optionally visualize the points with colored dots
            # cv2.circle(image, nose_coords, 5, (0, 0, 255), -1)  # Red for nose
            # cv2.circle(image, left_eye_coords, 5, (0, 255, 0), -1)  # Green for left eye
            # cv2.circle(image, right_eye_coords, 5, (255, 0, 0), -1)  # Blue for right eye

            mid_eye_x = (left_eye_coords[0] + right_eye_coords[0]) / 2
            mid_eye_y = (left_eye_coords[1] + right_eye_coords[1]) / 2
            dist_nose_mid_eye_x = abs(nose_coords[0] - mid_eye_x)
            dist_nose_mid_eye_y = abs(nose_coords[1] - mid_eye_y)
            dist_between_eyes = math.sqrt((right_eye_coords[0] - left_eye_coords[0])**2 + (right_eye_coords[1] - left_eye_coords[1])**2)

            screen_threshold_x = dist_between_eyes * 0.2
            screen_threshold_y = dist_between_eyes * 0.2

            if dist_nose_mid_eye_x < screen_threshold_x and dist_nose_mid_eye_y < screen_threshold_y:
                direction_looking = "at-system"
            else:
                if nose_coords[1] < mid_eye_y and nose_coords[0] < mid_eye_x:
                    direction_looking = "up-left"
                elif nose_coords[1] < mid_eye_y and nose_coords[0] > mid_eye_x:
                    direction_looking = "up-right"
                elif nose_coords[1] > mid_eye_y and nose_coords[0] < mid_eye_x:
                    direction_looking = "down-left"
                elif nose_coords[1] > mid_eye_y and nose_coords[0] > mid_eye_x:
                    direction_looking = "down-right"

    output = {
        "people_count": people_count,
        "direction-looking": direction_looking,
        "communication_device_present": communication_device_present,
        "image_path": image_path
    }
    
    cv2.imshow("name", image)
    cv2.waitKey(1)  # Add small delay to show image

    return output  # Return dictionary instead of JSON string

def process_directory(directory_path):
    """
    Process all images in a directory and return a list of JSON results
    
    Args:
        directory_path (str): Path to directory containing images
        
    Returns:
        list: List of JSON objects with detection results for each image
    """
    results_list = []
    
    if not os.path.exists(directory_path):
        return results_list
    
    images = os.listdir(directory_path)
    
    for img_name in images:
        if img_name.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(directory_path, img_name)
            result = classify_image(img_path)
            results_list.append(result)
    
    cv2.destroyAllWindows()  # Close any open windows when done
    return results_list

# Example usage
if __name__ == "__main__":
    dir_path = "Test_Cheating_Detection\\frames\\kokita"
    results = process_directory(dir_path)
    
    # Print the results as JSON strings
    for result in results:
        print(json.dumps(result, indent=4))
    
    # Or return the entire list as a single JSON string
    # all_results_json = json.dumps(results, indent=4)
    # print(all_results_json)
