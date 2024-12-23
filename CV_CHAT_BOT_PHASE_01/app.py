from flask import Flask, request, jsonify
from analyzer_model import query_cv, rebuild_index

app = Flask(__name__)

@app.route('/api/data_handle', methods=['POST'])
def handle_prompt():
    data = request.json
    file_path = data.get('file_path')
    prompt = data.get('prompt')

    if not file_path:
        return jsonify({"message": "File path is missing, using default path."}), 400
    
    if not prompt:
        return jsonify({"message": "Prompt is missing, using default prompt."}), 400

    # Rebuild index if new file uploaded
    rebuild_index()  # Rebuild or reload index from 'data' directory

    response_message = query_cv(file_path, prompt)
    return jsonify({"message": response_message})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
