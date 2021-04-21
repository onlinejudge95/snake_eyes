from flask_wtf import Form
from wtforms import IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange


class BetForm(Form):
    guess = IntegerField("Guess", [DataRequired(), NumberRange(min=2, max=12)])
    wagered = IntegerField("Wagered", [DataRequired(), NumberRange(min=1)])
