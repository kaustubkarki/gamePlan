import sys
import os

def process_video(video_path):
    print(f"Processing video: {video_path}")
    # Check if the file exists
    if not os.path.exists(video_path):
        print("Error: Video file not found")
        sys.exit(1)
    
    # Simulated processing logic (replace with your actual processing)
    print("Video processing completed successfully")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <video_file_path>")
        sys.exit(1)

    video_file_path = sys.argv[1]
    process_video(video_file_path)
