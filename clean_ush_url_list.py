
#!/usr/bin/env python
""" Clean Ushahidi list of ushahidi deployments

Sara-Jayne Terp
2014
"""

import read_write_csv #SJF functions for csv handling
import all_the_ush #SJF functions for ushahidi url checking
import sys
import csv
import json

""" Get inlist from file
"""
def get_urllist_from_csv(csvfilename):
	headers, inlist = read_write_csv.csv_to_dict(csvfilename);
	return(inlist)


"""Make live/dead ushahidi list from the cleaned and dead lists
"""
def create_deadalive_list():
	#Get deadlist from file
	fin = open("../../data/ush_deadurls.txt", "r");
	deadurls = json.load(fin);
	#Recreate fulllist from inputs
	urllist = get_urllist_from_csv("../../data/2014-11-18_Ushahidi_Site_Lists.csv");
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


""" Main function
"""
def main():
	directoryurl = "http://tracker.ushahidi.com/"

	urllist = get_urllist_from_csv("../../data/brian_ush_lists.csv");
	print("Original list length is "+str(len(urllist)));
	crowdmaps, standalones = clean_ush_list(urllist);
	print(str(len(crowdmaps))+ " crowdmaps, "+str(len(standalones))+" standalone instances");
	hostcounts, deadlist = all_the_ush.count_hosts(standalones);
	read_write_csv.dict_to_csv("ush_hostcounts.csv", ["Host","Count"], hostcounts);
	json.dump(deadlist, open("ush_deadurls.txt",'w')); #Write deadlist to file


""" Start here, if run from the commandline
"""	
if __name__ == "__main__":
	main()

