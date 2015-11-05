# WTForms imports
from wtforms import Form, TextField, FloatField, validators
from wtforms.validators import ValidationError
# base python imports
from datetime import datetime


# Ensures that user's can't input words greater than 25 characters
# fixes a bug where words that are too long would render weird
def validWordLength(form, field):
    words = field.data.split(' ')
    for word in words:
        if len(word) > 25:
            raise ValidationError("Can't use words bigger than 25 characters. (Use some spaces!)")


# Validator to check to make sure each date is sometime in the future
def validDate(form, field):
    print "###", str(field.data)
    date_object = datetime.strptime(str(field.data), "%a, %d %b %Y %H:%M:%S %Z")
    if date_object < datetime.now():
        raise ValidationError('Event must take place in the future!')


# Validator to ensure that the tags are not too big
def validTags(form, field):
    tags = field.data.split(',')
    for tag in tags:
        tag = tag.strip()
        if len(tag) > 20:
            raise ValidationError('Individual tags mush not be longer than 20 characters')


# defines all of the form fields needed to create an event
class createEventForm(Form):
    title = TextField('Title', [
        validators.Length(min=5, max=50),
        validators.Required(),
        validWordLength]
    )
    description = TextField('Description', [
        validators.Length(min=5, max=5000),
        validators.Required(),
        validWordLength]
    )
    address = TextField('Address', [
        validators.Length(min=5, max=500),
        validators.Required(),
        validWordLength]
    )
    street_address = TextField('Address', [
        validators.Length(min=5, max=500),
        validators.Required(),
        validWordLength]
    )
    lat = FloatField('Lat')
    lng = FloatField('Lng')

    start_datetime = TextField("Start Date/Time", [validDate, validators.Required()])
    end_datetime = TextField("End Date/Time", [validDate, validators.Required()])
    tags = TextField('Tags (Comma Seperated)', [
        validators.Length(min=1, max=500),
        validTags,
        validators.Required()]
    )


# defines the fields for adding a comment on an event page
class commentForm(Form):
    title = TextField('Title', [
        validators.length(min=1, max=50),
        validators.Required(),
        validWordLength]
    )
    msg = TextField('Comment', [
        validators.length(min=1, max=2000),
        validators.Required(),
        validWordLength]
    )
