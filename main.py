from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List
from database import SessionLocal
from models import Profile
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()
# Add this after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development allow all, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
session_history = {}

class Message(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(request: Request, message: Message):
    user_ip = request.client.host
    current_time = datetime.now()

    # Clean up expired history
    session_history[user_ip] = [
        (msg, ts) for msg, ts in session_history.get(user_ip, [])
        if current_time - ts < timedelta(hours=1)
    ]

    # Save current message
    session_history.setdefault(user_ip, []).append((message.message, current_time))

    # Smart response engine
    response = generate_smart_response(message.message)
    
    # Save bot response too
    session_history[user_ip].append((response, current_time))

    return {"response": response}

def generate_smart_response(user_input: str) -> str:
    db = SessionLocal()
    user_input = user_input.lower()

    # Respond to greeting
    if re.search(r"\bhello\b|\bhi\b|\bhey\b", user_input):
        return "Hey there! 👋 Ask me about skills, latest projects, or experience."

    # Skills
    elif "skill" in user_input or "skills" in user_input:
        profiles = db.query(Profile).all()
        skills = ", ".join(set(p.skill for p in profiles))
        return f"Here are some of the skills we have: {skills}."

    # Latest project (assumed to be the last entry)
    elif "latest project" in user_input:
        latest = db.query(Profile).order_by(Profile.id.desc()).first()
        if latest:
            return f"{latest.name}'s latest project involves {latest.skill}."
        return "No project data found."

    # Experience
    elif "experience" in user_input:
        profiles = db.query(Profile).all()
        exp_info = ". ".join(f"{p.name} has {p.years_of_experience} years of experience in {p.skill}" for p in profiles)
        return exp_info or "No experience data available."

    # Show help
    elif "help" in user_input or "what can you do" in user_input:
        return "Try asking: 'What is the latest project?', 'Show me the skills', or 'Tell me about experience'."

    # Default fallback
    else:
        return "I'm not sure how to help with that 🤖. Try asking about latest project, skills, or experience."
@app.get("/history")
def get_history(request: Request):
    user_ip = request.client.host
    history = session_history.get(user_ip, [])
    return {"history": [{"message": msg, "timestamp": ts.isoformat()} for msg, ts in history]}
