from wtforms import Form, TextField, validators
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField

class createEventForm(Form):
    title = TextField('Title', [validators.Length(min=5, max=50)])
    description = TextField('Description')
    start_date = DateField('Start date', format='%m-%d-%Y')
    start_time = TimeField('Start time')
