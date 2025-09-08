from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app import model, db
from app.schemas import FeedbackIn
from typing import Dict

app = FastAPI(title="AI Teaching Evaluation Prototype")

origins = [
    "https://fabulous-sundae-25a41e.netlify.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.init_db()

@app.post("/feedback", response_model=Dict)
def submit_feedback(payload: FeedbackIn):
    text = payload.text
    analysis = model.analyze_text(text)
    fid = db.insert_feedback(payload.session_id, payload.teacher_id, payload.student_id, text, analysis)
    return {"id": fid, "analysis": analysis}

@app.post("/analyze", response_model=Dict)
def analyze(payload: FeedbackIn):
    analysis = model.analyze_text(payload.text)
    return {"analysis": analysis}

@app.get("/feedback/{fid}", response_model=Dict)
def get_feedback(fid: int):
    rec = db.get_feedback(fid)
    if not rec:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return rec

@app.get("/reports/session/{session_id}", response_model=Dict)
def session_report(session_id: str):
    r = db.get_session_analytics(session_id)
    return r
