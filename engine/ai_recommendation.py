import openai
from typing import List, Dict
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIRecommendationEngine:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please add it to your .env file.")
        openai.api_key = self.api_key

    def generate_module_test(self, module_content: str, difficulty_level: str) -> Dict:
        """Generate a test for a specific module based on its content and difficulty level."""
        prompt = f"""
        Create a multiple choice test based on the following module content.
        Difficulty level: {difficulty_level}
        Module content: {module_content}
        
        Generate 5 multiple choice questions with 4 options each.
        Format the response as a JSON with the following structure:
        {{
            "questions": [
                {{
                    "question": "question text",
                    "options": ["option1", "option2", "option3", "option4"],
                    "correct_answer": "correct option",
                    "explanation": "explanation of the correct answer"
                }}
            ]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating test: {e}")
            return {"questions": []}

    def adjust_module_difficulty(self, pre_assessment_score: int, module_content: str) -> str:
        """Adjust the difficulty level of module content based on pre-assessment score."""
        difficulty_levels = {
            "beginner": (0, 3),
            "intermediate": (4, 7),
            "advanced": (8, 10)
        }
        
        # Determine difficulty level based on score
        difficulty = "intermediate"  # default
        for level, (min_score, max_score) in difficulty_levels.items():
            if min_score <= pre_assessment_score <= max_score:
                difficulty = level
                break

        prompt = f"""
        Adjust the following educational content to {difficulty} difficulty level.
        Original content: {module_content}
        
        Make the content more suitable for {difficulty} level learners while maintaining the core concepts.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error adjusting difficulty: {e}")
            return module_content

    def recommend_next_modules(self, pre_assessment_score: int, completed_modules: List[str], 
                             all_modules: List[Dict]) -> List[Dict]:
        """Recommend the next set of modules based on pre-assessment score and completed modules."""
        # Sort modules by difficulty level
        difficulty_weights = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }
        
        # Filter out completed modules
        available_modules = [m for m in all_modules if m['id'] not in completed_modules]
        
        # Sort modules based on difficulty and pre-assessment score
        sorted_modules = sorted(
            available_modules,
            key=lambda x: abs(difficulty_weights.get(x.get('difficulty', 'intermediate'), 2) - 
                            (pre_assessment_score / 3.33))  # Normalize score to 1-3 range
        )
        
        return sorted_modules[:3]  # Return top 3 recommended modules 