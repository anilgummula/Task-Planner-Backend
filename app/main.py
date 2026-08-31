from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, tasks, timer, dashboard, ai

app = FastAPI(title="AI Planner & Time Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://flowline-2050.netlify.app","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(timer.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}
