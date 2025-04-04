# import pandas as pd
# import google.generativeai as genai
# from sklearn.ensemble import RandomForestClassifier
# from typing import List, Dict, Optional
# import json
# from dotenv import load_dotenv
# import os

# load_dotenv()

# class DiagnosisAgent:
#     def __init__(self, data_path: str = None):
#         self.model = None
#         self.symptom_encoder = None
#         self.disease_info = {}
#         self.ai_model = None
        
#         # Initialize Gemini
#         api_key = os.getenv('GEMINI_API_KEY')
#         if api_key:
#             genai.configure(api_key=api_key)
#             self.ai_model = genai.GenerativeModel('gemini-pro')
        
#         if data_path:
#             self.load_and_train(data_path)
    
#     def load_and_train(self, data_path: str):
#         """Load and train the ML model"""
#         data = pd.read_csv(data_path)
#         symptoms = data.drop("disease", axis=1).columns
#         self.symptom_encoder = {symptom: i for i, symptom in enumerate(symptoms)}
        
#         X = data.drop("disease", axis=1).values
#         y = data["disease"].values
#         self.model = RandomForestClassifier()
#         self.model.fit(X, y)
    
#     def get_diagnosis(self, symptoms: List[str]) -> Dict:
#         """Get diagnosis for given symptoms"""
#         if not self.model:
#             return {"error": "Model not trained"}
        
#         symptom_vector = [0] * len(self.symptom_encoder)
#         for symptom in symptoms:
#             if symptom in self.symptom_encoder:
#                 symptom_vector[self.symptom_encoder[symptom]] = 1
        
#         probabilities = self.model.predict_proba([symptom_vector])[0]
#         top_3 = sorted(zip(self.model.classes_, probabilities), 
#                      key=lambda x: x[1], reverse=True)[:3]
        
#         return {
#             "conditions": [
#                 {
#                     "name": disease,
#                     "probability": float(prob),
#                     "recommended_tests": self._get_tests_for_condition(disease)
#                 } for disease, prob in top_3
#             ]
#         }
    
#     def analyze_symptom_description(self, description: str) -> Dict:
#         """Analyze natural language symptom description"""
#         if not self.ai_model:
#             return {"error": "AI not configured"}
        
#         # Extract symptoms
#         prompt = f"""
#         Extract medical symptoms from:
#         "{description}"
        
#         Return JSON format:
#         {{
#             "symptoms": ["list", "of", "symptoms"],
#             "urgency": "mild/moderate/severe"
#         }}
#         """
#         extracted = self._get_ai_response(prompt)
        
#         # Get diagnosis
#         diagnosis = self.get_diagnosis(extracted.get("symptoms", []))
        
#         # Generate explanation
#         explanation = self._generate_explanation(description, diagnosis)
        
#         return {
#             "symptoms": extracted.get("symptoms", []),
#             "diagnosis": diagnosis,
#             "explanation": explanation,
#             "urgency": extracted.get("urgency", "moderate")
#         }
    
#     def _get_ai_response(self, prompt: str) -> Dict:
#         """Get structured response from Gemini"""
#         try:
#             response = self.ai_model.generate_content(prompt)
#             return json.loads(response.text)
#         except:
#             return {}
    
#     def _generate_explanation(self, description: str, diagnosis: Dict) -> str:
#         """Generate patient-friendly explanation"""
#         prompt = f"""
#         Patient description: "{description}"
#         Possible conditions: {[d['name'] for d in diagnosis['conditions']]}
        
#         Generate a patient-friendly explanation that:
#         1. Acknowledges their concerns
#         2. Lists possible conditions without alarming
#         3. Recommends next steps
#         4. Indicates urgency level
#         """
#         return self.ai_model.generate_content(prompt).text
    
#     def _get_tests_for_condition(self, condition: str) -> List[str]:
#         """Get recommended tests for a condition"""
#         prompt = f"""
#         Recommend 3 diagnostic tests for {condition}.
#         Return as a JSON list.
#         """
#         return self._get_ai_response(prompt).get("tests", [])


import pandas as pd
import google.generativeai as genai
from sklearn.ensemble import RandomForestClassifier
from typing import List, Dict, Optional, Tuple
import json
from dotenv import load_dotenv
import os

load_dotenv()

