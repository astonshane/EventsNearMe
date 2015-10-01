class Event:
	def __init__(self, name, lat, lon):
		self.name = name
		self.lat = lat
		self.lon = lon

	def __str__(self):
		return "{%s (%f, %f)}" % (self.name, self.lat, self.lon)

	def __repr__(self):
		return self.__str__()

def constructTestEvents():
	return [Event("CII", "42.728834", "-73.6792977"), Event("Pizza Bella", "42.7267581", "-73.6794012")]
