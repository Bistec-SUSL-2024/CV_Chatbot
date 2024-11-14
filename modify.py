import streamlit as st
import requests

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
        .stButton > button {
            font-size: 6px;
            padding: 1px 3px;  
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

# Initialize session states
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

def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

st.title("CV Analysis Chatbot - Phase_02")

def clear_text():
    # Reset all session states to initial values
    st.session_state.cv_results = []
    st.session_state.messages = []
    st.session_state.show_chat = False
    st.session_state.current_cv = None
    st.session_state.job_desc = ""

# Job description input
st.markdown(
    """
    <div style='background-color: #333; padding: 4px; border-top-left-radius: 10px; border-top-right-radius: 10px;'>
        <h6 style='color: white;'>Input the job description :</h6>
    </div>
    """, 
    unsafe_allow_html=True
)
job_description = st.text_area(label="type here ", placeholder="Enter job description here...", label_visibility="collapsed", key="job_desc")

col1, col2 = st.columns(2)

with col1:
    st.button("clear description", on_click=clear_text, use_container_width=True)

with col2:
    if st.button("Submit description", use_container_width=True):
        # Simulated results for demonstration
        st.session_state.cv_results = [
            {"id": 1, "title": "Candidate 1"},
            {"id": 2, "title": "Candidate 2"},
            {"id": 3, "title": "Candidate 3"},
            {"id": 4, "title": "Candidate 4"},
            {"id": 5, "title": "Candidate 5"}
        ]
        st.session_state.show_chat = False  # Reset chat visibility when new CVs are loaded

# Displaying candidates list
if st.session_state.cv_results:
    st.markdown("<div class='candidates-section'><h6>Relevant Candidates:</h6>", unsafe_allow_html=True)
    for result in st.session_state.cv_results:
        col1, col2, col3 = st.columns([6, 2, 2])
        with col1:
            st.write(f"**{result['title']}**")
        with col2:
            if st.button(f"Show CV", key=f"show_cv_{result['id']}"):
                st.write(f"Displaying {result['title']} details (Placeholder)")
        with col3:
            if st.button(f"Ask more info...", key=f"ask_question_{result['id']}"):
                st.session_state.show_chat = True  
                st.session_state.current_cv = result['title']

# Chat sidebar
if st.session_state.show_chat:
    with st.sidebar:
        st.markdown(f"<div class='ask-more-info'><h4>Ask more info. about {st.session_state.current_cv} :</h4></div>", unsafe_allow_html=True)
        
        # Display existing messages
        for message in st.session_state.messages:
            st.markdown(message, unsafe_allow_html=True)
        
        # Form for user input
        with st.form(key='question_form'):
            prompt = st.text_input(label="Ask a question", label_visibility="collapsed", placeholder="Enter your question...", key="prompt")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                clear_chat_button = st.form_submit_button(label="Clear Chat", on_click=lambda: st.session_state.messages.clear(), use_container_width=True)
            with col2:
                submit_button = st.form_submit_button(label="Ask", use_container_width=True)
        
        # Handling new message
        if submit_button and prompt:
            chatbot_response = f"Response for '{prompt}' regarding {st.session_state.current_cv} (Placeholder)"
            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
