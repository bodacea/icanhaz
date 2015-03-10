#!/usr/bin/env python
""" Search the Ushahidi list of deployments and add new ones to worldushahidis

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
import csv
import urlparse
from time import gmtime, strftime
from read_write_csv import csv_to_array, array_to_csv, dict_to_csv
import countrylocations
import ushapy


#Constants
countrylatlons = countrylocations.read_countrylatlons();
sizethreshold = 10;
addedsites = {};
mapcategories = {};


""" Get ushahidi username and password from a "secrets" file. 
example use: get_ush_login("../secrets.csv", 'crowdmap')
"""
def get_ush_login(csvfilename, secret):
	headers, secrets = read_write_csv.csv_to_dict(csvfilename, False);
	username = secrets[secret][0];
	password = secrets[secret][1];
	return(username, password)


def get_country_latlon(countryname):
	latlon = [0,0];
	if countryname in countrylatlons:
		latlon = countrylatlons[countryname];
		#print(str(latlon[0])+","+str(latlon[1]))
		if latlon == ['','']: #Correct for data bug in file
			latlon = [0,0];
	return(latlon)


""" Add locations to a CSV list of reports
example: all_the_ush.add_locations_to_ushcsv("datasets/worldushahidis_unknown.csv")
"""
def add_locations_to_ushcsv(filename):
	countrylatlons = countrylocations.read_countrylatlons();
	outrows = []
	headers, inrows = csv_to_array(filename);
	for row in inrows:
		locname = row[4];
		if locname == "unknown":
			siteurl = row[2];
			try:
				row[10] = siteurl;
				countryname, countrylat, countrylon = get_latlon_country(siteurl);
				print(countryname+": "+str(countrylat)+","+str(countrylon))
				row[4] = countryname;
				row[14] = countryname;
				row[7] = countrylat;
				row[8] = countrylon;
				if countryname != "unknown":
					outrows += [row];
			except:
				print("failed for "+siteurl)
	array_to_csv("worldushahidislocated.csv", outrows, headers);
	return()


""" Get name and location of country containing a lat/long point
"""
def get_latlon_country(siteurl):
	countryname = "unknown";
	countrylat = 0;
	countrylon = 0;
	response = requests.get(url=siteurl+"/api?task=geographicmidpoint");
	respjson = json.loads(response.text);
	lat = respjson['payload']['geographic_midpoint'][0]['latitude'];
	lon = respjson['payload']['geographic_midpoint'][0]['longitude'];
	#print(str(lat)+','+str(lon));
	if lat != None and lon != None:
		#Use country list to allocate country to map
		countryname = countrylocations.get_country_from_latlong(str(lat), str(lon));
		countrypos = get_country_latlon(countryname);
		countrylat = countrypos[0];
		countrylon = countrypos[1];

	return(countryname, countrylat, countrylon)


""" Get map details using its API and some scraping

Some jiggling with lat/longs: want to locate maps to *country* level, so convert original latlong into 
centre position of containing country.
"""
def get_site_details(siteurl):

	sitesizes = [0,10,100,1000,10000,10000000];
	sizenames = {0:'unknown',10:'tiny', 100:'small', 1000:'medium', 10000:'large', 10000000:'very large'};
	sitedesc = {'api':'unknown', 'numreports':-1, 'country':'unknown', \
				'countrylat':0,'countrylon':0,'title':'','description':'', \
				'category':'uncategorised', 'technology':'unknown'};
	#Can get geographic midpoint using api?task=geographicmidpoint
	try:
		fullsiteurl = siteurl+'/';
		sitedesc['numreports'] = ushapy.get_number_of_ush_reports(fullsiteurl);
		sitedesc['api'] = 'yes';
		if sitedesc['numreports'] >= sizethreshold:
			#Give map a size name
			for s in sitesizes:
				if sitedesc['numreports'] < s:
					sitedesc['category'] += "," + sizenames[s];
					break;
			#Scrape description and title from site
			#FIXIT: cheat for now
			sitedesc['title'] = siteurl;
			sitedesc['description'] = siteurl;
			if 'crowdmap' in siteurl:
				sitedesc['technology'] = 'Crowdmap'
			else:
				sitedesc['technology'] = 'Ushahidi'
			#Get lat/lon position of site
			sitedesc['country'], sitedesc['countrylat'], sitedesc['countrylon'] = \
				get_latlon_country(siteurl);
	except:
		sitedesc['api'] = 'no';
	#Clean up a bit
	sitedesc['category'] += ","+sitedesc['technology'];
	return(sitedesc)



""" Hack: add directory entries to the map website based on a file containing:
url, number of reports, country

