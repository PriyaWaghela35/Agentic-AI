# service.py
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

class HealthTipsService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_health_tips(self, diagnosis: str, user_context: dict = None) -> str:
        """Core health tips generation logic"""
        prompt = f"Provide concise health tips for managing {diagnosis}"
        
        if user_context:
            prompt += f" for a {user_context.get('age', '')} year old {user_context.get('gender', '')}"
            if user_context.get('conditions'):
                prompt += f" who also has {', '.join(user_context['conditions'])}"
        
        prompt += """. Include:
        1. Dietary recommendations
        2. Lifestyle changes
        3. When to see a doctor"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
# the out put of this is not that formated so we need to check that and update the output laylout.
# anything other than this as input given by user will be invalid input and after confirm of a appointment terminate the session 