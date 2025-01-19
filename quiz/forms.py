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


class QuestionForm(FlaskForm):
    text = TextAreaField("Main Question Text", validators=[DataRequired()])
    answer_method = SelectField(
        "Answer Method", choices=[], validators=[DataRequired()]
    )
    is_published = BooleanField("Published")
    submit = SubmitField("Save Question")

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.answer_method.choices = AnswerMethod.CHOICES


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
