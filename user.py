from flask import request, session
import base64
import json


class User:
    def __init__(self, uid, mongo):
        self.id = uid
        try:
            print "HERE"
            user = mongo.db.users.find({'_id': uid})
            print "GOT IT"
            user = user[0]
            self.first_name = user['name']['first']
            self.last_name = user['name']['last']
        except:
            self.first_name = "NO"
            self.last_name = "NAME"

    def fullName(self):
        return "%s %s" % (self.first_name, self.last_name)


# checkLoggedIn determines if the user is currently logged in
# returns true and sets session name / id if logged in
def checkLoggedIn(mongo):
    if request.cookies.get('fbsr_1055849787782314') != None:
        session['logged_in'] = True
        user_id = parseSignedRequest(request.cookies.get('fbsr_1055849787782314'))

        user = mongo.db.users.find({'_id': user_id})[0]
        name = user['name']
        session['name'] = "%s %s" % (name['first'], name['last'])
        session['uid'] = user_id

        session.modified = True
        return True

    else:
        session['logged_in'] = False
        session.modified = True
        return False



# returns the user's id (from the FB cookie)
def parseSignedRequest(sr):
    [encoded_signiture, payload] = sr.split('.')
    encoded_signiture = encoded_signiture + "="*(4 - len(encoded_signiture) % 4)
    payload = payload + "="*(4-len(payload) % 4)

    # signiture = base64.urlsafe_b64decode(str(encoded_signiture))
    data = json.loads(base64.urlsafe_b64decode(str(payload)))
    return data['user_id']

def nameFromId(id, mongo):
    user = ""
    try:
        user = mongo.db.users.find({'_id': id})[0]
    except:
        return None
    name = user['name']
    return "%s %s" % (name['first'], name['last'])
