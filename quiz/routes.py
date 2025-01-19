from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import firestore

from .models import (
    User,
    QuizProfile,
    Question,
    AttemptedQuestion,
    SubQuestion,
)  # Update import
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
    if request.method == "POST":
        question_id = request.form.get("question_pk")
        answer_method = request.form.get("answer_method")
        sub_question_id = request.form.get("sub_question_id")

        # Get all the captured images
        captured_images = {}
        for key in request.form:
            if key.startswith("captured_image_webcam"):
                captured_images[key] = request.form[key]

        # Get the sub-question to check correct answer
        sub_question_ref = (
            db.collection("sub_questions").document(sub_question_id).get()
        )
        if sub_question_ref.exists:
            sub_question_data = sub_question_ref.to_dict()
            correct_answer = sub_question_data.get("correct_answer")
            points = sub_question_data.get("points", 1)

            # TODO: Implement image processing logic here
            # is_correct = process_answer(answer_method, captured_images, correct_answer)
            is_correct = True  # Temporary, replace with actual logic

            # Save attempt
            attempted = AttemptedQuestion(
                user_id=current_user.id,
                question_id=question_id,
                sub_question_id=sub_question_id,
                is_correct=is_correct,
                images=captured_images,
            )
            attempted.save()

            # Update score if correct
            if is_correct:
                quiz_profile = QuizProfile.get_by_user_id(current_user.id)
                if quiz_profile:
                    quiz_profile.total_score += points
                    quiz_profile.save()

        return redirect(url_for("quiz.play"))

    # Get a new question
    quiz_profile = QuizProfile.get_by_user_id(current_user.id)
    if not quiz_profile:
        quiz_profile = QuizProfile(user_id=current_user.id)
        quiz_profile.save()

    question = quiz_profile.get_new_question()
    return render_template("quiz/play.html", question=question)


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
