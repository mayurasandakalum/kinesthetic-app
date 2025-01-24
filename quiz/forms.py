from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    EmailField,
    RadioField,
    SelectField,
    TextAreaField,
    IntegerField,
    FloatField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Optional, NumberRange


class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class QuizForm(FlaskForm):
    choice_pk = RadioField("Choice", validators=[DataRequired()])


class SubQuestionForm(FlaskForm):
    text = TextAreaField("Sub-Question Text", validators=[DataRequired()])
    instructions = TextAreaField("Instructions")
    correct_answer = StringField("Correct Answer", validators=[DataRequired()])
    answer_type = SelectField(
        "Answer Type",
        choices=[("number", "Number"), ("time", "Time")],
        validators=[DataRequired()],
    )
    min_value = FloatField("Minimum Value", validators=[Optional()])
    max_value = FloatField("Maximum Value", validators=[Optional()])
    time_format = StringField("Time Format")
    difficulty_level = IntegerField(
        "Difficulty Level", validators=[NumberRange(min=1, max=5)], default=1
    )
    points = IntegerField("Points", validators=[NumberRange(min=1)], default=1)
    hint = TextAreaField("Hint")
    submit = SubmitField("Save Sub-Question")

    class Meta:
        csrf = False  # Disable CSRF for nested form


class QuestionForm(FlaskForm):
    text = TextAreaField("Question Text", validators=[DataRequired()])
    answer_method = SelectField(
        "Answer Method",
        choices=[
            ("abacus", "Abacus"),
            ("analog_clock", "Analog Clock"),
            ("digital_clock", "Digital Clock"),
        ],
        validators=[DataRequired()],
    )
    is_published = BooleanField("Published")
    sub_questions = FieldList(FormField(SubQuestionForm), min_entries=1)
    submit = SubmitField("Save Question")
