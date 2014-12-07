
#!/usr/bin/env python
""" Read/write to Ushahidi v2.7 instances

Sara-Jayne Terp
2014
"""

import requests
from time import gmtime, strftime
import json

mapcategories = {}


""" Get reports from ushahidi website
"""
def get_ush_reports(mapurl):
	#Put list of sites into a dictionary
	reports = []
	numreports = get_number_of_ush_reports(mapurl)
	numcalls = numreports/100
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
			reports += [sitedetails];
	return reports



""" Get number of reports on an ushahidi site
"""
def get_number_of_ush_reports(siteurl):
	response = requests.get(url=siteurl+"api?task=incidentcount")
	numjson = json.loads(response.text)
	numreports = int(numjson['payload']['count'][0]['count'])	
	return numreports


""" Use ushahidi site's categories list to convert text categories list into ids
"""
def cats_to_catids(catslist, mapurl):
	catids = [];
	if mapcategories == {}:
		response = requests.get(url=mapurl+"api?task=categories");
		catsjson = json.loads(response.text);
		for cat in catsjson['payload']['categories']:
			mapcategories.setdefault(cat['category']['title'], cat['category']['id']);
	catnames = catslist.split(",");
	for catname in catnames:
		if catname in mapcategories:
			catids += [mapcategories[catname]];
	catidslist = ",".join(catids);
	return(catidslist)


""" Push entry with photo attached to an Ushahidi V2.7 repo 
#date, hour, minute, ampm are all mandatory fields 
#Url, Technology, Country are all custom formfields in my site; use similar
"""
def push_photo_to_ush(mapurl, title, description, lat, lon, location, categories, photopath, photoname):
#format if you have custom formfields yourself
	now = gmtime();
	payload = { \
	'task': 'report', \
	'incident_title': title, \
	'incident_description': description, \
	'incident_category': cats_to_catids(categories, mapurl), \
	'latitude': lat, \
	'longitude': lon, \
	#'Url': siteurl, \
	#'Technology': sitedesc['technology'], \
	#'Country': sitedesc['country'], \
	'incident_date': strftime('%m/%d/%Y', now), \
	'incident_hour': strftime('%I', now), \
	'incident_minute': strftime('%M', now), \
	'incident_ampm': strftime('%p', now).lower(), \
	'location_name': location, \
	'incident_photo[]': "@"+photoname+";filename="+photoname+";type=image/jpeg" \
	};
	imagefiles = {photoname: open(photoname, 'rb')};
	r = requests.post(mapurl+"api", data=payload, files=imagefiles);
	return(r)


def try_photo():
	#fake up some data
	mapurl = "https://worldushahidis.crowdmap.com/";
	title = "this is my title";
	description = "this is my description";
	lat = 0;
	lon = 0;
	location = "Nairobi";
	categories = "unknown,tiny";
	photopath = "/";
	photoname = "test.jpg"; #NB jpgs only at mo - will need other type above (e.g. image/otherformat) if not
	r = push_photo_to_ush(mapurl, title, description, lat, lon, location, categories, photopath, photoname);
	print(r.text);


