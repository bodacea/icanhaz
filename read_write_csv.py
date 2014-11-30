#!/usr/bin/env python
""" Simple CSV read/write tools

Sara-Jayne Terp
2014
"""
import csv

"""Read csv file into an array

"""
def csv_to_array(csvfilename, hasheaders=True, printout=False):
	fin = open(csvfilename, "rb");
	csvin = csv.reader(fin);
	#Read in header row
	headers = [];
	if hasheaders:
		headers = csvin.next(); 
		if printout:
			for header in headers:
				print(header)
	#Read in non-header rows
	datadict = [];
	for row in csvin: 
		datadict += [row];
		if printout:
 			for col in range(0,len(row)):
				print(row[col]);
	#tidy up
	fin.close()
	return(headers, datadict)


""" Read csv file into a data dictionary

This can also be done with csv.DictReader()
"""
def csv_to_dict(csvfilename, hasheaders=True):
	headers = []
	outdict = {}
	fin = open(csvfilename, "rb");
	csvin = csv.reader(fin);
	#Read in header row
	if hasheaders:
		headers = csvin.next();
	for row in csvin:
		outdict.setdefault(row[0], row[1:]); #NB if 1: is null, sets value to null
	fin.close();
	return(headers, outdict)


""" Write data dictionary to csv file

This can also be done with csv.DictWriter()
"""
def dict_to_csv(csvfilename, headers, datadict, hasheaders=True):
	fout = open(csvfilename, "wb")
	csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)  
	#Write headers to csv file
	if hasheaders == True:
		csvout.writerow(headers)
	#Write data to csv file
	for entry in datadict:
		csvout.writerow([entry, datadict[entry]])
	#tidy up
	fout.close()
	return()

