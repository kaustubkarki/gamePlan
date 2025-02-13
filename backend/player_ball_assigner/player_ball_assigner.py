import sys 
sys.path.append('../')
from utils import get_center_of_bbox, measure_distance

class PlayerBallAssigner():
    def __init__(self):
        self.max_player_ball_distance = 150  # Adjusted for better assignment
    
    def assign_ball_to_player(self, players, ball_bbox):
        """Assign the ball to the closest player within a threshold distance."""
        if not players:
            return -1  # No players detected

        if not ball_bbox or len(ball_bbox) < 4:
            return -1  # Ball detection issue
        
        ball_position = get_center_of_bbox(ball_bbox)
        min_distance = float('inf')
        assigned_player = -1

        for player_id, player in players.items():
            player_bbox = player['bbox']
            player_center = get_center_of_bbox(player_bbox)

            distance = measure_distance(player_center, ball_position)

            if distance < self.max_player_ball_distance and distance < min_distance:
                min_distance = distance
                assigned_player = player_id
            
            if min_distance < 20:  # Stop early if player is very close to ball
                break

        return assigned_player  # Return the player ID assigned to the ball
