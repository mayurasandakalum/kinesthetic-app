from flask_login import UserMixin
from datetime import datetime
import random
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
import os
import uuid  # Add this import

# Get the absolute path to the credentials file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Remove one dirname call
cred_path = os.path.join(project_root, "serviceAccountKey.json")

print(f"Looking for credentials at: {cred_path}")  # Debug print

# Initialize Firebase
cred = credentials.Certificate(cred_path)
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    # App already initialized
    pass
db = firestore.client()


class User(UserMixin):
    def __init__(self, username, email, first_name, last_name, password_hash, id=None):
        self.id = id if id else str(uuid.uuid4())
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
            return User(
                username=data.get("username"),
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                password_hash=data.get("password_hash"),
                id=user_doc.id,
            )
        return None

    @staticmethod
    def get_by_username(username):
        users = db.collection("users").where("username", "==", username).limit(1).get()
        for user in users:
            data = user.to_dict()
            return User(
                username=data.get("username"),
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                password_hash=data.get("password_hash"),
                id=user.id,
            )
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


class Question:
    def __init__(self, id=None, text="", is_published=False):
        self.id = id
        self.text = text
        self.is_published = is_published
        self.created = datetime.utcnow()
        self.modified = datetime.utcnow()

    @staticmethod
    def from_doc(doc):
        data = doc.to_dict()
        question = Question(
            id=doc.id,
            text=data.get("text", ""),
            is_published=data.get("is_published", False),
        )
        question.created = data.get("created", datetime.utcnow())
        question.modified = data.get("modified", datetime.utcnow())
        return question

    def save(self):
        data = {
            "text": self.text,
            "is_published": self.is_published,
            "created": self.created,
            "modified": self.modified,
        }
        if self.id:
            db.collection("questions").document(self.id).set(data)
        else:
            ref = db.collection("questions").add(data)
            self.id = ref[1].id


class Choice:
    def __init__(self, id=None, question_id=None, text="", is_correct=False):
        self.id = id
        self.question_id = question_id
        self.text = text
        self.is_correct = is_correct
        self.created = datetime.utcnow()
        self.modified = datetime.utcnow()

    @staticmethod
    def get_by_question(question_id):
        choices = db.collection("choices").where("question_id", "==", question_id).get()
        return [Choice.from_doc(doc) for doc in choices]

    @staticmethod
    def from_doc(doc):
        data = doc.to_dict()
        choice = Choice(
            id=doc.id,
            question_id=data.get("question_id"),
            text=data.get("text", ""),
            is_correct=data.get("is_correct", False),
        )
        choice.created = data.get("created", datetime.utcnow())
        choice.modified = data.get("modified", datetime.utcnow())
        return choice


class AttemptedQuestion:
    def __init__(self, user_id, question_id, selected_choice_id=None, is_correct=False):
        self.user_id = user_id
        self.question_id = question_id
        self.selected_choice_id = selected_choice_id
        self.is_correct = is_correct
        self.attempted_at = datetime.utcnow()

    def save(self):
        data = {
            "user_id": self.user_id,
            "question_id": self.question_id,
            "selected_choice_id": self.selected_choice_id,
            "is_correct": self.is_correct,
            "attempted_at": self.attempted_at,
        }
        db.collection("attempted_questions").add(data)
