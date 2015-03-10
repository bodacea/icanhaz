#!/usr/bin/env python
""" Handle json files

Sara-Jayne Terp
2014
"""

import requests #you may have to install this library
import json
import csv

""" Get openweathermap.org data for a given bounding box. Dump results to csv file

Example use:
tzabounds = '29.256,-12.039,40.561523,-0.922812' //Tanzania bounding box
openweather_to_csv(tzabounds);
"""
def openweather_to_csv(boundingbox):

	url = 'http://api.openweathermap.org/data/2.1/find/station?bbox='+boundingbox+',10&cluster=no'

	response = requests.get(url=url)
	data = json.loads(response.text)

	fout = open('TZAweather.csv', 'wb+')
	outcsv = csv.writer(fout)
	outcsv.writerow(['name','latitude','longitude'])

	for station in data['list']:
		print(station['name']+' latlong: '+
			str(station['coord']['lat'])+","+
			str(station['coord']['lon']))

		outcsv.writerow([station['name'], station['coord']['lat'], station['coord']['lon']])

	fout.close()
	return()
