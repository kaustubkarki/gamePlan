const timelineData = [
  {
    id: 1,
    label: "Open CV",
    className: "steps",
    date: "Video Reader",
    description: "Video Reading & Preparation",
    points: [
      "Reads the input video ('any.mp4') into frames.",
      "Generates a unique stub path for saving/loading tracking data.",
    ],
  },
  {
    id: 2,
    label: "ByteTrack & Optical flow",
    className: "steps",
    date: "Trackers",
    description: "Object tracking and camera movement estimation",
    points: [
      "Initializes a Tracker with a pre-trained model ('models/best.pt').",
      "Extracts object tracks for players, ball, and other elements.",
      "Adds positional data to tracked objects.",
      "Initializes CameraMovementEstimator with the first frame.",
      "Estimates camera movement for each frame.",
      "Adjusts tracked object positions based on detected camera movement.",
    ],
  },
  {
    id: 3,
    label: "OpenCV",
    className: "steps",
    date: "Camera movements",
    description: "View Transformation and Ball Position Interpolation",
    points: [
      "Initializes ViewTransformer with video frame dimensions.",
      "Applies perspective transformation to ensure positional consistency.",
      "Interpolates missing ball positions to ensure smooth tracking.",
    ],
  },
  {
    id: 4,
    label: "Open CV",
    className: "steps",
    date: "Individual tracks",
    description: "Speed & Distance Estimation",
    points: [
      "Initializes SpeedAndDistance_Estimator.",
      "Calculates speed and distance for tracked players and the ball.",
    ],
  },
  {
    id: 5,
    label: "K-means Algorithm",
    className: "steps",
    date: "Team play",
    description: "Team Assignment and Ball Possession",
    points: [
      "Initializes TeamAssigner with CUDA if available.",
      "Loads previously saved team assignments to avoid recomputation.",
      "Extracts player crops and reduces feature dimensionality.",
      "Assigns teams to players based on extracted features.",
      "Saves team assignments for future runs.",
      "Initializes PlayerBallAssigner.",
      "Checks ball presence in each frame.",
      "Assigns ball to the closest player if detected.",
      "Updates team ball control based on player assignment.",
    ],
  },
  {
    id: 6,
    label: "OpenCV",
    className: "steps",
    date: "Visualization",
    description: "Drawing Annotations ",
    points: [
      "Draws bounding boxes, team colors, and ball possession indicators.",
      "Overlays camera movement visualization.",
      "Displays speed and distance annotations for players.",
    ],
  },
  {
    id: 7,
    label: "Fast API",
    className: "steps",
    date: "Output",
    description: "Saving output and displaying the video",
    points: [
      "Prints debug info on input vs. output frames.",
      "Saves the final annotated video as 'output_videos/output.avi'.",
    ],
  },
];

export default timelineData;
