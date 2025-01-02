from langchain.text_splitter import RecursiveCharacterTextSplitter

markdown_text = """
# John Doe
Software Engineer with 5 years of experience in software development, specializing in Python, Machine Learning, and Cloud Computing. Strong knowledge in data structures, algorithms, and system design.

## Education
- **Master's Degree** in Computer Science, XYZ University, 2020
- **Bachelor's Degree** in Software Engineering, ABC University, 2018

## Skills
- **Languages**: Python, Java, JavaScript
- **Tools**: Git, Docker, Kubernetes
- **Technologies**: AWS, Azure, TensorFlow

## Experience
**Software Engineer**, TechCorp, 2020–Present
- Developed and maintained web applications using Python and Flask.
- Led machine learning projects to improve product recommendations.

**Intern**, DevWorks, 2018–2019
- Assisted in backend development with Java and MongoDB.
"""

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,  
    chunk_overlap=50
)

chunks = text_splitter.create_documents([markdown_text])
for chunk in chunks:
    print(chunk)

    #Test passed
