import cv2
import os
from datetime import datetime


def clear_directory(directory):
    """
    Deletes all image files (jpg, png, jpeg) in the specified directory.
    
    Args:
        directory (str): Path to the directory to be cleared
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it...")
        os.makedirs(directory)
        return
    
    file_count = 0
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                file_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    print(f"Cleared {file_count} image files from {directory}")


def extract_frames(video_path, output_dir, interval=2):
    """
    Extracts frames from a video at specified time intervals.
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save the extracted frames
        interval (int): Time interval in seconds between frames
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    print(f"Video FPS: {fps}")
    print(f"Total frames: {total_frames}")
    print(f"Video duration: {duration:.2f} seconds")
    
    frame_interval = int(fps * interval)
    
    count = 0
    frame_count = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    while True:
        success, frame = video.read()
        
        if not success:
            break
        
        if count % frame_interval == 0:
            current_time_sec = count / fps
            
            filename = f"frame_{frame_count:04d}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            cv2.imwrite(output_path, frame)
            print(f"Saved frame at {current_time_sec:.2f}s: {output_path}")
            frame_count += 1
        
        count += 1
    
    video.release()
    print(f"Extracted {frame_count} frames from the video")


if __name__ == "__main__":
    # Hardcoded parameters
    video_path = r"C:\Users\PC\Desktop\grad\WIN_20250502_18_19_02_Pro.mp4"
    candidate_name = "amr"  
    interval = 2  
    clear_old_frames = True  
    
    base_output_dir = os.path.join("content")
    candidate_dir = os.path.join(base_output_dir, candidate_name)
    
    if not os.path.exists(base_output_dir):
        os.makedirs(base_output_dir)
        print(f"Created base output directory: {base_output_dir}")
    
    print(f"Processing video: {video_path}")
    print(f"Candidate name: {candidate_name}")
    print(f"Saving frames to: {candidate_dir}")
    print(f"Frame interval: {interval} seconds")
    
    if clear_old_frames:
        clear_directory(candidate_dir)
    
    extract_frames(video_path, candidate_dir, interval)