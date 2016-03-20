# manage.py

from flask.ext.script import Manager

from server import app

manager = Manager(app)


@manager.command
def hello(name):
    "just say hello"
    print "hello"


@manager.command
def createAdmin():
    "Create an Admin User"
    print "Creating Admin User..."

if __name__ == "__main__":
    manager.run()
