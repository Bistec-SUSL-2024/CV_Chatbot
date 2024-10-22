from flask import Flask, request, jsonify
from analyzer_model import query_cv  

app = Flask(__name__)

@app.route('/api/data_handle', methods=['POST'])

def handle_prompt():
    data = request.json
    file_path = data.get('file_path')
    prompt = data.get('prompt')

    
    response_message = query_cv(file_path, prompt)

    return jsonify({"message": response_message})

if __name__ == '__main__':
    app.run(port=8000, debug=True) 
