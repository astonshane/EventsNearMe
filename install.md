Starting with fresh ubuntu install
### Set-up Database
# update package manager
apt-get update
apt-get upgrade
# Install mongo server
apt-get install mongodb -y
# Restart mongo server
service mongodb restart

### Set-up webserver
# Install git so you can pull the project
apt-get install git

# Navigate to location to intall (/home directory suggested)
cd /home

# download project
git clone https://github.com/vbhagwani/EventsNearMe.git

# Make sure python 2.7 is installed
apt-get install python2.7
# Install pip
apt-get install python-pip

# Install requirements from requirements.txt (Prefered method)
pip install -f requirements.txt

# Install requirements manually (Alternative method)
pip install flask-PyMongo
pip install flask-markdown
pip install wtforms
pip install wtforms-components
pip install flask

### Start server
# Change directory to EventsNearMe project folder
cd /home/EventsNearMe

# Start server and let it run in the background
python server.py &

# disown server so its no longer attached to a specific shell sesion
disown



The server is now up and running, you can now navigate to http://<server ip>
to view the site
