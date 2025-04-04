import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import Dict, List

load_dotenv()

class AppointmentSystem:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.sessions = {}
        self.calendar = {}
    
    def handle_request(self, user_id: str, user_input: str = None) -> Dict:
        """Handle all interactions through a single method"""
        # Initialize new session if doesn't exist
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'step': 'get_name',
                'data': {}
            }
            return {
                'message': 'Welcome! Please enter your full name:',
                'next_step': 'get_age'
            }
        
        session = self.sessions[user_id]
        
        # Process based on current step
        if session['step'] == 'get_name':
            session['data']['name'] = user_input
            session['step'] = 'get_age'
            return {
                'message': 'Please enter your age:',
                'next_step': 'get_gender'
            }
            
        elif session['step'] == 'get_age':
            session['data']['age'] = user_input
            session['step'] = 'get_gender'
            return {
                'message': 'Please enter your gender:',
                'next_step': 'select_doctor'
            }
            
        elif session['step'] == 'get_gender':
            session['data']['gender'] = user_input
            session['step'] = 'select_doctor'
            doctors = self._get_available_doctors()
            return {
                'message': 'Select a doctor:',
                'options': doctors,
                'next_step': 'select_time'
            }
            
        elif session['step'] == 'select_doctor':
            session['data']['doctor'] = user_input
            session['step'] = 'select_time'
            times = self._get_available_times()
            return {
                'message': 'Select appointment time:',
                'options': times,
                'next_step': 'confirm'
            }
            
        elif session['step'] == 'select_time':
            session['data']['time'] = user_input
            session['step'] = 'confirm'
            return {
                'message': f"Confirm booking with {session['data']['doctor']} at {session['data']['time']}? (yes/no)",
                'next_step': 'complete'
            }
            
        elif session['step'] == 'confirm':
            if user_input.lower() == 'yes':
                result = self._create_appointment(user_id)
                del self.sessions[user_id]  # Clear session
                return result
            else:
                del self.sessions[user_id]
                return {'message': 'Booking cancelled.'}
    
    def _get_available_doctors(self) -> List[str]:
        """Demo doctor list - extend with your actual logic"""
        return ["Dr. Smith", "Dr. Johnson", "Dr. Lee","Dr. Shah"]
    
    def _get_available_times(self) -> List[str]:
        """Demo available times"""
        return [
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 10:00'),
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 14:00'),
            (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d 11:00')
        ]
    
    def _create_appointment(self, user_id: str) -> Dict:
        """Finalize booking"""
        data = self.sessions[user_id]['data']
        self.calendar[data['time']] = {
            'patient': data['name'],
            'doctor': data['doctor'],
            'details': {
                'age': data['age'],
                'gender': data['gender']
            }
        }
        return {
            'status': 'success',
            'message': f"Appointment booked for {data['name']} with {data['doctor']} at {data['time']}",
            'appointment': self.calendar[data['time']]
        }
    
# now i just want ki agent will not book the same appointment date and time for other users 
# and also i want to add a cancel appointment functionality
# and also i want to add a reschedule appointment functionality
# anything other than this as input given by user will be invalide input and after confirm of a appointment terminate the session 