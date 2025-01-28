from neo4j import GraphDatabase
from extract_pdf import extract_text_from_pdf

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

class Neo4jUploader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def insert_data(self, category, content):
        with self.driver.session() as session:
            session.run(
                "CREATE (n:Category {name: $category, content: $content})",
                category=category, content=content
            )

if __name__ == "__main__":
    pdf_path = "Harshana-Madhuwantha-CV ( SE ).pdf"
    extracted_text = extract_text_from_pdf(pdf_path)

    sections = {
        "About Me": "I am a fast learner...",
        "Education": "Reading B.Sc. (Hons)...",
        "Projects": "Clever Convo, Content Harbor...",
        "Skills": "Python, Django, React JS...",
        "Certificates": "Machine Learning, Cybersecurity...",
    }

    uploader = Neo4jUploader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    for key, value in sections.items():
        uploader.insert_data(key, value)

    uploader.close()
    print("Data inserted successfully into Neo4j.")
