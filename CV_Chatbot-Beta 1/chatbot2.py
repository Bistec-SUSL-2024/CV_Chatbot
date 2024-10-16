# chatbot2.py

from transformers import AutoModelForCausalLM, AutoTokenizer
from cv_data2 import cv_data

class CVChatbot:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

    def generate_response(self, user_input):
       
        normalized_input = user_input.lower()

      
        if "developer" in normalized_input or "need" in normalized_input:
        
            if "net" in normalized_input:
                skill = ".NET"
            elif "python" in normalized_input:
                skill = "Python"
            elif "java" in normalized_input:
                skill = "Java"
            else:
                return "I'm sorry, I don't have information about that role."

       
            matching_developers = [
                cv["name"] for cv in cv_data if skill in cv["skills"]
            ]

            if matching_developers:
                return f"Here are the {skill} developers:\n- " + "\n- ".join(matching_developers)
            else:
                return f"I'm sorry, I couldn't find any {skill} developers."

       
        new_user_input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors='pt')
        bot_input_ids = new_user_input_ids

        response_ids = self.model.generate(bot_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(response_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

        return response
