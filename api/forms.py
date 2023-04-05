from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class inputForm(FlaskForm):
    employee_name = StringField("name", validators=[DataRequired()])
    employee_id = IntegerField("id", validators=[DataRequired()])
    submit = SubmitField("submit")
