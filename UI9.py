import streamlit as st
from PyPDF2 import PdfReader 

# Inject custom CSS to change the sidebar background color to blue, bot response background to pink, and double the height of the prompt area
st.markdown(
    """
    <style>
        /* Increase the height of the prompt input area (text input) */
        textarea {
            height: 100px !important; /* Double the default height */
        }
        .user-message {
            text-align: left;
            color: blue;
            margin-bottom: 10px;
        }
        .bot-message {
            text-align: right;
            color: green;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Function to style messages with emojis and CSS classes
def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

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

    # Form for prompt input and enter button
    st.write("# Ask a Question")
    with st.form(key='question_form'):
        prompt = st.text_area("Ask your question here:", placeholder="Type your question...", key="prompt")  # Use text_area instead of text_input
        submit_button = st.form_submit_button(label="Enter")  # This acts as the "Enter" button inside the form

    # Clear Chat button - resetting messages directly without rerun
    if st.button("Clear Chat"):
        # Clear chat history and reset session state for 'messages'
        st.session_state.messages = []

# Main area for chat responses
st.write("### Chatbot Responses:")

# If the user enters a prompt and clicks Enter
if submit_button and prompt:
    if st.session_state.cv_text:
        # Generate response from chatbot (based on user prompt and CV text)
        response = generate_response(prompt, st.session_state.cv_text)
        
        # Append user's prompt and chatbot's response to the message list
        st.session_state.messages.append(display_message(prompt, is_user=True))
        st.session_state.messages.append(display_message(response, is_user=False))
    else:
        st.warning("Please upload a CV before asking questions.")

# Display the latest chat history
message_container = st.container()
with message_container:
    # Display all chat history in a scrollable box
    if st.session_state.messages:
        for message in st.session_state.messages:
            st.markdown(message, unsafe_allow_html=True)
