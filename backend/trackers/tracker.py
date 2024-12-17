from ultralytics import YOLO
import supervision as sv
import pandas as pd
import pickle
import os
import sys
import cv2
import numpy as np
sys.path.append('../')
from utils import get_bbox_width,get_center_of_bbox,get_foot_position

class Tracker:
    def __init__(self,model_path):
        self.model=YOLO(model_path)
        self.tracker=sv.ByteTrack()
        
    def add_position_to_tracks(sekf,tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    bbox = track_info['bbox']
                    if object == 'ball':
                        position= get_center_of_bbox(bbox)
                    else:
                        position = get_foot_position(bbox)
                    tracks[object][frame_num][track_id]['position'] = position
    
    def interpolate_ball_positions(self, ball_positions):
        ball_positions = [x.get(1,{}).get('bbox',[]) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions,columns=['x1','y1','x2','y2'])

        # Interpolate missing values
        df_ball_positions = df_ball_positions.interpolate()
        df_ball_positions = df_ball_positions.bfill()

        ball_positions = [{1: {"bbox":x}} for x in df_ball_positions.to_numpy().tolist()]

        return ball_positions
        
    def detect_frames(self,frames):
        batch_size=20
        detections=[]
        for i in range(0, len(frames), batch_size):
            detections_batch=self.model.predict(frames[i:i+batch_size], conf=0.1)
            detections+=detections_batch
        return detections
        
    
    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        # Check if stub exists and validate it
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                data = pickle.load(f)
            # Validate metadata (e.g., frame count)
            if data.get("metadata", {}).get("frame_count") == len(frames):
                print(f"Loaded tracks from stub: {stub_path}")
                return data["tracks"]
            else:
                print("Stub file does not match the current video. Generating new tracks.")

        # Perform detection
        detections = self.detect_frames(frames)

        # Initialize tracks dictionary
        tracks = {
            "players": [],
            "referees": [],
            "ball": []
        }

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()}

            # Convert detections to supervision Detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            # Convert GoalKeeper to player object
            for object_ind, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            # Track Objects
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)
            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            # Process tracked detections
            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                # Calculate position as the center of the bounding box
                position = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]

                if cls_id == cls_names_inv['player']:
                    tracks["players"][frame_num][track_id] = {
                        "bbox": bbox,
                        "position": position
                }

                if cls_id == cls_names_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {
                        "bbox": bbox,
                        "position": position
                }

            # Process detections directly for the ball
            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv['ball']:
                    position = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
                    tracks["ball"][frame_num][1] = {
                        "bbox": bbox,
                        "position": position
                }

        # Save updated tracks to stub
        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump({
                    "tracks": tracks,
                    "metadata": {"frame_count": len(frames)}
            }, f)
            print(f"Saved new tracks to stub: {stub_path}")

        return tracks

    
    def draw_ellipse(self,frame, bbox, color, track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)
        
        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width), int(0.35*width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color = color,
            thickness=2,
            lineType=cv2.LINE_4
        )
        rectangle_width = 40
        rectangle_height=20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2- rectangle_height//2) +15
        y2_rect = (y2+ rectangle_height//2) +15

        if track_id is not None:
            cv2.rectangle(frame,
                            (int(x1_rect),int(y1_rect) ),
                            (int(x2_rect),int(y2_rect)),
                            color,
                            cv2.FILLED)
            
            x1_text = x1_rect+12
            if track_id > 99:
                x1_text -=10
            
            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text),int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )

        return frame
    def draw_traingle(self,frame,bbox,color):
        y= int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)
        
        return frame
    def draw_team_ball_control(self, frame, frame_num, team_ball_control):
        # Ensure team_ball_control is a NumPy array for proper slicing
        team_ball_control = np.array(team_ball_control)

        # Draw a semi-transparent rectangle
        overlay = frame.copy()
        alpha = 0.4
        box_start = (1350, 850)
        box_end = (1900, 970)
        cv2.rectangle(overlay, box_start, box_end, (255, 255, 255), -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Get ball control statistics up to the current frame
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]

        team_1_num_frames = np.sum(team_ball_control_till_frame == 1)
        team_2_num_frames = np.sum(team_ball_control_till_frame == 2)

        total_frames = team_1_num_frames + team_2_num_frames

        if total_frames > 0:
            team_1 = team_1_num_frames / total_frames
            team_2 = team_2_num_frames / total_frames
        else:
            team_1, team_2 = 0, 0  # Handle division by zero gracefully

        # Display the statistics
        text_position_1 = (1400, 900)
        text_position_2 = (1400, 950)
        text_scale = 1
        text_color = (0, 0, 0)
        text_thickness = 3

        cv2.putText(frame, f"Team 1 Ball Control: {team_1 * 100:.2f}%", text_position_1,
                cv2.FONT_HERSHEY_SIMPLEX, text_scale, text_color, text_thickness)
        cv2.putText(frame, f"Team 2 Ball Control: {team_2 * 100:.2f}%", text_position_2,
                cv2.FONT_HERSHEY_SIMPLEX, text_scale, text_color, text_thickness)

        return frame

    
    def draw_annotations(self,video_frames,tracks,team_ball_control):
        output_video_frames= []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Draw Players
            for track_id, player in player_dict.items():
                color=player.get("team_color", (0,0,255))
                frame =self.draw_ellipse(frame, player["bbox"], color, track_id)
                if player.get('has_ball',False):
                    frame = self.draw_traingle(frame, player["bbox"],(0,0,255))
                
            # Draw referees
            for _, referee in referee_dict.items():
                frame =self.draw_ellipse(frame, referee["bbox"], (0,255,255))
            # Draw ball 
            for track_id, ball in ball_dict.items():
                frame = self.draw_traingle(frame, ball["bbox"],(0,255,0))
                
            # Draw Team Ball Control
            frame = self.draw_team_ball_control(frame, frame_num, team_ball_control)
                
            output_video_frames.append(frame)
                
        # Ensure output frames match input frames
        assert len(output_video_frames) == len(video_frames), "Mismatch between input and output frames."
        return output_video_frames


