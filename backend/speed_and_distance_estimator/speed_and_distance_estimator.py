import cv2
import sys
import numpy as np

sys.path.append('../')
from utils import measure_distance, get_foot_position


class SpeedAndDistance_Estimator:
    def __init__(self):
        self.frame_window = 3  # Smaller window for accurate calculations
        self.frame_rate = 24

    def interpolate_missing_positions(self, object_tracks, track_id):
        """
        Interpolates missing positions for a specific track ID in object tracks.
        """
        # Ensure object_tracks exists and has valid frames
        if object_tracks is None or len(object_tracks) == 0:
            return

        # Create a list of positions (one per frame) for the given track_id
        positions = [None] * len(object_tracks)

        # Collect all positions for the track_id across frames
        for frame_num in range(len(object_tracks)):
            track = object_tracks[frame_num].get(track_id, None)
            if track and 'position_transformed' in track:
                positions[frame_num] = track['position_transformed']

        # Interpolate missing positions
        prev_position = None
        for i in range(len(positions)):
            if positions[i] is None and prev_position is not None:
                # Find the next valid position
                next_valid_index = next((j for j in range(i + 1, len(positions)) if positions[j] is not None), None)
                if next_valid_index:
                    # Linear interpolation
                    t = (i - positions.index(prev_position)) / (next_valid_index - positions.index(prev_position))
                    x = int(prev_position[0] + t * (positions[next_valid_index][0] - prev_position[0]))
                    y = int(prev_position[1] + t * (positions[next_valid_index][1] - prev_position[1]))
                    positions[i] = (x, y)
            elif positions[i] is not None:
                prev_position = positions[i]

        # Update object_tracks with interpolated positions
        for frame_num, position in enumerate(positions):
            if position is not None and track_id in object_tracks[frame_num]:
                object_tracks[frame_num][track_id]['position_transformed'] = position
    def add_speed_and_distance_to_tracks(self, tracks):
        total_distance = {}

        for object, object_tracks in tracks.items():
            if object in ["ball", "referees"]:
                continue  # Skip ball and referees

            # Interpolate missing positions for each track_id
            for frame_data in object_tracks:
                for track_id in frame_data.keys():
                    self.interpolate_missing_positions(object_tracks, track_id)

            number_of_frames = len(object_tracks)
            for frame_num in range(0, number_of_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, number_of_frames - 1)

                for track_id, _ in object_tracks[frame_num].items():
                    if track_id not in object_tracks[last_frame]:
                        continue

                    # Start and end positions
                    start_position = object_tracks[frame_num][track_id]['position_transformed']
                    end_position = object_tracks[last_frame][track_id]['position_transformed']

                    if start_position is None or end_position is None:
                        continue

                    # Measure distance
                    distance_covered = measure_distance(start_position, end_position)
                    time_elapsed = (last_frame - frame_num) / self.frame_rate
                    speed_m_per_sec = distance_covered / time_elapsed
                    speed_km_per_hr = speed_m_per_sec * 3.6

                    # Update total distance
                    if object not in total_distance:
                        total_distance[object] = {}
                    if track_id not in total_distance[object]:
                        total_distance[object][track_id] = 0

                    total_distance[object][track_id] += distance_covered

                    # Assign speed and distance to tracks
                    for frame_batch in range(frame_num, last_frame):
                        if track_id not in tracks[object][frame_batch]:
                            continue
                        tracks[object][frame_batch][track_id]['speed'] = speed_km_per_hr
                        tracks[object][frame_batch][track_id]['distance'] = total_distance[object][track_id]

    def draw_speed_and_distance(self, frames, tracks):
        output_frames = []
        for frame_num, frame in enumerate(frames):
            for object, object_tracks in tracks.items():
                if object in ["ball", "referees"]:
                    continue  # Skip ball and referees

                for _, track_info in object_tracks[frame_num].items():
                    speed = track_info.get('speed', None)
                    distance = track_info.get('distance', None)

                    if speed is None or distance is None:
                        continue

                    # Get bounding box and foot position
                    bbox = track_info['bbox']
                    position = get_foot_position(bbox)
                    position = list(position)
                    position[1] += 40  # Adjust position for text
                    position = tuple(map(int, position))

                    # Draw speed and distance
                    cv2.putText(frame, f"{speed:.2f} km/h", position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.putText(frame, f"{distance:.2f} m", (position[0], position[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            output_frames.append(frame)
        return output_frames


