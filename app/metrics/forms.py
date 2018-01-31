from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Regexp

class MetricForm(FlaskForm):
    """
    Form to lookup sysstats metrics
    """
    activity = SelectField('activity', validators=[DataRequired()], id='activity')
    submit = SubmitField('Generate')
