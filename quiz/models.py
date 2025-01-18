from . import db
from flask_login import UserMixin
import random

# Time-stamped mixin if you want to replicate "model_utils.fields.AutoCreatedField"
from datetime import datetime


class TimeStampedModel:
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Flask-Login requirement: a user model that includes UserMixin
class User(db.Model, UserMixin, TimeStampedModel):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))

    # Relationship to quiz profile, if you want it 1-to-1
    quiz_profile = db.relationship("QuizProfile", backref="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Question(db.Model, TimeStampedModel):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    html = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    maximum_marks = db.Column(db.Float, default=4.0)

    choices = db.relationship("Choice", backref="question", lazy=True)

    def __repr__(self):
        return f"<Question {self.id} {self.html[:20]}>"


class Choice(db.Model, TimeStampedModel):
    __tablename__ = "choices"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    html = db.Column(db.Text)

    def __repr__(self):
        return f"<Choice {self.id} {self.html[:20]}>"


class QuizProfile(db.Model, TimeStampedModel):
    __tablename__ = "quiz_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    total_score = db.Column(db.Float, default=0.0)

    attempts = db.relationship("AttemptedQuestion", backref="quiz_profile", lazy=True)

    def get_new_question(self):
        # Retrieve all question IDs that the user has attempted
        used_questions_ids = [attempt.question_id for attempt in self.attempts]
        # Query for questions that are not in used_questions_ids
        remaining_questions = Question.query.filter(
            ~Question.id.in_(used_questions_ids)
        ).all()
        if remaining_questions:
            return random.choice(remaining_questions)
        return None

    def create_attempt(self, question):
        attempted = AttemptedQuestion(question_id=question.id, quiz_profile_id=self.id)
        db.session.add(attempted)
        db.session.commit()

    def evaluate_attempt(self, attempted_question, selected_choice):
        if attempted_question.question_id != selected_choice.question_id:
            return
        attempted_question.selected_choice_id = selected_choice.id
        if selected_choice.is_correct:
            attempted_question.is_correct = True
            attempted_question.marks_obtained = (
                attempted_question.question.maximum_marks
            )
        db.session.commit()
        self.update_score()

    def update_score(self):
        correct_attempts = AttemptedQuestion.query.filter_by(
            quiz_profile_id=self.id, is_correct=True
        ).all()
        total = sum(a.marks_obtained for a in correct_attempts)
        self.total_score = total
        db.session.commit()

    def __repr__(self):
        return f"<QuizProfile for user_id={self.user_id}>"


class AttemptedQuestion(db.Model, TimeStampedModel):
    __tablename__ = "attempted_questions"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    quiz_profile_id = db.Column(
        db.Integer, db.ForeignKey("quiz_profiles.id"), nullable=False
    )
    selected_choice_id = db.Column(
        db.Integer, db.ForeignKey("choices.id"), nullable=True
    )
    is_correct = db.Column(db.Boolean, default=False)
    marks_obtained = db.Column(db.Float, default=0.0)

    question = db.relationship("Question", lazy=True)
    selected_choice = db.relationship("Choice", lazy=True)

    def __repr__(self):
        return (
            f"<AttemptedQuestion Q={self.question_id} Profile={self.quiz_profile_id}>"
        )
