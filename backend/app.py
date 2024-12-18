from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from main_backend_model import (
    rank_cvs_by_description,
    query_cv_by_id,
    start_chatbot_with_cv,
    show_cv,
)

app = FastAPI()

# Request models
class JobDescription(BaseModel):
    description: str

class CVQuery(BaseModel):
    cv_id: str

class ChatbotRequest(BaseModel):
    cv_id: str
    question: str

class ShowCVRequest(BaseModel):
    cv_id: str

# Endpoints
@app.post("/rank_cvs")
async def rank_cvs(job_description: JobDescription):
    """
    Ranks CVs based on the job description provided.
    """
    try:
        ranked_cvs = rank_cvs_by_description(job_description.description)
        return {"ranked_cvs": ranked_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_cv")
async def query_cv(cv_query: CVQuery):
    """
    Retrieves a CV's content by its ID.
    """
    try:
        cv_text = query_cv_by_id(cv_query.cv_id)
        if cv_text:
            return {"cv_id": cv_query.cv_id, "cv_text": cv_text}
        else:
            raise HTTPException(status_code=404, detail="CV not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chatbot")
async def chatbot(query: ChatbotRequest):
    """
    Starts a chatbot session with a specific CV and answers a user's question.
    """
    try:
        response = start_chatbot_with_cv(query.cv_id, query.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/show_cv")
async def handle_show_cv(request: ShowCVRequest):
    """
    Fetches metadata or a preview for a CV by its ID.
    """
    try:
        result = show_cv(request.cv_id)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(status_code=404, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error showing CV: {str(e)}")

# Run application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
