#!/usr/bin/env python
""" Create a list of all the files in a given directory. 

Example use: python all_files_in_a_directory.py testdata csv

Sara-Jayne Terp
2014
"""
import glob
import os
import sys

def getfiles(datadir, filetype):
	allfiles = glob.glob(os.path.join(datadir, filetype))
	return(allfiles)

def main(argv):
	if len(argv) > 1:
		datadir = argv[0]
		filetype = '*.'+argv[1]
		print("looking for %s in directory %s" % (filetype, datadir))
	else:
		datadir = '.'
		filetype = '*'
	allfiles = getfiles(datadir, filetype)
	for infile_fullname in allfiles:
	    filename = infile_fullname[len(datadir)+1:]
	    print(filename)

if __name__ == "__main__":
	main(sys.argv[1:])