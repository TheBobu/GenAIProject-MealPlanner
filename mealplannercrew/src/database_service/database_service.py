from pathlib import Path
import sqlite3
from typing import Optional


class DatabaseService:
    """Service class for all database operations."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def init_db(self):
        """Initialize database tables."""
        if not self.db_path.exists():
            self.connect()
        else:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                dietary_preferences TEXT,
                allergies TEXT,
                age INTEGER,
                height TEXT,
                weight TEXT,
                gender TEXT,
                activity_level TEXT DEFAULT 'Light',
                nutritional_goals TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Results/Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                task_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                status TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        self.conn.commit()
        print("Database initialized successfully.", flush=True)
    
    def save_user_profile(self, username: str, profile_data: dict) -> bool:
        """Save or update user profile."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, dietary_preferences, allergies, age, height, weight, gender, activity_level, nutritional_goals)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    dietary_preferences=excluded.dietary_preferences,
                    allergies=excluded.allergies,
                    age=excluded.age,
                    height=excluded.height,
                    weight=excluded.weight,
                    gender=excluded.gender,
                    activity_level=excluded.activity_level,
                    nutritional_goals=excluded.nutritional_goals,
                    updated_at=CURRENT_TIMESTAMP
            """, (
                username,
                profile_data.get('dietary_preferences'),
                profile_data.get('allergies'),
                profile_data.get('age'),
                profile_data.get('height'),
                profile_data.get('weight'),
                profile_data.get('gender'),
                profile_data.get('activity_level', 'Light'),
                profile_data.get('nutritional_goals')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user profile: {e}", flush=True)
            return False
    
    def get_user(self, username: str) -> Optional[dict]:
        """Retrieve user profile by username."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_users(self) -> list:
        """Retrieve all users."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def save_task_result(self, task_id: str, username: str, status: str, result: Optional[str] = None, error: Optional[str] = None) -> bool:
        """Save or update task result."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO results (task_id, username, status, result, error)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    status=excluded.status,
                    result=excluded.result,
                    error=excluded.error,
                    updated_at=CURRENT_TIMESTAMP
            """, (task_id, username, status, result, error))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving task result: {e}", flush=True)
            return False
    
    def get_task_result(self, task_id: str) -> Optional[dict]:
        """Retrieve task result by task_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM results WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_tasks(self, username: str) -> list:
        """Retrieve all tasks for a user."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM results WHERE username = ? ORDER BY created_at DESC", (username,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]