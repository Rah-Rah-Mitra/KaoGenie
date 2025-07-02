# config/exam_presets.py

"""
This file contains pre-configured presets for exam generation.
Each key is a preset name that can be passed to the API.
The value is a list of question specifications that the pipeline will use.
"""

PRESETS = {
    "primary_math_quiz": [
        {"question_type": "MCQ", "count": 5, "prompt": "Focus on basic arithmetic and geometry definitions."},
        {"question_type": "Math Problem", "count": 3, "prompt": "Create simple word problems involving addition and subtraction."},
    ],
    "university_physics_concepts": [
        {"question_type": "Open-Ended", "count": 4, "prompt": "Generate questions requiring detailed explanations of core physics principles like Newton's Laws or thermodynamics."},
        {"question_type": "MCQ", "count": 6, "prompt": "Create questions that test conceptual understanding rather than complex calculations."},
    ],
    "us_history_review": [
        {"question_type": "MCQ", "count": 10, "prompt": "Focus on key dates, figures, and events in US history."},
        {"question_type": "Open-Ended", "count": 2, "prompt": "Ask for a short analysis of the impact of a major historical event."},
    ]
}