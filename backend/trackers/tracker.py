
from ultralytics import YOLO
import supervision as sv
import pandas as pd
import pickle
import os
import cv2
import numpy as np
import gzip
import torch
from utils import get_bbox_width, get_center_of_bbox,get_foot_position


class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.optical_flow_tracker = {}  # Store previous player positions
        self.team_colors = {0: (0, 255, 0), 1: (0, 0, 255)} # Team 1: Green, Team 2: Red
        self.ball_positions = [] 
    
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

    def detect_frames(self, frames):
        batch_size = 20
        detections = []
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        for i in range(0, len(frames), batch_size):
            print(f"Processing batch {i // batch_size + 1}/{len(frames) // batch_size + 1}")
            detections_batch = self.model.predict(frames[i:i+batch_size], conf=0.3, device=device, verbose=False)
            detections += detections_batch
        return detections

    def track_with_optical_flow(self, prev_frame, curr_frame, tracks):
        """Use Optical Flow to improve tracking across frames."""
        if prev_frame is None:
            print("⚠️ No previous frame, skipping Optical Flow tracking.")
            return

        gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray_curr = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        lost_players = []

        for player_id, player_data in tracks["players"][-1].items():  # Last frame players
            bbox = player_data["bbox"]
            x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

            if player_id in self.optical_flow_tracker:
                prev_pos = np.float32([[self.optical_flow_tracker[player_id]]])
                new_pos, status, _ = cv2.calcOpticalFlowPyrLK(gray_prev, gray_curr, prev_pos, None)

                if status[0][0] == 1:  # Successfully tracked
                    new_x, new_y = new_pos[0][0]
                    self.optical_flow_tracker[player_id] = (new_x, new_y)
                    print(f"🔄 Optical Flow Updated Player {player_id}: {new_x}, {new_y}")
                else:
                    print(f"❌ Lost tracking for player {player_id}. Marking for reassignment.")
                    lost_players.append(player_id)

            else:
                self.optical_flow_tracker[player_id] = (x + w // 2, y + h // 2)
                print(f"🎯 Initialized Optical Flow Tracking for Player {player_id}: {self.optical_flow_tracker[player_id]}")

        for lost_player in lost_players:
            if lost_player in self.optical_flow_tracker:
                print(f"🔄 Keeping previous tracking for lost player {lost_player}")
            else:
                print(f"⚠️ Lost player {lost_player} was never assigned a position, defaulting to None.")
                self.optical_flow_tracker[lost_player] = None  # Mark as lost

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with gzip.open(stub_path, 'rb') as f:
                data = pickle.load(f)
            if data.get("metadata", {}).get("frame_count") == len(frames):
                print(f"Loaded tracks from stub: {stub_path} (compressed)")
                return data["tracks"]

        detections = self.detect_frames(frames)
        tracks = {"players": [], "referees": [], "ball": []}

        prev_frame = None

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {v: k for k, v in cls_names.items()}
            detection_supervision = sv.Detections.from_ultralytics(detection)

            for object_ind, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)
            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                position = [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]

                if cls_id == cls_names_inv['player']:
                    tracks["players"][frame_num][track_id] = {"bbox": bbox, "position": position}

                if cls_id == cls_names_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox, "position": position}

            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv['ball']:
                    tracks["ball"][frame_num][1] = {"bbox": bbox, "position": position}

            # Apply Optical Flow Tracking for this frame
            if prev_frame is not None:
                self.track_with_optical_flow(prev_frame, frames[frame_num], tracks)

            prev_frame = frames[frame_num]

        if stub_path:
            with gzip.open(stub_path, 'wb') as f:
                pickle.dump({"tracks": tracks, "metadata": {"frame_count": len(frames)}}, f)
                print(f"Saved new tracks to stub: {stub_path} (compressed)")

        return tracks
    
    def draw_team_ball_control(self, frame, frame_num, team_ball_control, team_colors):
        """Draw a bar showing ball possession percentage at the top of the screen."""
    
        # Ensure team_ball_control is a NumPy array
        team_ball_control = np.array(team_ball_control)

        # Compute ball control statistics up to the current frame
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]

        # ✅ Filter out "Unknown" values for accurate possession stats
        valid_control = team_ball_control_till_frame[team_ball_control_till_frame != "Unknown"]

        if len(valid_control) == 0:
            # print(f"⚠️ Frame {frame_num}: No valid ball control data!")
            return frame  # Skip drawing if no valid data

        team_1_num_frames = np.sum(valid_control == 0)  # Team 0
        team_2_num_frames = np.sum(valid_control == 1)  # Team 1

        total_frames = len(valid_control)

        if total_frames > 0:
            team_1_possession = team_1_num_frames / total_frames
            team_2_possession = team_2_num_frames / total_frames
        else:
            team_1_possession, team_2_possession = 0.5, 0.5  # Default 50-50 if no valid data

        

        # Draw UI at the top of the screen
        bar_height = 40
        frame_width = frame.shape[1]

        # ✅ Default colors for missing teams
        team_1_color = tuple(int(c) for c in team_colors.get(0, (0, 0, 255)))  # Red
        team_2_color = tuple(int(c) for c in team_colors.get(1, (0, 255, 0)))  # Green

        # Compute bar widths
        team_1_width = int(team_1_possession * frame_width)
        team_2_width = frame_width - team_1_width

        # Draw rectangles
        cv2.rectangle(frame, (0, 0), (team_1_width, bar_height), team_1_color, -1)
        cv2.rectangle(frame, (team_1_width, 0), (frame_width, bar_height), team_2_color, -1)

        # Add text percentages
        cv2.putText(frame, f"{team_1_possession * 100:.0f}%", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"{team_2_possession * 100:.0f}%", (frame_width - 100, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return frame






    # def draw_annotations(self, video_frames, tracks, team_ball_control):
    #     """Draw team-colored ellipses and track IDs on players."""
    #     output_video_frames = []

    #     for frame_num, frame in enumerate(video_frames):
    #         frame = frame.copy()
    #         player_dict = tracks["players"][frame_num]
    #         ball_dict = tracks["ball"][frame_num]
    #         referee_dict = tracks["referees"][frame_num]

    #         for track_id, player in player_dict.items():
    #             bbox = player["bbox"]
    #             team = player.get("team", -1)
    #             color = self.team_colors.get(team, (0, 0, 255))  # Default Red if missing

    #             # Draw ellipse around player
    #             frame = self.draw_ellipse(frame, bbox, color, track_id)
    #             # Draw ball possession indicator (triangle)
    #             if player.get("has_ball", False):
    #                 frame = self.draw_traingle(frame, bbox, (0, 255, 0))  # Yellow for ball possession
                
    #         for _, referee in referee_dict.items():
    #             frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255))

    #         for track_id, ball in ball_dict.items():
    #             frame = self.draw_traingle(frame, ball["bbox"], (0, 255, 0))
                
    #         # ✅ Pass `team_colors` when calling `draw_team_ball_control()`
    #         frame = self.draw_team_ball_control(frame, frame_num, team_ball_control, self.team_colors)

    #         output_video_frames.append(frame)

    #     return output_video_frames
    
    
    # def draw_traingle(self,frame,bbox,color):
    #     y= int(bbox[1])
    #     x,_ = get_center_of_bbox(bbox)

    #     triangle_points = np.array([
    #         [x,y],
    #         [x-10,y-20],
    #         [x+10,y-20],
    #     ])
    #     cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED)
    #     cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2)
        
    #     return frame
    
    
    
    def draw_annotations(self, video_frames, tracks, team_ball_control):
        """Draw team-colored ellipses, track IDs on players, and visualize ball trajectory."""
        output_video_frames = []
        self.ball_positions = []  # Store ball positions over frames

        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()
            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Track ball trajectory
            if 1 in ball_dict:
                bbox = ball_dict[1]["bbox"]
                center_x, center_y = get_center_of_bbox(bbox)
                self.ball_positions.append((center_x, center_y))

            # Draw previous ball positions as a fading trajectory
            for i, (x, y) in enumerate(self.ball_positions[-15:]):  # Keep last 15 positions
                cv2.circle(frame, (int(x), int(y)), 3, (0, 165, 255), -1)  # Orange trail

            for track_id, player in player_dict.items():
                bbox = player["bbox"]
                team = player.get("team", -1)
                color = self.team_colors.get(team, (0, 0, 255))  # Default Red if missing
                frame = self.draw_ellipse(frame, bbox, color, track_id)

                # Draw ball possession indicator (triangle)
                if player.get("has_ball", False):
                    frame = self.draw_triangle(frame, bbox, (0, 255, 0))  # Green for ball possession
                
            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255))

            for track_id, ball in ball_dict.items():
                frame = self.draw_triangle(frame, ball["bbox"], (0, 255, 0))
                
            # ✅ Pass `team_colors` when calling `draw_team_ball_control()`
            frame = self.draw_team_ball_control(frame, frame_num, team_ball_control, self.team_colors)
            output_video_frames.append(frame)

        return output_video_frames
    
    def draw_triangle(self, frame, bbox, color, confidence=None):
        y = int(bbox[1])
        x, _ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x, y],
            [x - 10, y - 20],
            [x + 10, y - 20],
        ])
        cv2.drawContours(frame, [triangle_points], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points], 0, (0, 0, 0), 2)

        if confidence is not None:
            cv2.putText(frame, f"{confidence:.2f}", (x - 15, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return frame


    def draw_ellipse(self, frame, bbox, color, track_id=None):
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
