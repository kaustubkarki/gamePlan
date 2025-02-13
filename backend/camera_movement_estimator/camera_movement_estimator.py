import pickle
import cv2
import numpy as np
import os
import sys 
import gzip
import hashlib
sys.path.append('../')
from utils import measure_distance,measure_xy_distance
def hash_frame(frame):
        
    return hashlib.md5(frame.tobytes()).hexdigest()

class CameraMovementEstimator():
    def __init__(self,frame):
        self.minimum_distance = 5

        self.lk_params = dict(
            winSize = (15,15),
            maxLevel = 2,
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03)
        )

        first_frame_grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        mask_features = np.zeros_like(first_frame_grayscale)
        mask_features[:,0:20] = 1
        mask_features[:,900:1050] = 1

        self.features = dict(
            maxCorners = 100,
            qualityLevel = 0.3,
            minDistance =3,
            blockSize = 7,
            mask = mask_features
        )
    
    def add_adjust_positions_to_tracks(self, tracks, camera_movement_per_frame):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                if frame_num >= len(camera_movement_per_frame):
                    print(f"Frame {frame_num} exceeds camera_movement_per_frame length {len(camera_movement_per_frame)}. Skipping.")
                    continue

                for track_id, track_info in track.items():
                    position = track_info['position']
                    camera_movement = camera_movement_per_frame[frame_num]
                    position_adjusted = (position[0] - camera_movement[0], position[1] - camera_movement[1])
                    tracks[object][frame_num][track_id]['position_adjusted'] = position_adjusted



    def get_camera_movement(self, frames, read_from_stub=False, stub_path=None):
        if len(frames) == 0:
            raise ValueError("Frames list is empty. Cannot calculate camera movement.")
        data= None
        
        # Generate a hash of the first frame to identify different videos
        new_video_hash = hash_frame(frames[0])

        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with gzip.open(stub_path, 'rb') as f:
                data= pickle.load(f)
                
        if data and isinstance(data, dict) and "camera_movement" in data and "video_hash" in data:
            if data["video_hash"] == new_video_hash and len(data["camera_movement"]) == len(frames):
                print(f"Loaded camera movement from stub: {stub_path} (compressed)")
                return data["camera_movement"]
            else:
                print("Stub does not match current video. Regenerating stubs.")

        camera_movement = [[0, 0] for _ in range(len(frames))]  # Correct initialization

        old_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        old_features = cv2.goodFeaturesToTrack(old_gray, **self.features)

        for frame_num in range(1, len(frames)):
            frame_gray = cv2.cvtColor(frames[frame_num], cv2.COLOR_BGR2GRAY)
            if old_features is None or len(old_features) == 0:
                print(f"No features detected in frame {frame_num}. Skipping.")
                old_features = cv2.goodFeaturesToTrack(frame_gray, **self.features)
                old_gray = frame_gray.copy()
                continue

            new_features,status, _ = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, old_features, None, **self.lk_params)
            if new_features is None or status is None or len(status) == 0:
                print(f"Optical flow failed in frame {frame_num}, skipping.")
                continue
            
            max_distance = 0
            camera_movement_x, camera_movement_y = 0, 0

            for i, (new, old) in enumerate(zip(new_features, old_features)):
                new_features_point = new.ravel()
                old_features_point = old.ravel()

                distance = measure_distance(new_features_point, old_features_point)
                if distance > max_distance:
                    max_distance = distance
                    camera_movement_x, camera_movement_y = measure_xy_distance(old_features_point, new_features_point)

            if max_distance > self.minimum_distance:
                camera_movement[frame_num] = [camera_movement_x, camera_movement_y]
                old_features = cv2.goodFeaturesToTrack(frame_gray, **self.features)

            old_gray = frame_gray.copy()

        if stub_path is not None:
            with gzip.open(stub_path, 'wb') as f:
                pickle.dump({"camera_movement": camera_movement, "video_hash": new_video_hash}, f)
            print(f"Saved new camera movement to stub: {stub_path} (compressed)")

        return camera_movement

    
    def draw_camera_movement(self, frames, camera_movement_per_frame):
        """Draws camera movement information at the bottom-left of the screen."""
    
        output_frames = []
    
        for frame_num, frame in enumerate(frames):
            frame = frame.copy()
        
            # Get frame dimensions
            frame_height, frame_width, _ = frame.shape

            # Position at bottom-left
            text_x = 10
            text_y = frame_height - 50  # Move text 50px above bottom
            box_start = (0, frame_height - 100)  # Background rectangle start
            box_end = (300, frame_height)  # Background rectangle end

            # Draw semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, box_start, box_end, (255, 255, 255), -1)
            alpha = 0.6
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Get camera movement values
            x_movement, y_movement = camera_movement_per_frame[frame_num]

            # Draw text
            frame = cv2.putText(frame, f"Camera Movement X: {x_movement:.2f}", 
                            (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            frame = cv2.putText(frame, f"Camera Movement Y: {y_movement:.2f}", 
                            (text_x, text_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            output_frames.append(frame)

        return output_frames
