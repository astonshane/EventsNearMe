from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3

searchDict = {"postal_code":"12180"}


address = "1999 Burdett Ave, Troy, NY 12180"
print "lat", GoogleV3().geocode(address, components=searchDict).latitude
print "lon", GoogleV3().geocode(address, components=searchDict).longitude
