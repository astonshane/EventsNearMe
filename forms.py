from wtforms import Form, TextField, validators
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import ValidationError
from datetime import datetime


# Validator to check to make sure each date is sometime in the future
def validDate(form, field):
    date_object = datetime.strptime(str(field.data), '%m/%d/%Y %I:%M %p')
    if date_object < datetime.now():
        raise ValidationError('Event must take place in the future!')


# Validator to ensure that the tags are not too big
def validTags(form, field):
    #print field.data
    tags = field.data.split(',')
    for tag in tags:
        tag = tag.strip()
        if len(tag) > 20:
            raise ValidationError('Individual tags mush not be longer than 20 characters')


# defines all of the form fields needed to create an event
class createEventForm(Form):
    title = TextField('Title', [validators.Length(min=5, max=50), validators.Required()])
    description = TextField('Description', [validators.Length(min=5, max=5000), validators.Required()])
    address = TextField('Address', [validators.Length(min=5, max=500), validators.Required()])
    street_address = TextField('Address', [validators.Length(min=5, max=500), validators.Required()])

    start_datetime = TextField("Start Date/Time", [validDate, validators.Required()])
    end_datetime = TextField("End Date/Time", [validDate, validators.Required()])
    tags = TextField('Tags (Comma Seperated)', [validators.Length(min=1, max=500), validTags, validators.Required()])


class commentForm(Form):
    title = TextField('Title', [validators.length(min=1, max=50), validators.Required()])
    msg = TextField('Comment', [validators.length(min=1, max=2000), validators.Required()])
