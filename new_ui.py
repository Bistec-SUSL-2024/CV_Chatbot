import streamlit as st
import requests

# --------------------------------------------------------CSS-------------------------------------------------------
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
        .candidates-section {
            background-color: #444;
            padding: 5px;
            border-radius: 10px;
            color: white;
            margin-bottom: 5px;
        }
        .ask-more-info {
            background-color: #555;
            color: white;
            padding: 5px;
            border-radius: 10px;
            margin-bottom: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if 'cv_results' not in st.session_state:
    st.session_state.cv_results = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'current_cv' not in st.session_state:
    st.session_state.current_cv = None
if 'job_desc' not in st.session_state:
    st.session_state.job_desc = ""

# App Title
st.title("CV Analysis Chatbot - Phase_02")

# Function to clear all inputs and session states
def clear_text():
    st.session_state.cv_results = []
    st.session_state.messages = []
    st.session_state.show_chat = False
    st.session_state.current_cv = None
    st.session_state.job_desc = ""


def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"


# Job description input
st.markdown(
    """
    <div style='background-color: #333; padding: 4px; border-top-left-radius: 10px; border-top-right-radius: 10px;'>
        <h6 style='color: white;'>Input the job description :</h6>
    </div>
    """, 
    unsafe_allow_html=True
)
job_description = st.text_area(
    label="type here", 
    placeholder="Enter job description here...", 
    label_visibility="collapsed", 
    key="job_desc"
)

# Clear and Submit buttons
col1, col2 = st.columns(2)
with col1:
    st.button("Clear description", on_click=clear_text, use_container_width=True, key="clear_description")
with col2:
    if st.button("Submit description", use_container_width=True, key="submit_description"):
        if job_description.strip():
            try:
                response = requests.post(
                    "http://localhost:8000/rank_cvs",  # Replace with your backend API URL
                    json={"description": job_description}
                )
                if response.status_code == 200:
                    st.session_state.cv_results = response.json().get("ranked_cvs", [])
                    st.session_state.show_chat = False
                else:
                    st.error("Failed to fetch CV rankings. Please try again.")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
        else:
            st.warning("Please enter a job description before submitting.")

#------------

def start_chatbot_for_cv(cv_id):
    """ Trigger the backend to start chatbot for the selected CV """
    try:
        response = requests.post(
            "http://localhost:8000/start_chatbot", 
            json={"cv_id": cv_id}
        )
        if response.status_code == 200:
            st.session_state.messages.append(display_message(f"Chatbot started for CV {cv_id}. Ask anything about it!", is_user=False))
        else:
            st.error("Failed to start chatbot session.")
    except Exception as e:
        st.error(f"Error starting chatbot: {e}")


# Display CV results
if st.session_state.cv_results:
    st.markdown("<div class='candidates-section'><h6>Ranked Candidates:</h6>", unsafe_allow_html=True)
    for idx, result in enumerate(st.session_state.cv_results, start=1):
        col1, col2, col3 = st.columns([6, 2, 2])
        with col1:
            st.write(f"**{idx}. {result['cv_id']}** (Score: {result['score']:.2f})")
        with col2:
            if st.button(f"Show CV", key=f"show_cv_{result['cv_id']}"):
                st.write(f"Displaying details of **{result['cv_id']}** (Placeholder) ")
        with col3:
            if st.button(f"Ask more info...", key=f"ask_question_{result['cv_id']}"):
                st.session_state.show_chat = True  
                st.session_state.current_cv = result['cv_id']
                start_chatbot_for_cv(result['cv_id'])


# Frontend: Get response from the backend based on user input question
def get_backend_response(user_input):
    try:
        response = requests.post(
            "http://localhost:8000/ask", 
            json={"cv_id": st.session_state.current_cv, "question": user_input}
        )
        if response.status_code == 200:
            return response.json().get('answer', "Sorry, I couldn't get an answer.")
        else:
            return "Error in response from backend."
    except Exception as e:
        return f"Error connecting to backend: {e}"

# Chat sidebar
if st.session_state.show_chat:
    with st.sidebar:
        st.markdown(f"<div class='ask-more-info'><h4>Ask more info about {st.session_state.current_cv} :</h4></div>", unsafe_allow_html=True)

        # Display previous conversation
        for message in st.session_state.messages:
            st.markdown(message, unsafe_allow_html=True)
        
        # Input for chat
        with st.form(key='question_form'):
            prompt = st.text_input(label="Ask a question", label_visibility="collapsed", placeholder="Enter your question...", key="prompt")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                clear_chat_button = st.form_submit_button(label="Clear Chat", on_click=lambda: st.session_state.messages.clear(), use_container_width=True)
            with col2:
                ask_button = st.form_submit_button(label="Ask", use_container_width=True)
        
        # Handle question submission
        if ask_button and prompt:
            chatbot_response = get_backend_response(prompt)  # Get response from backend
            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
            
            # Re-run the app to maintain the sidebar chat session
            st.rerun()
