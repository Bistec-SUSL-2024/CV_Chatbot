import streamlit as st
import requests
import os

DATA_DIR = './data'

def save_uploaded_file(uploaded_file):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


st.markdown(
    """
    <style>
        .user-message {
            background-color: #faeabe;
            color: black;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: left;
        }
        .bot-message {
            background-color: #fffaed;
            color: black;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: right;
        }
           /* Fixed position for input form at the bottom */
        .chat-input {
            position: fixed;
            bottom: 0;
            width: 200%;
            max-width: 1200px;
            background-color: #333;
            padding: 10px;
            margin: 0 auto;
            z-index: 999;
        }
        
        /* Increase the width of the input field */
        .chat-input input[type="text"] {
            width: 85%;
            margin-right: 10px;
        }
        
        /* Main container padding to prevent overlap with input form */
        .main-container {
            padding-bottom: 260px;
        }

        /* Sidebar Responsiveness */
        @media (max-width: 768px) {
            .css-1lcbmhc.e1fqkh3o1 { /* Class for Streamlit's sidebar */
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            .css-1lcbmhc.e1fqkh3o1:hover {
                transform: translateX(0);
            }
        }
        .chat-input {
    position: fixed;
    bottom: 0;
    width: 160%;  /* Changed from 200% */
    max-width: 1600px;  /* Increased from 1200px */
    background-color: #333;
    padding: 20px;  /* Increased padding */
    margin: 0 auto;
    z-index: 999;
    left: 50%;
    transform: translateX(-50%);  /* Center the chat input */
}

.chat-input input[type="text"] {
    width: 150%;  /* Increased from 85% */
    margin-right: 10px;
    padding: 12px;  /* Added padding */
    border-radius: 8px;  /* Added rounded corners */
}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state-----------------------------------------------
if 'messages' not in st.session_state:
    st.session_state.messages = []

def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

st.title("CV Analysis Chatbot - Phase_01")

# Sidebar for CV upload----------------------------------------------------
with st.sidebar:
    st.write("# Upload Your CV")
    uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"], label_visibility="collapsed",key="upfile")

    if st.button("Submit CV"):
        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            st.session_state.file_path = file_path  
            st.success("CV submitted successfully!")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Form for prompt input
    st.write("# Ask a Question")
    with st.form(key='question_form'):
        prompt = st.text_area("Ask your questions here:", placeholder="Enter your question....", key="prompt")
        submit_button = st.form_submit_button(label="Ask")

    if st.button("Clear Chat"):
        st.session_state.messages = []


st.write("### Chatbot Responses:")

# Handle form submission-------------------------------------------------------------
if submit_button and prompt:
    if 'file_path' in st.session_state:  
        file_path = st.session_state.file_path
        response = requests.post("http://127.0.0.1:8000/api/data_handle", json={"file_path": file_path, "prompt": prompt})

        if response.status_code == 200:
            data = response.json()
            chatbot_response = data['message']

            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
        else:
            st.error("Error fetching response from backend.")
    else:
        st.warning("Please upload a CV before asking questions.")

# Display chat history--------------------------------------------
if st.session_state.messages:
    for message in st.session_state.messages:
        st.markdown(message, unsafe_allow_html=True)
