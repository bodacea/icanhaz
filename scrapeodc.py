#!/usr/bin/env python
""" Scrape dataset from Cambodia development website
http://cdc.khmer.biz/Reports/ lists all .asp files available for this

Mechanize settings are from http://stockrt.github.io/p/emulating-a-browser-in-python-with-mechanize/
Requests kept getting a timeout message from the CDC site

Sara-Jayne Terp
2015
"""

import mechanize
import cookielib
from bs4 import BeautifulSoup
import csv
import lxml.html
import cssselect

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

#Go grab some data
baseurl = "http://cdc.khmer.biz/";
url0 = baseurl + "index.asp?submit=Guest";
url1 = baseurl + "Reports/reports_by_sector_list.asp?OtherSubSector=101&status=0";
#br.add_password(url0, 'username', 'password') #<- only needed if site is password-protected
r = br.open(url0); #have to do this, or get timeout message
r = br.open(url1);
htmlstring = r.read();

# f = open('cdc_workfile', 'w')
# f.write(htmlstring)
# f.close()

#SOUP version
#htmltree = html.fromstring(htmlstring);
# soup = BeautifulSoup(htmlstring, 'html.parser');
# #print(soup.prettify())
# bysector=soup.find_all(id="report_listing_by_sector"); #probably only works for url1
# ts = bysector[0].find_all("table");

#LXML version: find the list of pages and the data table
root = lxml.html.fromstring(htmlstring)
lbs = root.cssselect("td#report_listing_by_sector table");

#List of pages
print("PAGES: ")
for index,element in enumerate(lbs[0].cssselect("a")):
	print(element.text)

numpages = index+2; #first page doesn't have link, and index started at 0

#Data table
#Data table structure is: header row, with subject row (text in td) then 
#subsubject row (text in th), then data rows.
datarows = lbs[1].cssselect("tr")

dataheaders = []
datarow = datarows[0];
ths = datarow.cssselect("th"); 
for t in range(0,len(ths)):
	dataheaders += [ths[t].text]; #FIXIT: strip string

dataset = [];
headers = ['id', 'country', 'title', 'url', 'number', 'start date', 'end date', 'budget', 'status'];
for r in range(1,len(datarows)):
	datarow = datarows[r];
	print("Row {}".format(r));
	tds = datarow.cssselect("td");

	#Null or subsubject row
	if len(tds) < 1:
		ths = datarow.cssselect("th");
		if len(ths) > 0:
			rowtext = ths[0].cssselect("font")[0].text;
		continue;

	#Subject row - save value, continue
	if len(tds) == 1:
		rowtext = tds[0].cssselect("img")[0].tail; #FIXIT: string \r\n\t from here
		print(rowtext);
		continue;

	#Data row
	if len(tds) >= 8:
		pid = tds[0].text;
		pcountry = tds[1].text;
		ptitle = tds[2].cssselect("a")[0].text;
		purl = tds[2].cssselect("a")[0].attrib['href'];
		pnumber = tds[3].text;
		pstartdate = tds[4].text;
		penddate = tds[5].text;
		pbudget = tds[6].text; #FIXIT: strip string
		pstatus = tds[7].text;
		dataset += [[pid, pcountry, ptitle, purl, pnumber, pstartdate, penddate, pbudget, pstatus]];


#Output dataset to CSV file
fout = open("cdc_data.csv", "wb");
csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)  
csvout.writerow(headers)
for entry in dataset:
	csvout.writerow(entry)

fout.close()



