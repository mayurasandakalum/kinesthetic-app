import json
import os
from firebase_admin import firestore
from .models import Question, Choice


def load_initial_questions():
    db = firestore.client()

    # Check if questions already exist
    existing_questions = db.collection("questions").limit(1).get()
    if len(list(existing_questions)) > 0:
        print("Questions already exist in Firebase")
        return

    # Load questions from JSON
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "initial_questions.json")

    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Add questions and choices to Firebase
        for q_data in data["questions"]:
            # Create question
            question = Question(
                text=q_data["text"], is_published=q_data["is_published"]
            )
            question.save()

            # Create choices for the question
            for c_data in q_data["choices"]:
                choice = Choice(
                    question_id=question.id,
                    text=c_data["text"],
                    is_correct=c_data["is_correct"],
                )
                choice.save()

        print("Successfully loaded initial questions into Firebase")
    except Exception as e:
        print(f"Error loading initial questions: {str(e)}")
