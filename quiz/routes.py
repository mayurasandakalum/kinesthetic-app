from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import firestore

from .models import User, QuizProfile, Question, AttemptedQuestion, Choice
from .forms import UserLoginForm, RegistrationForm, QuizForm

db = firestore.client()

quiz_blueprint = Blueprint(
    "quiz", __name__, template_folder="../templates/quiz", static_folder="../static"
)


@quiz_blueprint.route("/")
def home():
    return render_template("quiz/home.html")


@quiz_blueprint.route("/user-home")
@login_required
def user_home():
    return render_template("quiz/user_home.html")


@quiz_blueprint.route("/leaderboard")
def leaderboard():
    # Get all quiz profiles and sort by total_score
    profiles_ref = (
        db.collection("quiz_profiles")
        .order_by("total_score", direction=firestore.Query.DESCENDING)
        .limit(500)
    )
    profiles = profiles_ref.get()
    top_quiz_profiles = [QuizProfile(**profile.to_dict()) for profile in profiles]
    total_count = len(top_quiz_profiles)
    return render_template(
        "quiz/leaderboard.html",
        top_quiz_profiles=top_quiz_profiles,
        total_count=total_count,
    )


@quiz_blueprint.route("/play", methods=["GET", "POST"])
@login_required
def play():
    quiz_profile = QuizProfile.get_by_user_id(current_user.id)
    if not quiz_profile:
        quiz_profile = QuizProfile(user_id=current_user.id)
        quiz_profile.save()

    form = QuizForm()
    question = quiz_profile.get_new_question()
    if question:
        choices = Choice.get_by_question(question.id)
        form.choice_pk.choices = [(str(choice.id), choice.text) for choice in choices]

    if request.method == "POST":
        question_id = request.form.get("question_pk")
        choice_id = request.form.get("choice_pk")
        attempted = AttemptedQuestion(
            user_id=current_user.id,
            question_id=question_id,
            selected_choice_id=choice_id,
        )
        attempted.save()
        return redirect(url_for("quiz.play"))

    return render_template("quiz/play.html", question=question, form=form)


@quiz_blueprint.route("/submission-result/<int:attempted_question_pk>")
@login_required
def submission_result(attempted_question_pk):
    attempted_question = AttemptedQuestion.query.get_or_404(attempted_question_pk)
    return render_template(
        "quiz/submission_result.html", attempted_question=attempted_question
    )


@quiz_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("quiz.home"))

    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for("quiz.user_home"))
        else:
            flash("Invalid username/password!", "danger")
    return render_template("quiz/login.html", form=form, title="Login")


@quiz_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("quiz.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user:
            flash("Username already exists")
            return redirect(url_for("quiz.register"))

        password_hash = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password_hash=password_hash,
        )

        new_user.save()

        quiz_profile = QuizProfile(user_id=new_user.id)
        quiz_profile.save()

        flash("Registration successful!")
        return redirect(url_for("quiz.login"))

    return render_template("quiz/registration.html", form=form, title="Register")


@quiz_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("quiz.home"))
