import requests
import json

url = 'http://events.rpi.edu:7070/feeder/main/eventsFeed.do?f=y&sort=dtstart.utc:asc&fexpr=(categories.href!=%22/public/.bedework/categories/Ongoing%22)%20and%20(entity_type=%22event%22%7Centity_type=%22todo%22)&skinName=list-json&count=10'

f = requests.get(url)


print(f.text)
