import streamlit as st
from PyPDF2 import PdfReader

# Chat history storage
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("CV Chatbot Phase-1")
st.markdown("Upload 5 PDF CVs and ask questions to filter them.")

# Sidebar for uploading CVs
st.sidebar.header("Upload CVs")
uploaded_files = st.sidebar.file_uploader("Upload up to 5 PDF CVs", type="pdf", accept_multiple_files=True)

# Ensure 5 files are uploaded
if uploaded_files and len(uploaded_files) <= 5:
    st.success("All CVs uploaded successfully!")

    # Extract text from the uploaded PDF files
    pdf_texts = []
    for file in uploaded_files:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()  # Extract text from each page
        pdf_texts.append(text)

    # Chat-based interface
    st.header("Chat with the CVs")

    # Keep the question input bar at the top
    question = st.text_input("Ask a question about the CVs (e.g., 'Does this CV mention React or Python?')")

    # Display previous chat history below the input
    for chat in st.session_state.chat_history:
        st.chat_message(chat["role"]).markdown(chat["content"])

    # If a question is asked
    if question:
        # Display user question
        st.chat_message("user").markdown(question)

        # Store question in session state
        st.session_state.chat_history.append({"role": "user", "content": question})

        # Filter logic for the CVs
        st.subheader("CVs matching your question:")
        matched = False
        response = ""
        for i, text in enumerate(pdf_texts):
            if question.lower() in text.lower():
                response += f"**CV {i+1}** matches your question.\n\n"
                matched = True

        if not matched:
            response = "No CVs match your question."

        # Display the bot's response
        st.chat_message("assistant").markdown(response)

        # Store bot's response in session state
        st.session_state.chat_history.append({"role": "assistant", "content": response})

else:
    if not uploaded_files:
        st.warning("Please upload some CVs to proceed.")
    else:
        st.warning("Please upload only up to 5 PDF CVs.")
