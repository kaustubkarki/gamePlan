
import numpy as np
import cv2

class ViewTransformer:
    def __init__(self, image_size):
        # Field dimensions in meters
        court_width = 68  # Width of the football field
        court_length = 105  # Length of the football field

        # Image dimensions
        height, width = image_size

        # Dynamically define the polygon vertices for perspective transformation
        self.pixel_vertices = np.array([
            [int(0.05 * width), height],       # Bottom-left
            [int(0.25 * width), int(0.1 * height)],  # Top-left
            [int(0.75 * width), int(0.1 * height)],  # Top-right
            [int(0.95 * width), height]        # Bottom-right
        ]).astype(np.float32)

        # Define target vertices (transformed points)
        self.target_vertices = np.array([
            [0, court_width],
            [0, 0],
            [court_length, 0],
            [court_length, court_width]
        ]).astype(np.float32)

        # Get perspective transformation matrix
        self.perspective_transformer = cv2.getPerspectiveTransform(self.pixel_vertices, self.target_vertices)

    def transform_point(self, point):
        """Transform a single point using the perspective transform matrix."""
        reshaped_point = np.array(point).reshape(-1, 1, 2).astype(np.float32)
        transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer)
        return transformed_point.reshape(-1, 2)

    def add_transformed_position_to_tracks(self, tracks):
        """Add transformed positions to each track."""
        for object_name, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info.get('position_adjusted', None)
                    if position is not None:
                        position = np.array(position)
                        transformed_position = self.transform_point(position)
                        if transformed_position is not None:
                            transformed_position = transformed_position.squeeze().tolist()
                        tracks[object_name][frame_num][track_id]['position_transformed'] = transformed_position

    def draw_transformation_polygon(self, frame):
        """Draw the transformation polygon on a given frame for debugging."""
        for i in range(4):
            start = tuple(self.pixel_vertices[i])
            end = tuple(self.pixel_vertices[(i + 1) % 4])
            cv2.line(frame, start, end, (0, 255, 0), 2)
        return frame
