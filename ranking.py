from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
import os

#file reading part
def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

cv_directory = 'E:/INTERN-BISTEC/Projects/V1/data'
cv_texts = []
cv_files = [f for f in os.listdir(cv_directory) if f.endswith('.pdf')]

for cv_file in cv_files:
    cv_path = os.path.join(cv_directory, cv_file)
    cv_texts.append(read_pdf(cv_path))

# filter
query_text = "who is best in frontend"

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(cv_texts + [query_text])

cv_vectors = tfidf_matrix[:-1]  
query_vector = tfidf_matrix[-1]   

# cosine sililarity
cosine_similarities = cosine_similarity(query_vector, cv_vectors).flatten()

# Sort CVs by similarity score
sorted_indices = cosine_similarities.argsort()[::-1]
sorted_scores = cosine_similarities[sorted_indices]

# output
print("Results for %s:" %(query_text))
for idx, score in zip(sorted_indices, sorted_scores):
    print(f"CV '{cv_files[idx]}': Similarity Score = {score:.4f}")
