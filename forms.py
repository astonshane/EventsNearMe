from wtforms import Form, TextField, validators
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import ValidationError
from datetime import datetime

#checks to make sure each date is sometime in the future
def validDate(form, field):
    date_object = datetime.strptime(str(field.data), '%m/%d/%Y %H:%M %p')
    #print date_object

    if date_object < datetime.now():
        raise ValidationError('Event must take place in the future!')

def validTags(form, field):
    #print field.data
    tags = field.data.split(',')
    for tag in tags:
        tag = tag.strip()
        if len(tag) > 20:
            raise ValidationError('Individual tags mush not be longer than 20 characters')

class createEventForm(Form):
    title = TextField('Title', [validators.Length(min=5, max=50), validators.Required()])
    description = TextField('Description', [validators.Length(min=5, max=5000), validators.Required()])
    address = TextField('Address', [validators.Length(min=5, max=500), validators.Required()])
    street_address = TextField('Address', [validators.Length(min=5, max=500), validators.Required()])

    start_datetime = TextField("Start Date/Time", [validDate, validators.Required()])
    end_datetime = TextField("End Date/Time", [validDate, validators.Required()])
    tags = TextField('Tags (Comma Seperated)', [validators.Length(min=1, max=500), validTags, validators.Required()])
