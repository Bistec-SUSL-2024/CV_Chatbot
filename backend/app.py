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

#-----------------------------------Endpoint to submit job description-------------------------------------

@app.route("/submit-job-description", methods=["POST"])
def submit_job_description():
    data = request.get_json()
    user_input_job_description = data.get("job_description")

    if not user_input_job_description:
        return jsonify({"error": "Job description is required"}), 400

    try:
        # Step 1: Process job description
        examples, instructions = retrieve_examples_and_instructions(user_input_job_description)
        refined_job_description = refine_user_prompt_with_llm(user_input_job_description, examples, instructions)
        mandatory_conditions = extract_mandatory_conditions(refined_job_description)

        # Step 2: Rank CVs based on job description
        ranked_cvs = rank_and_validate_cvs(refined_job_description, mandatory_conditions)

        # Step 3: Format the ranked CVs for output
        ranked_cvs_output = [
            f"CV ID: {cv['id']}, Similarity Score: {cv['score']:.4f}"
            for cv in ranked_cvs
        ]
        formatted_response = {
            "top_ranked_cvs": f"Top ranked CVs based on refined job description:\n" + "\n".join(
                f"{idx + 1}. {entry}" for idx, entry in enumerate(ranked_cvs_output)
            ),
        }
        return jsonify(formatted_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#-------------------------------------------Endpoint to retrieve a CV by ID----------------------------------------

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

#-------------------------------------------New Endpoint: Chatbot communication-------------------------------------

@app.route("/ask-more-info", methods=["POST"])
def ask_more_info():
    data = request.get_json()
    cv_id = data.get("cv_id")
    user_message = data.get("message")

    if not cv_id or not user_message:
        return jsonify({"error": "CV ID and message are required"}), 400

    try:
        # Simulated chatbot initiation response (replace with actual logic)
        bot_response = f"Chat started for CV ID: {cv_id}. Received your message: '{user_message}'."
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#---------------------------------------New Endpoint: Clear chat messages---------------------------------------

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
