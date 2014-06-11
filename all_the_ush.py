import sys
from urllib2 import urlopen
import json

#global variables
trackerurl = 'http://tracker.ushahidi.com/list'
ushahidiurl = "https://worldushahidis.crowdmap.com/api?task=incidents"

def get_country(lat, lon):
	url = "http://maps.googleapis.com/maps/api/geocode/json?latlng="+lat+","+lng+"&sensor=false"
	res = urlopen(url).read()
	jres = json.loads(res)
	for i in jres['results'][0]['address_components']:
		if "country" in i['types']:
			countryname = i['long_name']
			break
	return(countyname)

#convert tracker.ushahidi.com line into ushahidi report
def add_line_to_site():
  #Check that line isn't already in worldwideushahidis - use the site URL
  #Check that site is active (e.g. has more than 100 reports)
    #if not active, then add to deadushahidis csv
  #Convert line's lat/long into country (and country coordinate)


  #Translate line's heading and description into English
  #Add category based on previous hand-categorisations


#Read lines from tracker.ushahidi.com


def main(argv):
	print("main")

if __name__ == "__main__":
	main(sys.argv[1:])
