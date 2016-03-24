# flask imports
from flask import request, session
# base python imports
import base64
import json
import uuid
import md5


# User class to hold user's info
class User:
    def __init__(self, uid, mongo):
        try:
            self.id = uid  # set the user id
            user = mongo.db.users.find({'_id': uid})  # look for the user in the DB
            user = user[0]
            self.email = user['email']
            # set the user's name from the DB
            self.first_name = user['name']['first']
            self.last_name = user['name']['last']

            self.admin = user.get('admin', False)
            self.tags = user.get('tags', [])

            self.picture = user.get('picture', "http://lorempixel.com/g/250/250/")

            self.valid = True
        except:
            self.valid = False

    def __str__(self):
        return self.fullName()

    # function to return the full name of the User
    def fullName(self):
        # low coupling: could in future change first_name or last_name and add stuff like
        #   a middle name, name prefix, or name suffix and it would be populated everywhere
        #   simply by changing this method
        return "%s %s" % (self.first_name, self.last_name)


# checkLoggedIn determines if the user is currently logged in
# returns true and sets session name / id if logged in
def checkLoggedIn(mongo):
    loggedIn = session.get('logged_in', False)
    if loggedIn:
        user = mongo.db.users.find({'_id': session['uid']})[0]
        if user.get('admin', False):
            session['admin'] = True
        else:
            session['admin'] = False
        session.modified = True

    # also, add a cookie for the sitename...
    config = json.loads(open('config.json').read())
    session['sitename'] = config['sitename']
    session.modified = True

    return loggedIn


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


# get all of the events to be displayed on the main map page or event list page
def generateUsers(mongo):
    new_users = []

    users = mongo.db.users.find({})
    for u in users:
        new_users.append(User(u['_id'], mongo))

    return new_users


def changePassword(uid, password, mongo):
    salt = str(uuid.uuid4())
    m = md5.md5()
    m.update(unicode(salt)+password)
    hashed = m.hexdigest()
    return mongo.db.users.update(
        {"_id": uid}, {
            "$set": {
                "salt": salt,
                "hash": hashed
            }
        }
    )
