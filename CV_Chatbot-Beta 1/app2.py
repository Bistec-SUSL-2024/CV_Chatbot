# app2.py

import streamlit as st
from chatbot2 import CVChatbot 

def main():
    st.title("CV Analysis Chatbot")  
  
    chatbot = CVChatbot()

    user_input = st.text_input("Ask a question about a CV (e.g., 'I need a .NET developer')")

    if user_input:
        response = chatbot.generate_response(user_input)
        st.write(response)

if __name__ == "__main__":
    main()
