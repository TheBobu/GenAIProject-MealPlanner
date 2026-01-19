import json
from pathlib import Path
from crewai import Crew
from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
import uuid
from src.mealplannercrew.crew import Mealplannercrew
import os 

DB_PATH = Path("./knowledge/user_db.json")
def init_db():
    if not DB_PATH.exists():
        with open(DB_PATH, "w") as f:
            json.dump({}, f)
            f.flush()
        print("Initialized empty user database via lifespan.", flush=True)
    else:
        print(f"Path exists already: {DB_PATH}", flush=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup")
    # --- STARTUP LOGIC ---
    init_db()
    # init crew
    app.state.mealplannercrew = Mealplannercrew().crew()
    
    yield  # The app runs while it's here
    
    # --- SHUTDOWN LOGIC ---
    print("Application is shutting down. Database is preserved.", flush=True)
    
app = FastAPI(title="Meal Planner API", lifespan=lifespan)
results_db = {}

class UserProfile(BaseModel):
    username:str
    dietary_preferences: str
    allergies: str
    age: Optional[int]
    height: Optional[str]
    weight: Optional[str]
    gender: Optional[str]
    activity_level: Optional[str] = 'Light'
    nutritional_goals: Optional[str]



def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


def run_crew_logic(task_id: str, inputs: dict):
    """Background task to run the Crew without blocking the API."""
    username:str = inputs["username"]
    try:
        result = app.state.mealplannercrew.kickoff(inputs=inputs)
        results_db[username][task_id] = {"status": "completed", "result": str(result)}
    except Exception as e:
        results_db[username][task_id] = {"status": "failed", "error": str(e)}
    



@app.post("/users/profile")
async def save_profile(profile: UserProfile):
    db = load_db()
    db[profile.username] = profile.model_dump()
    save_db(db)
    results_db[profile.username] = {}
    return {"status": "success", "message": f"Profile for {profile.username} saved."}

@app.post("/generate-plan")
async def generate_plan(username: str, prompt:str, background_tasks: BackgroundTasks):
    db = load_db()
    user = db.get(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please add a user and its preferences first.")
    
    if not results_db.get(username):
        results_db[username] = {}
    
    task_id = str(uuid.uuid4())
    results_db[username][task_id] = {"status": "pending"}
    
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
    background_tasks.add_task(run_crew_logic, task_id, inputs)
    
    return {"task_id": task_id, "message": "Meal plan generation started"}

@app.get("/status/{username}")
async def get_status(username: str):
    return results_db.get(username, {"status": "not_found"})

@app.get("/users")
async def get_users():
    users = load_db()
    return users