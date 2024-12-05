from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main_backend_model import rank_cvs_by_description, query_cv_by_id, start_chatbot_with_cv, show_cv



app = FastAPI()

class JobDescription(BaseModel):
    description: str

class CVQuery(BaseModel):
    cv_id: str

class ChatbotRequest(BaseModel):
    cv_id: str
    question: str

class ShowCVRequest(BaseModel):
    cv_id: str

@app.post("/rank_cvs")
def rank_cvs(job_description: JobDescription):
    try:
        ranked_cvs = rank_cvs_by_description(job_description.description)
        return {"ranked_cvs": ranked_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/query_cv")
def query_cv(cv_query: CVQuery):
    try:
        print(f"Received CV ID: {cv_query.cv_id}")  # Log the received CV ID for debugging
        
        cv_text = query_cv_by_id(cv_query.cv_id)
        if cv_text:
            return {"cv_id": cv_query.cv_id, "cv_text": cv_text}
        else:
            raise HTTPException(status_code=404, detail="CV not found")
    except Exception as e:
        print(f"Error in query_cv: {str(e)}")  # Log any errors for debugging
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/chatbot")
def chatbot(query: ChatbotRequest):
    
    try:
        response = start_chatbot_with_cv(query.cv_id, query.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/show_cv")
def handle_show_cv(request: ShowCVRequest):
    try:
        result = show_cv(request.cv_id)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(status_code=404, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error showing CV: {str(e)}")