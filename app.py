# # app.py
# from flask import Flask, request, jsonify
# from agents.recommendation_agent import HealthTipsService
# from agents.appointment_agent import AppointmentSystem
# from agents.diagnosis_agent import DiagnosisAgent


# app = Flask(__name__)
# health_service = HealthTipsService()

# @app.route('/health-tips', methods=['POST'])
# def get_health_tips():
#     """Endpoint for generating health tips"""
#     data = request.json
    
#     # Validate required fields
#     if not data or 'diagnosis' not in data:
#         return jsonify({"error": "Diagnosis is required"}), 400
    
#     # Generate tips
#     tips = health_service.generate_health_tips(
#         diagnosis=data['diagnosis'],
#         user_context=data.get('user_context')
#     )
    
#     return jsonify({
#         "diagnosis": data['diagnosis'],
#         "tips": tips
#     })

# scheduler = AppointmentSystem()

# @app.route('/appointment', methods=['POST'])
# def handle_appointment():
#     data = request.json
#     user_id = data.get('user_id')
#     user_input = data.get('input')
    
#     if not user_id:
#         return jsonify({'error': 'user_id is required'}), 400
        
#     response = scheduler.handle_request(user_id, user_input)
#     return jsonify(response)

# try:
#     agent = DiagnosisAgent(data_path="symptom_disease.csv")
#     print("Diagnosis agent initialized successfully")
# except Exception as e:
#     print(f"Failed to initialize agent: {str(e)}")
#     agent = None

# @app.route('/diagnose', methods=['POST'])
# def diagnose():
#     """Endpoint for symptom-based diagnosis"""
#     if agent is None:
#         return jsonify({"error": "Diagnosis system unavailable", "reason": "Model not loaded"}), 503
    
#     data = request.json
#     if not data or 'symptoms' not in data:
#         return jsonify({"error": "Symptoms list required", "example": {"symptoms": ["fever", "cough"]}}), 400
    
#     try:
#         result = agent.get_diagnosis(data['symptoms'])
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({"error": "Diagnosis failed", "details": str(e)}), 500

# @app.route('/analyze', methods=['POST'])
# def analyze():
#     """Endpoint for natural language analysis"""
#     if agent is None:
#         return jsonify({"error": "Diagnosis system unavailable"}), 503
        
#     data = request.json
#     if not data or 'description' not in data:
#         return jsonify({"error": "Description required", "example": {"description": "I have fever and headache"}}), 400
    
#     try:
#         result = agent.analyze_symptom_description(data['description'])
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({"error": "Analysis failed", "details": str(e)}), 500

# @app.route('/health')
# def health_check():
#     """Service health check"""
#     status = {
#         "model_loaded": agent is not None and agent.model is not None,
#         "ai_configured": agent is not None and agent.ai_model is not None
#     }
#     return jsonify(status)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify, render_template
from agents.recommendation_agent import HealthTipsService
from agents.appointment_agent import AppointmentSystem
from agents.diagnosis_agent import DiagnosisAgent
import os
print("HEllo World")
app = Flask(__name__)
health_service = HealthTipsService()
scheduler = AppointmentSystem()

# Initialize diagnosis agent
try:
    agent = DiagnosisAgent(data_path=os.path.join('data', 'symptom_disease.csv'))
    print("Diagnosis agent initialized successfully")
except Exception as e:
    print(f"Failed to initialize agent: {str(e)}")
    agent = None

# Serve main page
@app.route('/')
def index():
    return render_template('index.html')

# API Endpoints (keep your existing ones)
@app.route('/health-tips', methods=['POST'])
def get_health_tips():
    data = request.json
    if not data or 'diagnosis' not in data:
        return jsonify({"error": "Diagnosis is required"}), 400
    tips = health_service.generate_health_tips(
        diagnosis=data['diagnosis'],
        user_context=data.get('user_context')
    )
    return jsonify({"diagnosis": data['diagnosis'], "tips": tips})

@app.route('/appointment', methods=['POST'])
def handle_appointment():
    data = request.json
    if not data.get('user_id'):
        return jsonify({'error': 'user_id is required'}), 400
    response = scheduler.handle_request(data['user_id'], data.get('input'))
    return jsonify(response)

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if not agent:
        return jsonify({"error": "Diagnosis system unavailable"}), 503
    data = request.json
    if not data or 'symptoms' not in data:
        return jsonify({"error": "Symptoms list required"}), 400
    result = agent.get_diagnosis(data['symptoms'])
    return jsonify(result)

@app.route('/analyze', methods=['POST'])
def analyze():
    if not agent:
        return jsonify({"error": "Diagnosis system unavailable"}), 503
    data = request.json
    if not data or 'description' not in data:
        return jsonify({"error": "Description required"}), 400
    result = agent.analyze_symptom_description(data['description'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)