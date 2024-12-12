# Football Video Analysis SaaS

This project is a SaaS platform designed to analyze football videos using AI and machine learning. Users can upload videos, process them to track the ball, generate heatmaps, and gain actionable insights through a seamless web interface.

## Features

- **Video Upload and Processing**: Easily upload football videos for real-time or batch analysis.
- **Ball Tracking**: Leverage AI to track the ball's movement throughout the video.
- **Heatmap Generation**: Automatically create heatmaps to visualize player and ball activity.
- **FastAPI Backend**: High-performance API backend for handling video processing tasks.
- **React Frontend**: Interactive user interface for managing uploads and viewing analysis results.

---

## Tech Stack

### Backend

- **Language**: Python
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Key Libraries**:
  - [torch](https://pytorch.org/)
  - [ultralytics](https://github.com/ultralytics/ultralytics)
  - [python-opencv](https://opencv.org/)
  - [scikit-learn](https://scikit-learn.org/)
  - [Pillow](https://python-pillow.org/)
  - [skimage](https://scikit-image.org/)

### Frontend

- **Framework**: React 19
- **Styling**: TailwindCSS or your preferred CSS framework
- **API Communication**: Axios

---

## Setup Instructions

### Prerequisites

- **Python 3.8 or above**
- **Node.js 16.x or above**
- **pipenv** (for managing Python dependencies)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kaustubkarki/football-video-analysis.git
   cd football-video-analysis
   ```
2. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
3. Install dependencies:
   ```bash
   pipenv install
   ```
4. Run the FastAPI server:
   ```bash
   pipenv run uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
4. Access the frontend at `http://localhost:5173`.

---

## Usage

1. Start the backend and frontend servers as described above.
2. Use the React interface to upload a football video.
3. View the analysis results, including ball tracking and heatmaps, directly in the app.

---

## Folder Structure

```
football-video-analysis/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── models/           # Trained models for ball tracking
│   ├── utils/            # Utility scripts
│   └── ...
├── frontend/
│   ├── public/           # Static files
│   ├── src/              # React components and pages
│   └── ...
├── README.md
└── ...
```

---

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- Inspired by modern football analytics and AI-driven insights.
- Special thanks to the creators of FastAPI, React, and the libraries used.

---

## Contact

For questions or collaboration opportunities, please email [kaustubkarki@gmail.com].
