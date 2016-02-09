# flask imports
from flask import request, session
# base python imports
import base64
import json


# User class to hold user's info
class User:
    def __init__(self, uid, mongo):
        self.id = uid  # set the user id
        user = mongo.db.users.find({'_id': uid})  # look for the user in the DB
        user = user[0]
        # set the user's name from the DB
        self.first_name = user['name']['first']
        self.last_name = user['name']['last']

    # function to return the full name of the User
    def fullName(self):
        # low coupling: could in future change first_name or last_name and add stuff like
        #   a middle name, name prefix, or name suffix and it would be populated everywhere
        #   simply by changing this method
        return "%s %s" % (self.first_name, self.last_name)


# checkLoggedIn determines if the user is currently logged in
# returns true and sets session name / id if logged in
def checkLoggedIn(mongo):
    return session.get('logged_in', False)


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
