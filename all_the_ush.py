#!/usr/bin/env python
""" Search the Ushahidi list of deployments and add noew ones to worldushahidis

Sara-Jayne Terp
2014
"""

import sys
import os
from urllib2 import urlopen
import requests
import json
import socket
from ipwhois import IPWhois


""" Get the country location of a lat/long from the Googlemaps gazetteer
"""
def get_country_from_latlong(lat, lon):

	gmapsurl = "http://maps.googleapis.com/maps/api/geocode/json?latlng="
	url = gmapsurl+lat+","+lng+"&sensor=false"
	res = urlopen(url).read()
	jres = json.loads(res)
	for i in jres['results'][0]['address_components']:
		if "country" in i['types']:
			countryname = i['long_name']
			break
	return(countyname)


""" Add a new directory entry to the map website
  #Check that site is active (e.g. has more than 100 reports)
  #if not active, then add to smallushahidis list
  #Convert line's lat/long into country (and country coordinate)

  #Translate line's heading and description into English
  #Add category based on previous hand-categorisations
"""
def add_site_to_map(siteurl, mapurl):
	smallushahidis = []
 	return smallushahidis

"""
"""
def count_hosts(urllist):
	hostcounts = {}
	for url in urllist:
		try:
			owner = check_site_hosting(url)
		except:
			owner = "dead"
		hostcounts.setdefault(owner, 0);
		hostcounts[owner] += 1;
	return(hostcounts)

"""
"""
def check_site_hosting(url):
	urlcentre = url.split("://")[1].strip("/");
	ipaddress = socket.gethostbyname(urlcentre);
	#response = os.system("ping -c 1 " + ipaddress); #0 = site's up and okay
	obj = IPWhois(ipaddress);
	res=obj.lookup();
	owner = res['nets'][0]['description'];
	return(owner)


""" Find and check all sites listed in the directory against the list of map websites

Notes about tracker are in https://wiki.ushahidi.com/display/WIKI/Deployment+Search
"""
def check_directory_entries(mapentries, mapurl, directoryurl):
	newurls = []
	response = requests.get(url=directoryurl+"list?limit=0,500000&json=true")
	directorydata = json.loads(response.text)
	for site in directorydata:
		siteurl = directorydata[site]['url']
		if siteurl not in mapentries.keys():
			print ("New url: "+siteurl);
			add_site_to_map(siteurl, mapurl);
			newurls += [siteurl];
	return newurls


""" Get number of reports on an ushahidi site
"""
def get_number_of_ush_reports(siteurl):
	response = requests.get(url=siteurl+"api?task=incidentcount")
	numjson = json.loads(response.text)
	numreports = numjson['payload']['count'][0]['count']	
	return numreports


""" Get list of all the sites currently listed on map website
"""
def get_urls_from_map(mapurl):
	#Put list of sites into a dictionary
	mapentries = {}
	numsites = get_number_of_ush_reports(mapurl)
	numcalls = int(numsites)/100
	if numcalls%100 != 0:
		numcalls += 1
	for call in range(0, numcalls):
		startid = str(call*100)
		if call == 0:
			response = requests.get(url=mapurl+"api?task=incidents&limit=100")  #Ush api crashes if sinceid=0
		else:
			response = requests.get(url=mapurl+"api?task=incidents&by=sinceid&id="+startid+"&limit=100")
		reportsjson = json.loads(response.text)
		for sitedetails in reportsjson['payload']['incidents']:
			siteurl = sitedetails['customfields']['2']['field_response']
			mapentries[siteurl] = {}
	return mapentries


""" Main function
"""
def main(argv):
	directoryurl = "http://tracker.ushahidi.com/"
	mapurl = "https://worldushahidis.crowdmap.com/"

	mapentries = get_urls_from_map(mapurl)
	newurls = check_directory_entries(mapentries, mapurl, directoryurl)


""" Start here, if run from the commandline
"""	
if __name__ == "__main__":
	main(sys.argv[1:])
