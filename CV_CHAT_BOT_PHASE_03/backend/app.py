from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from model_for_phase_03 import (
    rank_and_validate_cvs,
    query_cv_by_id,
    start_chatbot_with_cv,
    show_cv,
    retrieve_examples_and_instructions,
    refine_user_prompt_with_llm,
    extract_mandatory_conditions
)
import os

app = FastAPI()

origins = [
    "http://localhost:3000",  # Allow frontend running on localhost (React app)
    # Add any other domains here if necessary
]

# app.mount("/static", StaticFiles(directory="./data"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows the specified domains
    allow_credentials=True,  # Allows cookies to be sent if needed
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers in the request
)


class JobDescription(BaseModel):
    description: str

class CVQuery(BaseModel):
    cv_id: str

class ChatbotRequest(BaseModel):
    cv_id: str
    question: str

class ShowCVRequest(BaseModel):
    cv_id: str


#-------------------------------------------------Rank CV Endpoint--------------------------------------------------

@app.post("/rank_cvs")
async def rank_cvs(job_description: JobDescription):
    """
    Ranks CVs based on the job description provided.
    """
    try:
        examples, instructions = retrieve_examples_and_instructions(job_description.description)
        refined_JD = refine_user_prompt_with_llm(job_description.description, examples, instructions)
        mandatory_conditions, keywords = extract_mandatory_conditions(refined_JD)
        ranked_cvs = rank_and_validate_cvs(refined_JD, mandatory_conditions, keywords)
        return {"ranked_cvs": ranked_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#-------------------------------------------------Query CV Endpoint-----------------------------------------------------------


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


#-------------------------------------------Chatbot Endpoint-----------------------------------------------


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


#-------------------------------------Show CV Endpoint--------------------------------------------


@app.post("/show_cv")
async def handle_show_cv(request: ShowCVRequest):
    """
    Fetches metadata or a preview for a CV by its ID.
    """
    try:
        # Assuming `show_cv` checks for file existence and returns a success message
        result = show_cv(request.cv_id)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(status_code=404, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error showing CV: {str(e)}")



#------------------------------------Main Section---------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
