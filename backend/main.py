import sys
import os
import pickle
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI
from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
import cv2
import numpy as np
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

app = FastAPI(debug=True)

# CORS settings
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
input_videos_dir = "input_videos"
output_videos_dir = "output_videos"

os.makedirs(input_videos_dir, exist_ok=True)
os.makedirs(output_videos_dir, exist_ok=True)

def process_video(input_video_path, output_video_path):
    # Read Video
    video_frames = read_video(input_video_path)

    # Generate a unique stub path
    video_name = os.path.splitext(os.path.basename(input_video_path))[0]
    stub_path = f'stubs/{video_name}_track_stubs.pkl'

    # Initialize Tracker
    tracker = Tracker('models/best1.pt')

    # Get Tracks (validate or regenerate as needed)
    if not os.path.exists(stub_path):
        print(f"Stub file not found: {stub_path}. Generating new stubs...")
        tracks = tracker.get_object_tracks(video_frames, read_from_stub=False, stub_path=stub_path)
    else:
        print(f"Using existing stub file: {stub_path}")
        tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=stub_path)
    
    # Ensure tracks are in the correct format
    if not isinstance(tracks, dict):
        raise ValueError("Tracks data is not in the expected format.")
    
    # Get object positions
    tracker.add_position_to_tracks(tracks)

    # Camera Movement Estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_stub_path = 'stubs/camera_movement_stub.pkl'

    # Load camera movement data
    if os.path.exists(camera_movement_stub_path):
        print(f"Using existing stub file: {camera_movement_stub_path}")
        with open(camera_movement_stub_path, 'rb') as f:
            camera_movement_per_frame = pickle.load(f)
    else:
        print(f"Stub file not found: {camera_movement_stub_path}. Generating new stubs...")
        camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
            video_frames,
            read_from_stub=False,
            stub_path=camera_movement_stub_path
        )

    # Debugging output for camera movement data
    print(f"Camera movement data type: {type(camera_movement_per_frame)}")
    if isinstance(camera_movement_per_frame, list):
        print(f"First element in camera movement list: {camera_movement_per_frame[0]}")

    # View Transformation
    frame_height, frame_width, _ = video_frames[0].shape
    view_transformer = ViewTransformer((frame_height, frame_width))
    view_transformer.add_transformed_position_to_tracks(tracks)
    
    # Ensure 'position_transformed' key exists
    for frame_tracks in tracks.get('players', []):
        for player_id, player_data in frame_tracks.items():
            if 'position_transformed' not in player_data:
                player_data['position_transformed'] = None
    
    # Interpolate Ball Positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    # Speed and Distance Estimation
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)
    
    # Assign Player Teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            tracks['players'][frame_num][player_id]['team'] = team 
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
            
    # Assign Ball Acquisition
    player_assigner = PlayerBallAssigner()
    team_ball_control = []
    for frame_num, player_track in enumerate(tracks['players']):
        ball_bbox = tracks['ball'][frame_num][1]['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)
        if assigned_player != -1:
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            team_ball_control.append(tracks['players'][frame_num][assigned_player]['team'])
        else:
            team_ball_control.append(team_ball_control[-1])
    team_ball_control = np.array(team_ball_control)

    # Draw Annotations
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)
    
    # Draw Camera Movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames, camera_movement_per_frame)
    
    # Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

    # Save cropped image of a player
    for track_id, player in tracks['players'][0].items():
        bbox = player['bbox']
        frame = video_frames[0]
        cropped_image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
        cropped_image_path = os.path.join(output_videos_dir, 'cropped_image.jpg')
        cv2.imwrite(cropped_image_path, cropped_image)
        print(f"Cropped image saved at: {cropped_image_path}")
        break
    
    # Save Annotated Video
    save_video(output_video_frames, 'output_videos/output_video.avi')
    print(f"Processed video saved at: {output_video_path}")
    
def process_video_task(input_video_path, output_video_path):
    try:
        process_video(input_video_path, output_video_path)
    except Exception as e:
        print(f"Error in background processing: {e}")

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        input_video_path = os.path.join(input_videos_dir, file.filename)
        with open(input_video_path, "wb") as f:
            f.write(await file.read())
        print(f"Video uploaded to: {input_video_path}")

        output_video_path = os.path.join(output_videos_dir, f"processed_{file.filename}")
        background_tasks.add_task(process_video_task, input_video_path, output_video_path)

        

        return JSONResponse(
            content={
                "message": "Video uploaded and processed successfully",
                "video_url": f"/output/{os.path.basename(output_video_path)}"
            },
            status_code=202
        )
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/output/{video_filename}")
async def get_processed_video(video_filename: str):
    video_path = os.path.join(output_videos_dir, video_filename)
    if os.path.exists(video_path):
        return FileResponse(video_path)
    else:
        raise HTTPException(status_code=404, detail="Video not found")
    
@app.get("/download/{video_filename}")
async def download_video(video_filename: str):
    video_path = os.path.join(output_videos_dir, video_filename)
    if os.path.exists(video_path):
        return StreamingResponse(
            open(video_path, "rb"),
            media_type="video/avi",
            headers={"Content-Disposition": f"attachment; filename={video_filename}"},
        )
    else:
        raise HTTPException(status_code=404, detail="Video not found")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
