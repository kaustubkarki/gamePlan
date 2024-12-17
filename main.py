import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import FileResponse, JSONResponse
import subprocess

from backend.routers import auth
from backend.routers import user

app = FastAPI(debug=True)

# CORS settings
origins = [
    "http://localhost:5173",
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(auth.router, prefix="/auth")

# Ensure the uploads directory exists
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)

# Upload video endpoint and trigger script
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Step 1: Save the uploaded file
        file_location = os.path.join(uploads_dir, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        print(f"Video uploaded successfully: {file_location}")

        # Step 2: Run the script.py with the uploaded video path
        script_path = os.path.join("backend", "script.py")

        # Run script.py using subprocess and pass video path as an argument
        process = subprocess.run(
            ["python", script_path, file_location],
            capture_output=True,
            text=True
        )

        # Step 3: Debug output of script execution
        print("Script Output:", process.stdout)
        print("Script Errors:", process.stderr)

        if process.returncode != 0:
            return JSONResponse(
                content={
                    "message": "Script execution failed",
                    "script_error": process.stderr
                },
                status_code=500
            )

        # Step 4: Return a success response and the video back to frontend
        return JSONResponse(
            content={
                "message": "Video uploaded and script executed successfully",
                "script_output": process.stdout,
                "video_url": f"/uploads/{file.filename}"
            },
            status_code=200
        )
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Serve video files statically from 'uploads' directory
@app.get("/uploads/{video_filename}")
async def get_uploaded_video(video_filename: str):
    video_path = os.path.join(uploads_dir, video_filename)
    if os.path.exists(video_path):
        return FileResponse(video_path)
    else:
        raise HTTPException(status_code=404, detail="Video not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