Example use: all_the_ush.add_file_to_map("add_to_wwtoday.txt");
"""
def add_file_to_map(filename):
	countrylatlons = countrylocations.read_countrylatlons();
	sitesizes = [0,10,100,1000,10000,10000000];
	sizenames = {0:'unknown',10:'tiny', 100:'small', 1000:'medium', 10000:'large', 10000000:'very large'};
	mapurl = "https://worldushahidis.crowdmap.com/";
	f = open(filename, "r");
	flop=0;
	for line in f:
		#Read in 2 lines, turn them into [url,numreports,country]
		flop = 1-flop;
		if flop > 0:
			row = line.strip().split(",");
		else:
			row += [line.strip()];
			#Create sitedesc
			siteurl = row[0];
			numreports = int(row[1]);
			countryname = row[2];
			latlon = get_country_latlon(countryname, countrylatlons);
			if 'crowdmap' in siteurl:
				tech = 'Crowdmap'
			else:
				tech = 'Ushahidi'
			category = 'uncategorised' + "," + tech;
			for s in sitesizes:
				if numreports < s:
					category += "," + sizenames[s];
					break;
			sitedesc = {'api':'yes', 'numreports':numreports, 'country':countryname, \
					'countrylat':latlon[0],'countrylon':latlon[1], \
					'title':siteurl,'description':siteurl, \
					'category':category, 'technology':tech};
			#Add to map
			#print(sitedesc);
			add_site_to_map(siteurl, mapurl, sitedesc);
	return()


""" Add a new directory entry to the map website
  #Check that site is active (e.g. has more than 100 reports)
  #if not active, then add to smallushahidis list
  #Convert line's lat/long into country (and country coordinate)

  #Translate line's heading and description into English
  #Add category based on previous hand-categorisations
"""
def add_site_to_map(siteurl, mapurl, sitedesc={}):
	#Create a site description if we don't have one already
	if sitedesc == {}:
		sitedesc = get_site_details(siteurl);
	#Use map API to add report to worldushahidis.com
	if sitedesc['numreports'] >= sizethreshold:
		print("Adding "+siteurl+" to map "+str(sitedesc['numreports'])+" reports");
		print("country: "+sitedesc['country']+" pos:"+str(sitedesc['countrylat'])+","+str(sitedesc['countrylon']));
		addedsites.setdefault(siteurl, sitedesc);
		now = gmtime();
		payload = { \
		'task': 'report', \
		'incident_title': sitedesc['title'], \
		'incident_description': sitedesc['description'], \
		'incident_category': ushapy.cats_to_catids(sitedesc['category'], mapurl), \
		'latitude': sitedesc['countrylat'], \
		'longitude': sitedesc['countrylon'], \
		'Url': siteurl, \
		'Technology': sitedesc['technology'], \
		'Country': sitedesc['country'], \
		'incident_date': strftime('%m/%d/%Y', now), \
		'incident_hour': strftime('%I', now), \
		'incident_minute': strftime('%M', now), \
		'incident_ampm': strftime('%p', now).lower(), \
		'location_name': sitedesc['country'], \
		};
		r = requests.post(mapurl+"/api", data=payload);
	#else:
	#	print("Rejected "+siteurl+" "+str(sitedesc['numreports'])+" reports");
 	return(sitedesc)


""" Count the number of hosting sites in a set of ushahidi deployments
"""
def count_hosts(urllist):
	hostcounts = {}
	deadlist = []
	count = 0;
	for url in urllist:
		count += 1;
		try:
			print(str(count)+" checking "+ url);
			owner = check_site_hosting(url)
		except:
			owner = "dead";
			deadlist += [url]
		hostcounts.setdefault(owner, 0);
		hostcounts[owner] += 1;
	return(hostcounts, deadlist)


"""
"""
def check_site_hosting(url):
	urlbreakdown = urlparse.urlparse(url);
	netlocation = urlbreakdown.netloc;
	#urlcentre = url.split("://")[1].strip("/");
	if netlocation[-12:] == "crowdmap.com":
		owner = "crowdmap"
	else:
		ipaddress = socket.gethostbyname(netlocation);
		#response = os.system("ping -c 1 " + ipaddress); #0 = site's up and okay
		obj = IPWhois(ipaddress);
		res=obj.lookup();
		owner = res['nets'][0]['description'];
	return(owner)


""" Find and check all sites listed in the directory against the list of map websites

Notes about tracker are in https://wiki.ushahidi.com/display/WIKI/Deployment+Search
"""
def check_tracker_entries(mapentries, mapurl, directoryurl):
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


""" Get list of live urls

