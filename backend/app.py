from flask import Flask, request, jsonify
from flask_cors import CORS
from backend_model import (
    retrieve_examples_and_instructions,
    refine_user_prompt_with_llm,
    extract_mandatory_conditions,
    rank_and_validate_cvs,
    query_cv_by_id
)

app = Flask(__name__)
CORS(app)  

# Endpoint to submit job description
@app.route("/submit-job-description", methods=["POST"])
def submit_job_description():
    data = request.get_json()
    user_input_job_description = data.get("job_description")

    if not user_input_job_description:
        return jsonify({"error": "Job description is required"}), 400

    try:
        examples, instructions = retrieve_examples_and_instructions(user_input_job_description)
        refined_job_description = refine_user_prompt_with_llm(user_input_job_description, examples, instructions)
        mandatory_conditions = extract_mandatory_conditions(refined_job_description)
        ranked_cvs = rank_and_validate_cvs(refined_job_description, mandatory_conditions)

        return jsonify({"refined_description": refined_job_description, "candidates": ranked_cvs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve a CV by ID
@app.route("/show-cv", methods=["POST"])
def show_cv():
    data = request.get_json()
    cv_id = data.get("cv_id")

    if not cv_id:
        return jsonify({"error": "CV ID is required"}), 400

    try:
        cv_text = query_cv_by_id(cv_id)
        return jsonify({"cv_text": cv_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New Endpoint: Chatbot communication
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    candidate_id = data.get("candidate_id")

    if not user_message or not candidate_id:
        return jsonify({"error": "Message and candidate ID are required"}), 400

    try:
        # Simulated bot response for now (replace with actual logic)
        bot_response = f"Received your message: '{user_message}' about candidate ID: {candidate_id}"
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New Endpoint: Clear chat messages
@app.route("/clear-chat", methods=["POST"])
def clear_chat():
    try:
        # Logic for clearing saved chat messages if required
        # Example placeholder response
        return jsonify({"message": "Chat cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
