#!/usr/bin/env python
""" Handle lists of country positions, including centre points and bounding boxes

Sara-Jayne Terp
2014
"""

import csv
from urllib2 import urlopen
import requests
import json
from read_write_csv import csv_to_dict


#Constants
countryerrors = {
'DR Congo': 'Congo, the Democratic Republic of the',
'Iran': 'Iran, Islamic Republic of',
'Libya':'Libyan Arab Jamahiriya',
'Moldova':'Moldova, Republic of',
'Russia': 'Russian Federation',
'Syria': 'Syrian Arab Republic',
'Taiwan':'Taiwan, Province of China',
'Venezuela':'Venezuela, Bolivarian Republic of'
}



"""
Use Googlemaps api to find the country that a latlong is in
This gets screwed up by the google api limits- likely to see message 
'You have exceeded your daily request quota for this API.'
FIXIT: use country boundaries and shapely to get past this problem
"""
def get_country_from_latlong(lat, lon, provider='Googlemaps'):
	countryname = "unknown";
	if provider == 'OSM':
		#Using Nomimatim API on OSM data
		nomurl = "http://nominatim.openstreetmap.org/reverse?format=json";
		requrl = nomurl+"&lat="+lat+"&lon="+lon;
		response = requests.get(url=requrl);
		respjson = json.loads(response.text);
	else:
		#Using google maps APi
		gmapsurl = "http://maps.googleapis.com/maps/api/geocode/json?latlng="
		url = gmapsurl+lat+","+lon+"&sensor=false"
		res = urlopen(url).read()
		jres = json.loads(res)
		if jres['results'] != []: #Check that we're in a country, not ocean
			for i in jres['results'][0]['address_components']:
				if "country" in i['types']:
					countryname = i['long_name']
					break
	#Tidy up
	if countryname in countryerrors:
		countryname = countryerrors[countryname];
	return(countryname)


def check_boundingboxes(boundings):
	#Use google maps api to check bounding box file
	for name in boundings:
		midlat = (float(boundings[name][2])+float(boundings[name][4]))/2.0;
		midlon = (float(boundings[name][1])+float(boundings[name][3]))/2.0;
		gname = get_country_from_latlong(str(midlat), str(midlon));
		if gname != name:
			print(name+" in file, "+gname+" in GoogleMaps");
		else:
			print(name+" FOUND")
	return()


def correct_latlon(latlons, boundings):
	#Use bounding box file to correct latlons file
	#namesdiff = list(set(latlons.keys()).difference(set(boundings.keys())));
	for name in latlons:
		if latlons[name][0:2] == ['','']:
			bounds = boundings[name];
			latlons[name] = [(bounds[3]+bounds[5])/2.0, (bounds[2]+bounds[4])/2.0];
	#Output latlons list to new CSV file
	return()


""" Main function
"""
def main(argv):
	latlons = csv_to_dict('countrylatlons.csv');
	boundings = csv_to_dict('country-boundingboxes.csv');


""" Start here, if run from the commandline
"""	
if __name__ == "__main__":
	main(sys.argv[1:])