Assumes that status file is a CSV with columns Site URL and status
where status is one of live, crowdmap or dead
"""
def get_urls_from_status_file(csvfilename):
	urls = []
	headers, allurls = csv_to_array(csvfilename);
	for url in allurls:
		if url[1] != "dead":
			urls += [url[0]];
	return urls


""" Get list of all the sites currently listed on map website
"""
def get_urls_from_map(mapurl):
	#Put list of sites into a dictionary
	mapentries = {}
	numsites = ushapy.get_number_of_ush_reports(mapurl)
	numcalls = numsites/100
	if numcalls < 100 or numcalls%100 != 0:
		numcalls += 1
	for call in range(0, numcalls):
		startid = str(call*100)
		if call == 0:
			response = requests.get(url=mapurl+"api?task=incidents&limit=100")  #Ush api crashes if sinceid=0
		else:
			response = requests.get(url=mapurl+"api?task=incidents&by=sinceid&id="+startid+"&limit=100")
		reportsjson = json.loads(response.text)
		for sitedetails in reportsjson['payload']['incidents']:
			siteurl = sitedetails['customfields']['2']['field_response'].strip("/");
			mapentries.setdefault(siteurl, 0);
			mapentries[siteurl] += 1; #build in check for duplicates
	return mapentries



""" Create a csv file containing all the larger ushahidis worldwide (or attempting to do this)
"""
def get_all_the_ush(argv):
	trackerurl = "http://tracker.ushahidi.com/";
	mapurl = "https://worldushahidis.crowdmap.com/";
	# Get list of live urls on tracker list but not on map list
	mapentries = get_urls_from_map(mapurl);
	trackerentries = get_urls_from_status_file('../../data/2014-11-18_all_ush_status.csv');
	#trackerurls = check_tracker_entries(mapentries, mapurl, trackerurl)
	# diff the mapentries and all_ush sets to give in all_ush, not-in mapentries
	newurls = list(set(trackerentries).difference(set(mapentries.keys())));
	# add all new urls to map
	for siteurl in newurls:
		sitedesc = add_site_to_map(siteurl, mapurl);
	#Put all new urls into csv file for now
	fout = open("addedsites.csv", "wb")
	csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)  
	for url in addedsites:
		csvout.writerow([url]);
	fout.close()
	return()

"""Make live/dead ushahidi list from the cleaned and dead lists
"""
def create_deadalive_list():
	#Get deadlist from file
	fin = open("../../data/ush_deadurls.txt", "r");
	deadurls = json.load(fin);
	#Recreate fulllist from inputs
	headers, urllist = csv_to_array("../../data/2014-11-18_Ushahidi_Site_Lists.csv");
	crowdmaps, standalones = clean_ush_list(urllist);
	#create array of dead, live, crowdmap from lists
	liveurls = list(set(standalones).difference(set(deadurls)));
	#Output results to csv file
	fout = open("../../data/all_ush_status.csv", "wb");
	csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC);
	csvout.writerow(["Site URL", "Status"]);
	for entry in liveurls:
		csvout.writerow([entry, "live"])
	for entry in crowdmaps:
		csvout.writerow([entry, "crowdmap"])
	for entry in deadurls:
		csvout.writerow([entry, "dead"])
	fout.close();
	#Ideas for more: add country, #reports, lastreportyear, category, tech, 
	#livedead and scrape the description from the site. Add language? Add 
	#original description text (but translate main one into English?).
	return()


""" Clean the ushahidi list
"""
def clean_ush_list(inlist):
	badstarts = [".urlencode", "http://127.0.0.1", "http://localhost", "http://10.", "http://192.", "http://172."];
	#Create list from input rows
	allurls = []
	for inrow in inlist:
		if len(inrow) > 0:
			entry = inrow[0].lower().strip("'").strip("/")
			if "://" not in entry:
				entry = "http://" + entry
			allurls += [entry]
	#Do first cleaning = remove duplicates before more processing
	allurls = list(set(allurls))
	#More cleaning - remove all the bad starts and split deployment lists
	standalones = []
	crowdmaps = []
	for url in allurls:
		reject = False
		for bad in badstarts:
			if url.startswith(bad):
				reject = True
		if not reject:
			if "crowdmap.com" not in url:
				standalones += [url]
			else:
				crowdmaps += [url]
	return(crowdmaps, standalones)



""" Clean Ushahidi list of ushahidi deployments
"""
def clean_ush_url_list():
	directoryurl = "http://tracker.ushahidi.com/"

	headers, urllist = csv_to_array("../../data/brian_ush_lists.csv");
	print("Original list length is "+str(len(urllist)));
	crowdmaps, standalones = clean_ush_list(urllist);
	print(str(len(crowdmaps))+ " crowdmaps, "+str(len(standalones))+" standalone instances");
	hostcounts, deadlist = all_the_ush.count_hosts(standalones);
	dict_to_csv("ush_hostcounts.csv", ["Host","Count"], hostcounts);
	json.dump(deadlist, open("ush_deadurls.txt",'w')); #Write deadlist to file


""" Correct report locations in an ushahidi instance, reading a csv list for the correct
location name, lat and long
"""
def correct_locations():
	mapurl = "https://worldushahidis.crowdmap.com/";
	[username, password] = get_ush_login("../secrets.csv", 'crowdmap')
	headers, csvdata = csv_to_array('worldushahidislocated.csv')
	for item in csvdata:
		reportid = item[0]
		print(reportid)
		viewpayload = ushapy.get_ush_report(mapurl, reportid)
		editpayload = ushapy.reformat_ush_api_report_view_to_edit(viewpayload)
		editpayload['location_name'] = item[4]
		editpayload['latitude'] = item[7]
		editpayload['longitude'] = item[8]
		#FIXIT: Also need to add 'incident_category' to the payload
		resp = ushapy.edit_ush_report(mapurl, editpayload, username, password)
		print(resp.text)
	return()


""" Main function
"""
def main(argv):
	correct_locations()

""" Start here, if run from the commandline
"""	
if __name__ == "__main__":
	main(sys.argv[1:])
