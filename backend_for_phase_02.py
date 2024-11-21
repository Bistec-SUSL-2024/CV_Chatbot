from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main_backend_model import rank_cvs_by_description, query_cv_by_id, start_chatbot_with_cv

app = FastAPI()

class JobDescription(BaseModel):
    description: str

class Query(BaseModel):
    cv_id: str

class ChatBotRequest(BaseModel):
    cv_id: str
    question: str

@app.post("/rank_cvs")
def rank_cvs(job_description: JobDescription):
    try:
        ranked_cvs = rank_cvs_by_description(job_description.description)
        return {"ranked_cvs": ranked_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def ask_query(query: Query):
    try:
        response = query_cv_by_id(query.cv_id)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_chatbot")
def start_chatbot(chatbot_request: ChatBotRequest):
    try:
        chatbot_session = start_chatbot_with_cv(chatbot_request.cv_id)
        return {"message": f"Chatbot started for CV {chatbot_request.cv_id}", "session": chatbot_session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
