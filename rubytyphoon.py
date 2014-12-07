#!/usr/bin/env python
""" Pull location information out of a list of Ushahidi V2 instances

Sara-Jayne Terp
2014
"""

import ushahiditools
import read_write_csv

sources = ['https://supertyphoonpablo.crowdmap.com/', \
'https://pablo.crowdmap.com/', \
'http://bopharesponse.crowdmap.com/', \
'https://phtyphoonactionableintel.crowdmap.com/', \
'https://sbtftyphoonbopha.crowdmap.com/', \
'https://philippinedisasterwatch.crowdmap.com/', \
'https://yolandaph.crowdmap.com/', \
'https://haiyan.crowdmap.com/', \
'https://phdisaster.crowdmap.com/', \
'https://floodtracker.crowdmap.com/', \
'https://manilafloods.crowdmap.com/', \
'https://saantatakbo.crowdmap.com/', \
'https://idpmindanao.crowdmap.com/'];

locs = [];
for mapurl in sources:
	reports = ushahiditools.get_ush_reports(mapurl);
	for r in reports:
		lat = r['incident']['locationlatitude'];
		lat = "" if lat==None else lat.encode('utf-8');
		lon = r['incident']['locationlongitude'];
		lon = "" if lon==None else lon.encode('utf-8');
		name = r['incident']['locationname'];
		name = "" if name==None else name.encode('utf-8');
		locs += [[lat, lon, name]];

#Send to CSV file
read_write_csv.array_to_csv("YolandaGeolocs.csv", locs, \
	['latitude','longitude','name']);

