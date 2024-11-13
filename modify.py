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

        /* Fixed position for input form at the bottom */
        .chat-input {
            position: fixed;
            bottom: 0;
            width: 160%;
            max-width: 1600px;
            background-color: #333;
            padding: 20px;
            margin: 0 auto;
            z-index: 999;
            left: 50%;
            transform: translateX(-50%);
        }

        .chat-input input[type="text"] {
            width: 150%;
            margin-right: 10px;
            padding: 12px;
            border-radius: 8px;
        }

        .main-container {
            padding-bottom: 260px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if 'cv_results' not in st.session_state:
    st.session_state.cv_results = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'current_cv' not in st.session_state:
    st.session_state.current_cv = None

def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

st.title("CV Analysis Chatbot - Phase_02")

def clear_text():
    st.session_state["job_desc"] = ""

st.markdown(
    """
    <div style='background-color: #333; padding: 4px; border-radius: 10px;'>
        <h7 style='color: white;'>Input the job description :</h7>
    </div>
    """, 
    unsafe_allow_html=True
)
job_description = st.text_area(label=" ", placeholder="Enter job description here...")

col1, col2 = st.columns(2)

with col1:
    st.button("clear description", on_click=clear_text)

with col2:
    if st.button("Show Job Description"):
        # Here you would add code to handle the submission
        st.session_state.cv_results = [
        {"id": 1, "title": "Candidate 1"},
        {"id": 2, "title": "Candidate 2"},
        {"id": 3, "title": "Candidate 3"},
        {"id": 4, "title": "Candidate 4"},
        {"id": 5, "title": "Candidate 5"}
    ]
    st.session_state.show_chat = False  # Reset chat visibility when new CVs are loaded


if st.session_state.cv_results:
    st.write("##### Relevant Candidates:")
    for result in st.session_state.cv_results:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{result['title']}**")
        with col2:
            if st.button(f"Show CV", key=f"show_cv_{result['id']}"):
                st.write(f"Displaying {result['title']} details (Placeholder)")
        with col3:
            if st.button(f"Ask more...", key=f"ask_question_{result['id']}"):
                st.session_state.show_chat = True  
                st.session_state.current_cv = result['title']  


if st.session_state.show_chat:
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.write(f"### Chat for {st.session_state.current_cv}")

 
    for message in st.session_state.messages:
        st.markdown(message, unsafe_allow_html=True)

   
    with st.form(key='question_form'):
        st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
        prompt = st.text_input(label="ask", label_visibility="collapsed", placeholder="Enter your question....", key="prompt")
        
        
        col1, col2 = st.columns([1, 1])
        with col1:
            clear_chat_button = st.form_submit_button(label="Clear Chat", on_click=lambda: st.session_state.messages.clear(), use_container_width=True)
        with col2:
            submit_button = st.form_submit_button(label="Ask", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

   
    if submit_button and prompt:
        
        chatbot_response = f"Response for '{prompt}' regarding {st.session_state.current_cv} (Placeholder)"
        st.session_state.messages.append(display_message(prompt, is_user=True))
        st.session_state.messages.append(display_message(chatbot_response, is_user=False))

    
    st.markdown("</div>", unsafe_allow_html=True)
