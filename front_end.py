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

# Inject custom CSS to style messages and input area-------------
st.markdown(
    """
    <style>
        /* Style for user message */
        .user-message {
            background-color: #faeabe;
            color: black;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: left;
        }
        /* Style for bot message */
        .bot-message {
            background-color: #fffaed;
            color: black;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: right;
        }
    </style>
    """,
    unsafe_allow_html=True
)


if 'messages' not in st.session_state:
    st.session_state.messages = []


def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"


st.title("CV Analysis Chatbot - Phase_01")

#Sidebar--------------------------------------------------

with st.sidebar:
    st.write("# Upload CV")
    uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"], label_visibility="collapsed")

    if st.button("Submit CV"):
        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            st.session_state.file_path = file_path  
            st.success("CV submitted successfully!")
    
    
    st.markdown("<hr>", unsafe_allow_html=True)  
    
# Form for prompt input and submit button-------------------
    st.write("# Ask a Question")
    with st.form(key='question_form'):
        prompt = st.text_area("Ask your question here:", placeholder="Type your question...", key="prompt")  
        submit_button = st.form_submit_button(label="Enter") 

    if st.button("Clear Chat"):
        st.session_state.messages = []  


st.write("### Chatbot Responses:")


if submit_button and prompt:
    if 'file_path' in st.session_state:  
        file_path = st.session_state.file_path  
        response = requests.post("http://localhost:8000/api/data_handle", json={"file_path": file_path, "prompt": prompt})

        if response.status_code == 200:
            data = response.json()
            chatbot_response = data['message']

            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
        else:
            st.error("Error fetching response from backend.")
    else:
        st.warning("Please upload a CV before asking questions.")


# Display the latest chat history--------------------------------
message_container = st.container()
with message_container:
    if st.session_state.messages:
        for message in st.session_state.messages:
            st.markdown(message, unsafe_allow_html=True)
