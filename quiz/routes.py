from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .models import db, User, QuizProfile, Question, AttemptedQuestion, Choice
from .forms import UserLoginForm, RegistrationForm

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
    # Let's fetch top 500
    top_quiz_profiles = (
        QuizProfile.query.order_by(QuizProfile.total_score.desc()).limit(500).all()
    )
    total_count = len(top_quiz_profiles)
    return render_template(
        "quiz/leaderboard.html",
        top_quiz_profiles=top_quiz_profiles,
        total_count=total_count,
    )


@quiz_blueprint.route("/play", methods=["GET", "POST"])
@login_required
def play():
    quiz_profile = current_user.quiz_profile
    if not quiz_profile:
        # If user has no quiz_profile yet, create one
        quiz_profile = QuizProfile(user_id=current_user.id)
        db.session.add(quiz_profile)
        db.session.commit()

    if request.method == "POST":
        question_pk = request.form.get("question_pk")
        attempted_question = AttemptedQuestion.query.filter_by(
            quiz_profile_id=quiz_profile.id, question_id=question_pk
        ).first()
        choice_pk = request.form.get("choice_pk")
        selected_choice = Choice.query.get(choice_pk)
        quiz_profile.evaluate_attempt(attempted_question, selected_choice)
        return redirect(
            url_for(
                "quiz.submission_result", attempted_question_pk=attempted_question.id
            )
        )
    else:
        question = quiz_profile.get_new_question()
        if question is not None:
            quiz_profile.create_attempt(question)
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
        user = User.query.filter_by(username=form.username.data).first()
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
        # Create user
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password_hash=hashed_pw,
        )
        db.session.add(new_user)
        db.session.commit()

        # Optionally create QuizProfile right away
        quiz_profile = QuizProfile(user_id=new_user.id)
        db.session.add(quiz_profile)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("quiz.login"))
    return render_template("quiz/registration.html", form=form, title="Create account")


@quiz_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("quiz.home"))
