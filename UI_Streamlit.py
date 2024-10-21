#Install PyPDF2

import streamlit as st
from PyPDF2 import PdfReader 


# Function to extract text from PDF
def extract_cv_text(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Function to generate chatbot response (replace with actual chatbot logic)
def generate_response(prompt, cv_text):
    # Example placeholder response (replace with actual chatbot model output)
    return f"Chatbot response to: '{prompt}' with the given CV data."

# Initialize session state for chat history and CV text
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'cv_text' not in st.session_state:
    st.session_state.cv_text = ""

# Function to style messages with emojis
def display_message(text, is_user):
    if is_user:
        return f"<div style='text-align: right; color: blue;'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div style='text-align: left; color: green;'><strong>🤖 Bot:</strong> {text}</div>"

# Streamlit layout
st.title("CV Analysis Chatbot - beta")

# Sidebar for file upload and prompt area
with st.sidebar:
    st.write("# Upload CV")
    
    # File upload area
    uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"], label_visibility="collapsed")

    if st.button("Submit CV"):
        if uploaded_file is not None:
            # Extract text from the uploaded PDF
            st.session_state.cv_text = extract_cv_text(uploaded_file)
            st.success("CV submitted successfully!")
    
    # Line separator
    st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal line to separate sections
    
    # Prompt input area
    st.write("# Ask a Question")
    prompt = st.text_input("Ask your question here:", placeholder="Type your question...", key="prompt")

    if st.button("Clear Chat"):
        st.session_state.messages = []  # Clear chat history

# Main area for chat responses
st.write("### Chatbot Responses:")

# Create a scrollable container for messages
message_container = st.container()
with message_container:
    # Display chat history in a scrollable box
    chat_history = st.empty()
    if st.session_state.messages:
        for message in st.session_state.messages:
            chat_history.markdown(message, unsafe_allow_html=True)

# If the user enters a prompt
if prompt:
    if st.session_state.cv_text:
        # Generate response from chatbot (based on user prompt and CV text)
        response = generate_response(prompt, st.session_state.cv_text)
        
        # Append user's prompt and chatbot's response to the message list
        st.session_state.messages.append(display_message(prompt, is_user=True))
        st.session_state.messages.append(display_message(response, is_user=False))
        
        # Display the latest chat history
        chat_history.markdown(display_message(response, is_user=False), unsafe_allow_html=True)
    else:
        st.warning("Please upload a CV before asking questions.")
