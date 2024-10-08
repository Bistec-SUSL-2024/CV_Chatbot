from sentence_transformers import SentenceTransformer, util
import torch

# Load pre-trained model from Huggingface
model = SentenceTransformer('all-MiniLM-L6-v2')

contexts = {
    "Person1": {
        "name": "Chamara",
        "degree": "M.Sc",
        "skills": "React, Python",
        "description": "I am Chamara and I'm familiar with Node.js and Python."
    },
    "Person2": {
        "name": "Saman",
        "degree": "B.Sc",
        "skills": "React, MongoDB",
        "description": "I am an experienced web developer with a strong background in React and MongoDB."
    },
    "Person3": {
        "name": "Kamal",
        "degree": "PhD",
        "skills": "Java, Enterprise Applications",
        "description": "I have expertise in Java and worked on several enterprise-level applications."
    },

    "Person4": {
        "name": "Amal",
        "degree": "B.Sc",
        "skills": "Java, Enterprise Applications",
        "description": "I have expertise in Java and worked on several enterprise-level applications."
    }
}

# Function to filter contexts by both skill and degree
def filter_by_skill_and_degree(skill, degree):
    matching_people = []
    for person_id, context in contexts.items():
        skill_match = skill.lower() in context['skills'].lower()
        degree_match = degree.lower() == context['degree'].lower()
        
        if skill_match:
            matching_people.append((context, degree_match))  # Include degree match as a flag
    return matching_people

# Function to process user question and find contexts that match both skill and degree
def find_people_with_skill_and_degree(question, skill, degree):
    question_embedding = model.encode(question, convert_to_tensor=True)
    
    # Filter contexts by the required skill and degree
    filtered_contexts = filter_by_skill_and_degree(skill, degree)
    
    results = []
    for context, degree_match in filtered_contexts:
        context_string = f"Name: {context['name']}, Degree: {context['degree']}, Skills: {context['skills']}, Description: {context['description']}"
        
        context_embedding = model.encode(context_string, convert_to_tensor=True)
        
        # Calculate cosine similarity
        cosine_scores = util.pytorch_cos_sim(question_embedding, context_embedding)
        score = cosine_scores.item()
        
        # Penalize if degree does not match
        if not degree_match:
            score *= 0.6  
        
        # Append result with score
        results.append({
            "answer": context_string,
            "score": score
        })
    
    # Sort results based on similarity scores
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    return results

# Main loop to dynamically ask for user questions, skill, and degree
while True:
    user_question = input("Please ask a question (or type 'exit' to quit): ")
    if user_question.lower() == 'exit':
        break

    skill = input("Enter the skill to filter by (e.g., React): ")
    degree = input("Enter the degree to filter by (e.g., B.Sc): ")
    
    # Get all people who match the skill and degree
    answers = find_people_with_skill_and_degree(user_question, skill, degree)
    
    if answers:
        print("\n--- Matching People ---")
        for answer in answers:
            print(f"Context: {answer['answer']}\nSimilarity Score: {answer['score']}\n")
    else:
        print("No matching context found.\n")
