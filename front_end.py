import streamlit as st 
import requests
import os

DATA_DIR = './data'

def save_uploaded_file(uploaded_file):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Corrected: Ensure we access the file name attribute of the UploadedFile object
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

st.markdown(
     """
    <style>
        /* Chat message styling */
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
            width: 160%;  /* Adjusted from 200% */
            max-width: 1600px;  /* Increased width */
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
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

st.title("CV Analysis Chatbot - Phase_01")

# Sidebar for CV upload
with st.sidebar:
    st.write("#### Upload Your CVs")
    
    # Allow multiple file uploads
    uploaded_files = st.file_uploader("#### Upload CVs (PDF)", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed", key="upfile")

    # Submit button
    if st.button("Submit CVs", key="sub"):
        if uploaded_files:
            file_paths = []
            
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                # Only call save_uploaded_file if uploaded_file is not None
                file_path = save_uploaded_file(uploaded_file)
                file_paths.append(file_path)
            
            # Save all file paths to session state
            st.session_state.file_paths = file_paths
            st.success("All CVs submitted successfully!")
        else:
            st.warning("Please upload at least one CV.")

# Main Section for Chatbot Responses
st.write("### Chatbot Responses:")
st.markdown("<div class='main-container'>", unsafe_allow_html=True)

# Display chat history
if st.session_state.messages:
    for message in st.session_state.messages:
        st.markdown(message, unsafe_allow_html=True)

# Closing the main container div
st.markdown("</div>", unsafe_allow_html=True)

# Form for question input at the bottom
with st.form(key='question_form'):
    st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
    prompt = st.text_input(label="ask", label_visibility="collapsed", placeholder="Enter your question....", key="prompt")
    
    # Arrange Ask and Clear Chat buttons side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        clear_chat_button = st.form_submit_button(label="Clear Chat", on_click=lambda: st.session_state.messages.clear(), use_container_width=True)
    with col2:
        submit_button = st.form_submit_button(label="Ask", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Handle form submission
if submit_button and prompt:
    if 'file_paths' in st.session_state:  
        file_paths = st.session_state.file_paths
        response = requests.post("http://127.0.0.1:8000/api/data_handle", json={"file_paths": file_paths, "prompt": prompt})

        if response.status_code == 200:
            data = response.json()
            chatbot_response = data['message']

            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
        else:
            st.error("Error fetching response from backend.")
    else:
        st.warning("Please upload a CV before asking questions.")
