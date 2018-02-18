from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Regexp

class CaseSearchForm(FlaskForm):
    """
    Form to lookup a case and get the sosreports
    """
    casenum = StringField('casenum', 
                          validators=[DataRequired(),
                                      Regexp('^0[0-9]{7}$',
                                      message="Invalid case number")],
                                      id='casenum') 
    submit = SubmitField('Search')