class DiagnosisAgent:
    def __init__(self, data_path: str = None):
        self.model = None
        self.symptom_encoder = None
        self.disease_info = {}
        self.ai_model = None
        
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            print("Api success")
            self.ai_model = genai.GenerativeModel('gemini-pro')
        
        if data_path:
            try:
                self.load_and_train(data_path)
            except Exception as e:
                print(f"Error loading data: {str(e)}")
                self.model = None

    def load_and_train(self, data_path: str) -> Tuple[bool, str]:
        """Load and train the ML model with proper error handling"""
        try:
            data = pd.read_csv(data_path)
            print("hello world")
            # Check if 'disease' column exists
            if 'disease' not in data.columns:
                raise ValueError("CSV must contain a 'disease' column")
                
            # Get symptoms (all columns except 'disease')
            symptoms = [col for col in data.columns if col != 'disease']
            if not symptoms:
                raise ValueError("No symptom columns found in CSV")
                
            self.symptom_encoder = {symptom: i for i, symptom in enumerate(symptoms)}
            
            X = data[symptoms].values
            y = data["disease"].values
            
            self.model = RandomForestClassifier()
            self.model.fit(X, y)
            
            # Build disease info
            self.disease_info = {
                disease: {
                    "description": f"Information about {disease}",
                    "common_tests": ["Complete blood count", "Physical examination"],
                    "urgency": "moderate"
                } for disease in set(y)
            }
            return True, "Model trained successfully"
            
        except Exception as e:
            self.model = None
            raise Exception(f"Failed to train model: {str(e)}")

    def get_diagnosis(self, symptoms: List[str]) -> Dict:
        """Get diagnosis for given symptoms with proper validation"""
        if not self.model:
            return {"error": "Model not trained", "suggestion": "Check if data was loaded properly"}
        
        if not symptoms:
            return {"error": "No symptoms provided"}
            
        # Create symptom vector
        symptom_vector = [0] * len(self.symptom_encoder)
        valid_symptoms = []
        
        for symptom in symptoms:
            if symptom in self.symptom_encoder:
                symptom_vector[self.symptom_encoder[symptom]] = 1
                valid_symptoms.append(symptom)
        
        if not valid_symptoms:
            return {"error": "No valid symptoms recognized", "available_symptoms": list(self.symptom_encoder.keys())}
        
        # Get predictions
        probabilities = self.model.predict_proba([symptom_vector])[0]
        top_3 = sorted(zip(self.model.classes_, probabilities), 
                     key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "conditions": [
                {
                    "name": disease,
                    "probability": float(prob),
                    "recommended_tests": self._get_tests_for_condition(disease),
                    "info": self.disease_info.get(disease, {})
                } for disease, prob in top_3
            ],
            "matched_symptoms": valid_symptoms
        }
    def analyze_symptom_description(self, description: str) -> Dict:
        """Analyze natural language symptom description"""
        if not self.ai_model:
            return {"error": "AI not configured"}
        
        # Extract symptoms
        prompt = f"""
        Extract medical symptoms from:
        "{description}"
        
        Return JSON format:
        {{
            "symptoms": ["list", "of", "symptoms"],
            "urgency": "mild/moderate/severe"
        }}
        """
        extracted = self._get_ai_response(prompt)
        
        # Get diagnosis
        diagnosis = self.get_diagnosis(extracted.get("symptoms", []))
        
        # Generate explanation
        explanation = self._generate_explanation(description, diagnosis)
        
        return {
            "symptoms": extracted.get("symptoms", []),
            "diagnosis": diagnosis,
            "explanation": explanation,
            "urgency": extracted.get("urgency", "moderate")
        }
    
    def _get_ai_response(self, prompt: str) -> Dict:
        """Get structured response from Gemini"""
        try:
            response = self.ai_model.generate_content(prompt)
            return json.loads(response.text)
        except:
            return {}
    
    def _generate_explanation(self, description: str, diagnosis: Dict) -> str:
        """Generate patient-friendly explanation"""
        prompt = f"""
        Patient description: "{description}"
        Possible conditions: {[d['name'] for d in diagnosis['conditions']]}
        
        Generate a patient-friendly explanation that:
        1. Acknowledges their concerns
        2. Lists possible conditions without alarming
        3. Recommends next steps
        4. Indicates urgency level
        """
        return self.ai_model.generate_content(prompt).text
    
    def _get_tests_for_condition(self, condition: str) -> List[str]:
        """Get recommended tests for a condition"""
        prompt = f"""
        Recommend 3 diagnostic tests for {condition}.
        Return as a JSON list.
        """
        return self._get_ai_response(prompt).get("tests", [])

# anything other than this as input given by user will be invalide input and after confirm of a appointment terminate the session.
