from wtforms import Form, TextField, validators
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField

def validDate(form, field):
    print field.data

    # if len(field.data) > 50:
    #    raise ValidationError('Field must be less than 50 characters')

class createEventForm(Form):
    title = TextField('Title', [validators.Length(min=5, max=50)])
    description = TextField('Description', [validators.Length(min=5, max=500)])
    start_datetime = TextField("Start Date/Time", [validDate])
    end_datetime = TextField("End Date/Time", [validDate])
