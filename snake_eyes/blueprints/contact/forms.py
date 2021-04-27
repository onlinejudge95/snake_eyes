from flask_wtf import Form
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms_components import EmailField


class ContactForm(Form):
    email = EmailField("What's your email address?", [DataRequired(), Length(3, 254)])
    message = TextAreaField(
        "What's your question or issue?", [DataRequired(), Length(1, 8192)]
    )
