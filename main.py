# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth
from backend.routers import user

app = FastAPI(debug=True)

origins = [
    "http://localhost:5173",
    # Add more origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
