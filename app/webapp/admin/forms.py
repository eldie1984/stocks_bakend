# Forms for admin blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField
from wtforms.validators import DataRequired,Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Employee

class AlycForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    name = StringField('Name', validators=[DataRequired()])
    contraparte = IntegerField('Contraparte',validators=[Optional()])
    commitent=IntegerField('Comitente', validators=[DataRequired()])
    employee=QuerySelectField(query_factory=lambda: Employee.query.all(),
                                  get_label="email")
    submit = SubmitField('Submit')
