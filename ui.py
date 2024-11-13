import streamlit as st

# Custom CSS for styling the chatbot
st.markdown(
    """
    <style>
        /* Chat container styling */
        .chat-container {
            display: flex;
            flex-direction: column;
            max-height: 500px;
            overflow-y: auto;
            margin-bottom: 100px;
        }

        /* Chat message styling */
        .user-message {
            background-color: #f0f8ff;
            color: #333;
            border-radius: 15px;
            padding: 12px;
            margin-bottom: 10px;
            max-width: 80%;
            align-self: flex-start;
        }

        .bot-message {
            background-color: #dcdcdc;
            color: #333;
            border-radius: 15px;
            padding: 12px;
            margin-bottom: 10px;
            max-width: 80%;
            align-self: flex-end;
        }

        /* Chat input form styling */
        .chat-input {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #fafafa;
            padding: 15px;
            box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.1);
            z-index: 999;
        }

        .chat-input input[type="text"] {
            width: 90%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ccc;
            font-size: 14px;
        }

        .chat-input .submit-button {
            width: 15%;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px;
            cursor: pointer;
            font-size: 14px;
        }

        /* Job description container styling */
        .job-description {
            margin-bottom: 30px;
        }

        /* Hide the default Streamlit input container */
        .main-container {
            padding-bottom: 120px;
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

def display_message(text, is_user):
    """Function to display user and bot messages in the chat"""
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

st.title("CV Analysis Chatbot - V 2.0")

# Job description input
st.write("### Enter Job Description:")
job_description = st.text_area("Job Description", placeholder="Enter job description here...")
if st.button("Show Job Description"):
    st.session_state.cv_results = [
        {"id": 1, "title": "CV1"},
        {"id": 2, "title": "CV2"},
        {"id": 3, "title": "CV3"},
        {"id": 4, "title": "CV4"},
        {"id": 5, "title": "CV5"}
    ]
    st.session_state.show_chat = False  # Reset chat visibility when new CVs are loaded

# Display CV results
if st.session_state.cv_results:
    st.write("### CV Matching Results:")
    for result in st.session_state.cv_results:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{result['title']}**")
        with col2:
            if st.button(f"Show CV", key=f"show_cv_{result['id']}"):
                st.write(f"Displaying {result['title']} details (Placeholder)")
        with col3:
            if st.button(f"Ask Question", key=f"ask_question_{result['id']}"):
                st.session_state.show_chat = True  
                st.session_state.current_cv = result['title']  

# Chatbot view when 'Ask Question' is clicked
if st.session_state.show_chat:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.write(f"### Chat for {st.session_state.current_cv}")

    # Displaying messages in chat
    for message in st.session_state.messages:
        st.markdown(message, unsafe_allow_html=True)

    # Chat input form with submit button
    with st.form(key='question_form'):
        st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
        prompt = st.text_input(label="ask", label_visibility="collapsed", placeholder="Enter your question....", key="prompt")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            clear_chat_button = st.form_submit_button(label="Clear Chat", on_click=lambda: st.session_state.messages.clear(), use_container_width=True)
        with col2:
            submit_button = st.form_submit_button(label="Ask", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Handling the response from the chatbot
    if submit_button and prompt:
        chatbot_response = f"Response for '{prompt}' regarding {st.session_state.current_cv} (Placeholder)"
        st.session_state.messages.append(display_message(prompt, is_user=True))
        st.session_state.messages.append(display_message(chatbot_response, is_user=False))

    st.markdown("</div>", unsafe_allow_html=True)
