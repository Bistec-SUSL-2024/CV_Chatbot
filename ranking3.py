from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
import os
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

#othr text filter (lowercasing/ puncuation marks)
def preprocess_text(text):
    
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text) 
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return preprocess_text(text)

cv_directory = 'E:/INTERN-BISTEC/Projects/CV_Chatbot/V1/data'
cv_texts = []
cv_files = [f for f in os.listdir(cv_directory) if f.endswith('.pdf')]

for cv_file in cv_files:
    cv_path = os.path.join(cv_directory, cv_file)
    cv_texts.append(read_pdf(cv_path))

# Filter
query_text = preprocess_text("data science")

# remove common words
vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', max_df=0.8)
tfidf_matrix = vectorizer.fit_transform(cv_texts + [query_text])

cv_vectors = tfidf_matrix[:-1]  
query_vector = tfidf_matrix[-1]   

cosine_similarities = cosine_similarity(query_vector, cv_vectors).flatten()

# Output results
sorted_indices = cosine_similarities.argsort()[::-1]
sorted_scores = cosine_similarities[sorted_indices]

print("Results for %s:" % query_text)
for idx, score in zip(sorted_indices, sorted_scores):
    print(f"CV '{cv_files[idx]}': Similarity Score = {score:.4f}")
