from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

stop_words = set(stopwords.words('english')) #stop calculating is / am / the etc.
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
   
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens if word.isalpha() and word.lower() not in stop_words]
    return ' '.join(tokens)


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


query_text = "who is best in frontend"
query_text = preprocess_text(query_text)

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(cv_texts + [query_text])

cv_vectors = tfidf_matrix[:-1]
query_vector = tfidf_matrix[-1]


cosine_similarities = cosine_similarity(query_vector, cv_vectors).flatten()


sorted_indices = cosine_similarities.argsort()[::-1]
sorted_scores = cosine_similarities[sorted_indices]

print(f"Results for '{query_text}':")
for idx, score in zip(sorted_indices, sorted_scores):
    print(f"CV '{cv_files[idx]}': Similarity Score = {score:.4f}")
