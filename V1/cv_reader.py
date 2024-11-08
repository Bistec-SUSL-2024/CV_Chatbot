from llama_index.core import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

#file reading
data_directory = "E:/INTERN-BISTEC/Projects/V1/data"
loader = SimpleDirectoryReader(data_directory, recursive=True, required_exts=[".pdf"])
documents = loader.load_data()

job_description = """
Strong Java development skills including object-oriented programming, 
experience with frameworks such as Spring and Hibernate, 
knowledge in J2EE and enterprise applications, and familiarity with Java-based microservices.
"""

job_embedding = model.encode(job_description)

best_cv = None
best_score = -1  

# for loop
for doc in documents:
    cv_content = doc.content if hasattr(doc, 'content') else ''
    
    if cv_content.strip():  
        cv_embedding = model.encode(cv_content)
        
        # cosine similarity use here
        similarity_score = cosine_similarity([job_embedding], [cv_embedding])[0][0]
 
        if similarity_score > best_score:
            best_score = similarity_score
            best_cv = doc 

# output
if best_cv:
    print(f"The best CV for Java is: {best_cv.metadata.get('file_name', 'Unknown')}")
    print(f"File Path: {best_cv.metadata.get('file_path', 'Unknown')}")
    print(f"Similarity Score: {best_score}")
else:
    print("No suitable CVs found.")
