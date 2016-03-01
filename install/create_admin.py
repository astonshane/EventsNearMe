from pymongo import MongoClient
import uuid
import md5

client = MongoClient()

db = client.mydb
users = db.users

# create a default admin user with username:password admin1@admin.com:admin

uid = str(uuid.uuid4())
salt = str(uuid.uuid4())
m = md5.md5()
m.update(unicode(salt)+"admin")
hashed = m.hexdigest()

name = {"last": "Doe",
        "first": "John"}
email = "admin1@admin.com"

admin = {
    "_id": uid,
    "hash": hashed,
    "name": name,
    "admin": False,
    "salt": salt,
    "email": email,
    "admin": True,
    "tags": [],
    "picture": "http://lorempixel.com/g/250/250/"
}

users.insert_one(admin)
