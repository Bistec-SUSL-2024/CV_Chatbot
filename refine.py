from llama_index import openai

prompt = "I have a job vacancy, that needs skills in Azure Data Engineering tools. Experience required least 5 years"
llm = openai(temperature=0.7)
refined_description = llm.predict(prompt)

print(refined_description)
