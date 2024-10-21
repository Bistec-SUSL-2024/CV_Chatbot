import streamlit as st
from PyPDF2 import PdfReader
from transformers import AutoModelForCausalLM, AutoTokenizer
from cv_data import cv_data

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

st.title("CV Analyzer Chatbot ")
st.markdown("Upload PDF CVs and ask questions to filter them.")

st.sidebar.header("Upload CVs")
uploaded_files = st.sidebar.file_uploader("Upload up to 5 PDF CVs", type="pdf", accept_multiple_files=True)


def query_cv(candidate_name, query):
    if candidate_name in cv_data:
        cv = cv_data[candidate_name]
        
        if "name" in query.lower():
            return f"Candidate's Name: {cv['name']}"
        elif "skills" in query.lower():
            return f"Skills: {', '.join(cv['skills'])}"
        elif "experience" in query.lower():
            exp_details = "\n".join([f"{exp['position']} at {exp['company']} ({exp['years']} years)" for exp in cv['experience']])
            return f"Experience: \n{exp_details}"
        elif "education" in query.lower():
            edu = cv['education']
            return f"Education: {edu['degree']} from {edu['university']} (Graduated in {edu['graduation_year']})"
        else:
            return "I couldn't understand your query. Please ask about name, skills, experience, or education."
    else:
        return "Candidate not found. Please provide a valid name."

# Function to generate a response from Microsoft DialoGPT
def generate_response(input_text):
    new_input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors='pt')
    bot_input_ids = new_input_ids
    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response

# Function to suggest candidates based on skills mentioned in the user input
def suggest_candidates_based_on_skill(skill):
    matching_candidates = []
    for candidate, data in cv_data.items():
        if skill.lower() in (s.lower() for s in data['skills']):
            matching_candidates.append(candidate)
    return matching_candidates


# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Text input for the user query
user_input = st.text_input("Good day, we welcome you.  Mention the skills,progaming language , framework or any if any, that a person you wish to find should have here: (eg : python ,aws)")

# Initialize found_candidates to avoid NameError
found_candidates = []

# If user provides input, check for skills and suggest candidates
if user_input:
    # Add user input to chat history
    st.session_state.chat_history.append(f"You: {user_input}")
    
    # Extract skills mentioned in the query
    for candidate in cv_data:
        # Check if the query mentions any skill
        for skill in cv_data[candidate]['skills']:
            if skill.lower() in user_input.lower():
                found_candidates = suggest_candidates_based_on_skill(skill)
    
    # Generate response or suggest candidates based on the user input
    if found_candidates:
        candidates_list = ', '.join(found_candidates)
        bot_response = f"Candidates with the mentioned skill: {candidates_list}"
    else:
        bot_response = generate_response(user_input)
    
    # Add bot response to chat history
   # st.session_state.chat_history.append(f"Bot: {bot_response}")

# Display chat history
for message in st.session_state.chat_history:
    st.write(message)

# If there are candidates found, allow users to ask more specific questions
if found_candidates:
    # Candidate selection after skill suggestion
    candidate_name = st.selectbox("Select a candidate", found_candidates)
    
    # Ask for a specific query (skills, experience, education)
    specific_query = st.text_input(f"What would you like to know about {candidate_name}? (e.g., skills, experience, education)")

    if st.button("Submit Query"):
        # If the query is related to CV details
        if any(keyword in specific_query.lower() for keyword in ["name", "skills", "experience", "education"]):
            bot_response = query_cv(candidate_name, specific_query)
        else:
            # Otherwise, generate a response using the chatbot
            bot_response = generate_response(specific_query)
        
        # Add bot response to chat history
        #st.session_state.chat_history.append(f"You: {specific_query}")
        st.session_state.chat_history.append(f"Bot: {bot_response}")

# Reset chat button (optional)
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    # No rerun, simply clear the chat history for the user to see immediately
    st.write("Chat history cleared.")





