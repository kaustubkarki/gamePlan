import os
import cv2
import uvicorn
import numpy as np
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import  JSONResponse
from fastapi import FastAPI
from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
import logging
import aiofiles
import ffmpeg 

app = FastAPI(debug=True)

# CORS settings
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify the origins you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
input_videos_dir = "input_videos"
output_videos_dir = "output_videos"

#chunk size desc 1 mb
CHUNK_SIZE = 1024 * 1024 

#base Directory
base_dir = os.getcwd()

os.makedirs(input_videos_dir, exist_ok=True)
os.makedirs(output_videos_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video(input_video_path, output_video_path):
    video_path = input_video_path
    video_frames = read_video(video_path)

    # Generate a unique stub path
    video_name = os.path.splitext(os.path.basename(video_path))[0]  
    stub_path = f'stubs/{video_name}_track_stubs.pkl'

    # Initialize Tracker
    tracker = Tracker('models/best1.pt')
    
    # Get Tracks (validate or regenerate as needed)
    tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=stub_path)
    
    # Get object positions 
    tracker.add_position_to_tracks(tracks)
    # camera movement estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                                read_from_stub=True,
                                                                                stub_path='stubs/camera_movement_stub.pkl')
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks,camera_movement_per_frame)
    
    
    # View Trasnformer
    frame_height, frame_width, _ = video_frames[0].shape
    view_transformer = ViewTransformer((frame_height, frame_width))
    view_transformer.add_transformed_position_to_tracks(tracks)


    
    # Interpolate Ball Positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    
    # Speed and distance estimator
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    # Assign Player Teams using TeamAssigner
    team_assigner = TeamAssigner(device="cuda" if torch.cuda.is_available() else "cpu", video_path=video_path)

    # Ensure saved team assignments are loaded (avoid recomputation)
    team_assigner.load_team_assignments()

    for frame_num, player_track in enumerate(tracks['players']):
        player_ids = list(player_track.keys())
        player_bboxes = [player_track[pid]["bbox"] for pid in player_ids]

        # Extract and reduce features
        player_crops = team_assigner.extract_player_crops(video_frames[frame_num], player_bboxes, [1.0] * len(player_ids))
        features = team_assigner.extract_features(player_ids, player_crops)
        reduced_features = team_assigner.reduce_dimensionality(features)

        # Assign teams
        labels = team_assigner.assign_teams_by_track_id(player_ids, reduced_features, reassign=(frame_num % 30 == 0))

        for pid, label in zip(player_ids, labels):
            tracks['players'][frame_num][pid]['team'] = label  # ✅ Assign team normally

        # 🔹 Ensure every player has a valid 'team' entry
        if 'team' not in tracks['players'][frame_num][pid]:
            tracks['players'][frame_num][pid]['team'] = "Unknown"  # Default team assignment


    # Save assigned teams for future runs
    team_assigner.save_team_assignments()


    # Assign Ball to Players
    player_assigner = PlayerBallAssigner()
    team_ball_control = []

    for frame_num, player_track in enumerate(tracks['players']):
        # ✅ Safely get ball information
        ball_info = tracks['ball'][frame_num] if frame_num < len(tracks['ball']) else {}
        ball_bbox = ball_info.get(1, {}).get("bbox", None) if isinstance(ball_info, dict) else None

        if not ball_bbox:
            print(f"⚠️ Frame {frame_num}: Ball not detected, using last known team control.")
            last_team = team_ball_control[-1] if team_ball_control else "Unknown"
            team_ball_control.append(last_team)
            continue

        # Assign the ball to the closest player
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

        if assigned_player != -1:
            if assigned_player in tracks['players'][frame_num]:
                player_data = tracks['players'][frame_num][assigned_player]

                # ✅ Ensure a team is always assigned
                if 'team' not in player_data:
                    print(f"⚠️ Frame {frame_num}: Assigned player {assigned_player} has no team! Assigning default team.")
                    player_data['team'] = 0  # Default team to avoid UI errors

                # ✅ Assign ball possession
                player_data['has_ball'] = True
                team_ball_control.append(player_data['team'])
                print(f"✅ Frame {frame_num}: Player {assigned_player} has ball. Team: {player_data['team']}")
            else:
                print(f"⚠️ Frame {frame_num}: Assigned player {assigned_player} not found in tracking data!")
                last_team = team_ball_control[-1] if team_ball_control else "Unknown"
                team_ball_control.append(last_team)
        else:
            # Maintain previous team possession if no assignment is found
            last_team = team_ball_control[-1] if team_ball_control else "Unknown"
            team_ball_control.append(last_team)

    team_ball_control = np.array(team_ball_control)  # Convert to NumPy array



    
    # Draw Annotations
    output_video_frames = tracker.draw_annotations(video_frames, tracks,  team_ball_control)
    
    ## Draw Camera movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames,camera_movement_per_frame)
    
    ## Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames,tracks)



    # Debugging Information
    print(f"Input video frames: {len(video_frames)}")
    print(f"Output video frames: {len(output_video_frames)}")

    # Save Annotated Video
    output_video_path_avi = f"output_videos/outputVideo.avi"
    save_video(output_video_frames,output_video_path_avi)
    
    #output to fix browser format
    output_video_path_mp4 = f"output_videos/{video_name}.mp4"
    ffmpeg.input(output_video_path_avi).output(output_video_path_mp4,vcodec="libx264").run()
    print(f"saved video on dir:", output_video_path_mp4)

