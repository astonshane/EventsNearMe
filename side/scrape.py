import requests
import json

url = 'http://events.rpi.edu:7070/feeder/main/eventsFeed.do?f=y&sort=dtstart.utc:asc&fexpr=(categories.href!=%22/public/.bedework/categories/Ongoing%22)%20and%20(entity_type=%22event%22%7Centity_type=%22todo%22)&skinName=list-json&count=10'

#url2 = 'http://localhost:5000'
f = requests.get(url)


print(f.text);
#out = open('event.json','w');

#file = open('data.json', 'r')

#parsed_json = json.loads(f.text)
#for x in range(0, 10):
# print(parsed_json['bwEventList']['events'][x]['summary'])
# print(parsed_json['bwEventList']['events'][x]['location']['address'])
# print(parsed_json['bwEventList']['events'][x]['description'])
# print
# print
