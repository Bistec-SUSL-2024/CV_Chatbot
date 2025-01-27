# CV Chatbot Project: 

## 🌐 Live Demo (Phase-1)
We’ve successfully deployed Phase-1 of the CV Chatbot, which supports **CV analysis for individual resumes**.
Check it out here:
👉 [CV Chatbot Phase-1 Demo](https://cv-chatbot-analyzer.streamlit.app/) 👈




## 🚀 Phases of Development

### 1. Phase-1: Individual CV Analysis

We’ve successfully deployed Phase-1 of the CV Chatbot, which supports **CV analysis for individual resumes**.

Check it out here:
👉 [CV Chatbot Phase-1 Demo](https://cv-chatbot-analyzer.streamlit.app/) 👈

   - **Features**:
     - Upload a single CV for analysis.
     - Extract and process key information like skills, education, and work experience.

### 2. Phase-2: Batch Processing and Database Integration
   - **Key Updates**:
     - Google Drive Integration:
       - Upload up to 100 CVs into a designated Google Drive folder.
       - Process each CV into Markdown format.
       - Store Markdown files in another Google Drive folder.
     - Pinecone Database:
       - Upsert the converted Markdown files into a Pinecone Vector Database for efficient storage and retrieval.
     - React Frontend Features:
       - Job Candidate Search:
          - Enter a job description to retrieve a list of relevant job candidates.
       - Candidate Chatbot:
          - Select a candidate from the list to generate a chatbot.
          - Ask specific questions about the selected candidate, and receive detailed responses.
            
### 3. Phase-3: Advanced Search and Large CV Support
   - **Planned Enhancements**:
     - Hybrid Search:
       - Combine vector search with keyword-based search for better accuracy.
     - Large CV Handling:
       - Chunk large CVs into smaller pieces for scalable storage in the Pinecone database.
     - Accuracy Improvements:
       - Refine algorithms to provide precise and relevant search results.

---

## 🛠️ Technology Stack
1. **Phase-1**:
   - Python
   - Streamlit
2. **Phase-2**:
   - Google Drive API
   - Markdownify
   - Pinecone Database
   - LlamaIndex
   - React
3. **Phase-3**:
   - Advanced Pinecone capabilities
   - Hybrid search algorithms
