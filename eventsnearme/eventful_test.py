import eventful
import json

api = eventful.API(json.loads(open('config.json').read())['eventful_api_key'])

# If you need to log in:
# api.login('username', 'password')

events = api.call('/events/search', l='12180', within='10', units='miles')
for event in events['events']['event']:
    # print "%s at %s" % (event['title'], event['venue_name'])
    print event['title']
    print event['venue_name']
    print event['venue_address']
    print event['description']
    print event['start_time']
    print ""
