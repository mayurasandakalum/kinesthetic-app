from flask_login import UserMixin
from datetime import datetime
import random
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase
cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class User(UserMixin):
    def __init__(self, id, username, email, first_name, last_name, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = password_hash
        self.created = datetime.utcnow()
        self.modified = datetime.utcnow()

    @staticmethod
    def get_by_id(user_id):
        user_doc = db.collection("users").document(str(user_id)).get()
        if user_doc.exists:
            data = user_doc.to_dict()
            return User(user_doc.id, **data)
        return None

    @staticmethod
    def get_by_username(username):
        users = db.collection("users").where("username", "==", username).limit(1).get()
        for user in users:
            data = user.to_dict()
            return User(user.id, **data)
        return None

    def save(self):
        data = {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "password_hash": self.password_hash,
            "created": self.created,
            "modified": self.modified,
        }
        db.collection("users").document(str(self.id)).set(data)


class QuizProfile:
    def __init__(self, user_id, total_score=0.0):
        self.user_id = user_id
        self.total_score = total_score
        self.created = datetime.utcnow()
        self.modified = datetime.utcnow()

    @staticmethod
    def get_by_user_id(user_id):
        profile = db.collection("quiz_profiles").document(str(user_id)).get()
        if profile.exists:
            return QuizProfile(**profile.to_dict())
        return None

    def save(self):
        data = {
            "user_id": self.user_id,
            "total_score": self.total_score,
            "created": self.created,
            "modified": self.modified,
        }
        db.collection("quiz_profiles").document(str(self.user_id)).set(data)

    def get_new_question(self):
        # Get all attempted questions
        attempts = (
            db.collection("attempted_questions")
            .where("user_id", "==", self.user_id)
            .get()
        )
        attempted_ids = [attempt.get("question_id") for attempt in attempts]

        # Get remaining questions
        questions = db.collection("questions").where("is_published", "==", True).get()
        available_questions = [q for q in questions if q.id not in attempted_ids]

        if available_questions:
            question = random.choice(available_questions)
            return Question.from_doc(question)
        return None

    def evaluate_attempt(self, attempted_question, selected_choice):
        # Implementation for Firebase
        # ...existing evaluation logic...
        pass


# Similar implementations for Question, Choice, and AttemptedQuestion classes
# ...
