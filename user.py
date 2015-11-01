from flask import request, session
import base64
import json

# User class to hold user's info
class User:
    def __init__(self, uid, mongo):
        self.id = uid #set the user id
        try:
            user = mongo.db.users.find({'_id': uid}) # look for the user in the DB
            user = user[0]
            # set the user's name from the DB
            self.first_name = user['name']['first']
            self.last_name = user['name']['last']
        except:
            self.first_name = "NO"
            self.last_name = "NAME"

    # function to return the full name of the User
    def fullName(self):
        return "%s %s" % (self.first_name, self.last_name)


# checkLoggedIn determines if the user is currently logged in
# returns true and sets session name / id if logged in
def checkLoggedIn(mongo):
    # the user must have the following FB cookie to be logged in
    if request.cookies.get('fbsr_1055849787782314') != None:
        session['logged_in'] = True # set the session var to true (used in the templates)
        # parse the signedRequest data stored in the cookie to pull out the user id
        user_id = parseSignedRequest(request.cookies.get('fbsr_1055849787782314'))

        # get the user with the above id in the DB
        user = User(user_id, mongo)
        # set the session vars used in the templates
        session['name'] = user.fullName()
        session['uid'] = user_id

        session.modified = True
        return True

    else:
        # not logged in
        session['logged_in'] = False
        session.modified = True
        return False


# returns the user's id (from the FB cookie)
def parseSignedRequest(sr):
    # split the request data over '.' into the encoded signiture and the payload
    [_, payload] = sr.split('.')
    # add padding characters to the payload
    payload = payload + "="*(4-len(payload) % 4)
    # decode the payload to json
    data = json.loads(base64.urlsafe_b64decode(str(payload)))
    return data['user_id']  # return the user_id from the json object


# retuns a user's name from their id
def nameFromId(uid, mongo):
    user = User(uid, mongo)
    return user.fullName()
