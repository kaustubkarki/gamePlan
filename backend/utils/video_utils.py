import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames


def save_video(output_video_frames, output_video_path):
    """
    Save a list of frames as a video to the specified output path.

    Parameters:
    - output_video_frames: List of frames (numpy arrays).
    - output_video_path: Path where the output video will be saved.

    Returns:
    - None
    """
    # Check if there are any frames to save
    if not output_video_frames or len(output_video_frames) == 0:
        raise ValueError("No frames to write to the video file.")
    
    # Determine codec and output format based on file extension
    file_extension = output_video_path.split('.')[-1].lower()
    if file_extension == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Compatible codec for MP4
    elif file_extension == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Compatible codec for AVI
    else:
        raise ValueError(f"Unsupported video format: {file_extension}. Use .mp4 or .avi")
    
    # Video properties
    frame_height, frame_width = output_video_frames[0].shape[:2]
    fps = 24  # Adjust as needed

    # Initialize VideoWriter
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Write frames to the video
    for frame in output_video_frames:
        out.write(frame)

    # Release resources
    out.release()
    print(f"Video saved successfully to {output_video_path}")