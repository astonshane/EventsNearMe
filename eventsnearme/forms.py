# WTForms imports
from wtforms import Form, TextField, PasswordField, FloatField, RadioField, validators
from wtforms.validators import ValidationError
# base python imports
from datetime import datetime


# Ensures that user's can't input words greater than 25 characters
# fixes a bug where words that are too long would render weird
def validWordLength(form, field):
    words = field.data.split(' ')
    for word in words:
        if "http" not in word and len(word) > 25:
            raise ValidationError("Can't use words bigger than 25 characters. (Use some spaces!)")


# Validator to check to make sure each date is sometime in the future
def validDate(form, field):
    date_object = datetime.strptime(str(field.data), "%m/%d/%Y, %I:%M:%S %p")
    if date_object < datetime.now():
        raise ValidationError('Event must take place in the future!')


# Validator to ensure that the tags are not too big
def validTags(form, field):
    tags = field.data.split(',')
    for tag in tags:
        tag = tag.strip()
        if len(tag) > 20:
            raise ValidationError('Individual tags mush not be longer than 20 characters')


# Validator to ensure that the item names are not too big
def validItems(form, field):
    items = field.data.strip().split(',')
    for item in items:
        item = item.strip()
        if len(item) > 20:
            raise ValidationError("Individual items mush not be longer than 20 characters")


# Validator to ensure that any links given as an event picture have the right extension type
def validPicture(form, field):
    valid_extensions = ['jpg', 'png', 'gif']
    extension = field.data.split('.')[-1]
    if extension not in valid_extensions and "lorempixel" not in field.data:
        raise ValidationError(
            'Image must be one of the following file types:' + str(valid_extensions)
        )


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
    master = TextField('Description', [
        validators.Required()]
    )
    address = TextField('Address', [
        validators.Length(min=5, max=500),
        validators.Required(),
        validWordLength]
    )
    street_address = TextField('Address', [
        validators.Length(min=5, max=500),
        validators.Required(""),
        validWordLength]
    )
    advice_tips = TextField('Guest Advice', [
        validators.Optional(),
        validWordLength]
    )
    picture = TextField('Picture', [
        validators.Optional(),
        validPicture]
    )
    lat = FloatField('Lat', [validators.Required("Google Autocomplete not used")])
    lng = FloatField('Lng', [validators.Required("Google Autocomplete not used")])

    start_datetime = TextField("Start Date/Time", [validDate, validators.Required()])
    end_datetime = TextField("End Date/Time", [validDate, validators.Required()])
    tags = TextField('Tags (Comma Seperated)', [
        validators.Length(min=1, max=500),
        validTags,
        validators.Required()]
    )
    items = TextField('Items (Comma Seperated)', [validators.Length(min=0, max=500), validItems])


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


# defines the fields for loging in a user
class loginForm(Form):
    email = TextField('Email', [
        validators.Required(),
        validators.Email()]
    )
    password = PasswordField('Password', [validators.Required()])


# defines the fields for registering a user
class registerForm(Form):
    fname = TextField('First Name', [validators.Required()])
    lname = TextField('Last Name', [validators.Required()])
    email = TextField('Email', [
        validators.Required(),
        validators.Email()]
    )
    password1 = PasswordField('Password1', [
        validators.Required(),
        validators.EqualTo('password2', message='Passwords must match')]
    )
    password2 = PasswordField('Password2', [validators.Required()])


# defines the fields for reseting a user's password
class forgotPasswordForm(Form):
    email = TextField('Email', [
        validators.Required(),
        validators.Email()]
    )


# defines the fields for updating user profiles
class updateProfileForm(Form):
    fname = TextField('First Name', [validators.Required()])
    lname = TextField('Last Name', [validators.Required()])
    email = TextField('Email', [
        validators.Required(),
        validators.Email()]
    )
    picture = TextField('Picture', [
        validators.Optional(),
        validPicture]
    )

class changePasswordForm(Form):
    password1 = PasswordField('Password1', [
        validators.Required(),
        validators.EqualTo('password2', message='Passwords must match')]
    )
    password2 = PasswordField('Password2', [validators.Required()])

# defines the fields for adding tags to a user
class addUserTagsForm(Form):
    newTag = TextField('newTag', [
        validators.Required(),
        validators.length(min=1, max=50),
        validWordLength]
    )