def generate_video_chunks(video_filename, start_byte=0, end_byte=None):
    counter = 0  

    with open(video_filename, "rb") as file_object:
        file_object.seek(start_byte)
        remaining_bytes = (end_byte - start_byte + 1) if end_byte else None

        while remaining_bytes is None or remaining_bytes > 0:
            chunk_size = min(CHUNK_SIZE, remaining_bytes) if remaining_bytes else CHUNK_SIZE
            chunk = file_object.read(chunk_size)

            if not chunk:
                print("End of file reached.")
                break  # Ensure we exit when file ends

            if remaining_bytes:
                remaining_bytes -= len(chunk)

            counter += 1
            print(f"Sending chunk #{counter}, size: {len(chunk)} bytes")

            yield chunk
        
    print("✅ Finished sending all chunks.") 
    
    

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    try:
        input_video_path = os.path.join(input_videos_dir, file.filename)
        with open(input_video_path, "wb") as f:
            f.write(await file.read())
        print(f"Video uploaded to: {input_video_path}")

        output_video_path = os.path.join(output_videos_dir, f"processed_{file.filename}")
        output_video_url = input_video_path
        
        try:
            process_video(input_video_path, output_video_path)
        except Exception as e:
            print(f"Error in background processing: {e}")

        return JSONResponse(
            content={
                "message": "Video uploaded and processed successfully",
                "video_url": f"{os.path.basename(output_video_url)}"
            },
            status_code=202
        )
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

   
@app.get("/output/{video_filename}")
async def stream_video(video_filename: str, request: Request):
    VIDEO_PATH = os.path.join(base_dir, "output_videos", video_filename)

    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404, detail="File not found")

    file_size = os.stat(VIDEO_PATH).st_size
    range_header = request.headers.get("Range")

    if range_header:
        byte_range = range_header.replace("bytes=", "").split("-")
        start_byte = int(byte_range[0])
        end_byte = int(byte_range[1]) if byte_range[1] else file_size - 1

        if start_byte >= file_size or end_byte >= file_size:
            raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

        headers = {
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
            "Content-Length": str(end_byte - start_byte + 1),
            "Content-Disposition": "inline",
            "Vary": "Range",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }

        print(f"📡 Streaming partial content: {start_byte} - {end_byte}")

        return StreamingResponse(
            content=generate_video_chunks(VIDEO_PATH, start_byte, end_byte),
            headers=headers,
            status_code=206
        )

    headers = {
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Disposition": "inline",
        "Vary": "Range",
    }

    print("📡 Streaming full video")

    return StreamingResponse(
        content=generate_video_chunks(VIDEO_PATH),
        headers=headers,
        status_code=200
    )

    
@app.get("/download/{video_filename}")
async def download_video(video_filename: str):
    video_path = os.path.join(output_videos_dir, video_filename)
    CHUNK_SIZE= 10 * 1024 * 1024
    
    if os.path.exists(video_path):
        async def iterfile():
            async with aiofiles.open(video_path, "rb") as file_like:
                while chunk := await file_like.read(CHUNK_SIZE):
                    yield chunk
        
        return StreamingResponse(iterfile(), 
                                 media_type="video/avi", 
                                 headers={"Content-Disposition": f"attachment; filename={video_filename}"})
    else:
        raise HTTPException(status_code=404, detail="Video not found")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,timeout_keep_alive=300, )
