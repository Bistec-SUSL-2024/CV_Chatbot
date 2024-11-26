from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main_backend_model import rank_cvs_by_description, query_cv_by_id, start_chatbot_with_cv

app = FastAPI()


session_storage = {}

class JobDescription(BaseModel):
    description: str

class StartChatbotRequest(BaseModel):
    cv_id: str

class AskQuestionRequest(BaseModel):
    question: str


# active_sessions = {}

@app.post("/rank_cvs")
def rank_cvs(job_description: JobDescription):
    try:
        ranked_cvs = rank_cvs_by_description(job_description.description)
        return {"ranked_cvs": ranked_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_cv")
async def query_cv_by_id(cv_id: str):
    # Store cv_id in the session
    session_storage["cv_id"] = cv_id
    return {"message": f"CV {cv_id} has been selected."}

@app.post("/ask")
async def start_chatbot_with_cv(request: AskQuestionRequest):
    # Retrieve cv_id from session storage
    cv_id = session_storage.get("cv_id")
    if not cv_id:
        raise HTTPException(status_code=400, detail="CV not selected. Please start by providing a cv_id.")
    
    # Process the question and return an answer (this can be a real lookup or analysis)
    question = request.question
    answer = get_answer_for_question(cv_id, question)
    return {"answer": answer}

@app.post("/exit")
async def exit():
    # Clear the stored cv_id when done
    session_storage.pop("cv_id", None)
    return {"message": "Session ended."}

def get_answer_for_question(cv_id: str, question: str):
    # Add logic to process the question based on the cv_id, e.g., searching the CV data
    return f"This is the answer to your question about CV {cv_id}: {question}"
