from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
import uuid
from src.database_service.database_service import DatabaseService
from src.mealplannercrew.crew import Mealplannercrew

DB_PATH = Path("./src/database_service/database/meal_planner.db")


def init_db_service():
    """Initialize database service."""
    db_service = DatabaseService(DB_PATH)
    db_service.init_db()
    return db_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup")
    # --- STARTUP LOGIC ---
    # init db
    app.state.db = init_db_service()
    # init crew
    app.state.mealplannercrew = Mealplannercrew().crew()

    yield

    # --- SHUTDOWN LOGIC ---
    print("Application is shutting down. Database is preserved.", flush=True)


app = FastAPI(title="Meal Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    username: str
    dietary_preferences: str
    allergies: str
    age: Optional[int]
    height: Optional[str]
    weight: Optional[str]
    gender: Optional[str]
    activity_level: Optional[str] = "Light"
    nutritional_goals: Optional[str]


def run_crew_logic(task_id: str, username: str, inputs: dict, crew):
    """Background task to run the Crew without blocking the API."""
    db_service = init_db_service()
    try:
        result = crew.kickoff(inputs=inputs)
        db_service.save_task_result(task_id, username, "completed", result=str(result))
    except Exception as e:
        db_service.save_task_result(task_id, username, "failed", error=str(e))

@app.post("/users/profile")
async def save_profile(profile: UserProfile):
    db = app.state.db
    success = db.save_user_profile(profile.username, profile.model_dump())

    if success:
        return {
            "status": "success",
            "message": f"Profile for {profile.username} saved.",
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save user profile.")


@app.post("/generate-plan")
async def generate_plan(username: str, prompt: str, background_tasks: BackgroundTasks):
    db = app.state.db
    user = db.get_user(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please add a user and its preferences first.")
    
    task_id = str(uuid.uuid4())
    db.save_task_result(task_id, username, "pending")
    
    user_profile = rf"""
    Username: {username}
    The user's body composition is: height = {user['height']}, weight = {user['weight']}, gender = {user['gender']}, activity level = {user['activity_level']}, age = {user['age']}
    The user has the following allergies: {user['allergies']}
    The user has the following dietary preferences: {user['dietary_preferences']}
    The user has the following nutritional goals: {user['nutritional_goals']}
    """
    
    inputs = {
        'username': username,
        'user_request': prompt,
        'user_profile': user_profile
    }
    
    # start crew in background
    background_tasks.add_task(run_crew_logic, task_id, username, inputs, app.state.mealplannercrew)
    
    return {"task_id": task_id, "message": "Meal plan generation started"}


@app.get("/status/{username}")
async def get_user_tasks_status(username: str):
    db = app.state.db
    tasks = db.get_user_tasks(username)
    return {"username": username, "tasks": tasks} if tasks else {"username": username, "tasks": []}


@app.get("/users")
async def get_users():
    db = app.state.db
    users = db.get_all_users()
    return users
