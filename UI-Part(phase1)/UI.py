import streamlit as st
from PyPDF2 import PdfReader

st.title("CV Chatbot Phase-1")
st.markdown("Upload 5 PDF CVs and ask questions to filter them.")


st.sidebar.header("Upload CVs")
uploaded_files = st.sidebar.file_uploader("Upload up to 5 PDF CVs", type="pdf", accept_multiple_files=True)

# Ensure 5 files are uploaded
if len(uploaded_files) > 5:
    st.warning("Please upload only up to 5 PDF CVs to proceed.")
else:
    if uploaded_files:
        st.success("All CVs uploaded successfully!")

        # Extract text from the uploaded PDF files
        pdf_texts = []
        for file in uploaded_files:
            reader = PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()  # Extract text from each page
            pdf_texts.append(text)

        # Step 2: Ask a question to filter CVs
        st.header("Ask a Question to Filter CVs")
        question = st.text_input("Type your question here (e.g., 'Does this CV mention React or Python?')")

        # Filter logic
        if question:
            st.subheader("CVs matching your question:")
            matched = False  # Track if any CV matches
            for i, text in enumerate(pdf_texts):
                if question.lower() in text.lower():
                    st.write(f"CV {i+1} matches your question.")
                    matched = True

            if not matched:
                st.write("No CVs match your question.")
