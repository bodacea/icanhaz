#!/usr/bin/env python
""" Scrape the ushahidi phabricator lists for dependencies

Phab API is described at: 

Sara-Jayne Terp
2014
"""

from phabricator import Phabricator
import csv

phab = Phabricator()
phab.update_interfaces()
 
print "Fetching tasks from Phab"
projectphid = 'PHID-PROJ-rbdn2wck434bye3sjpxc';
tasks = phab.maniphest.query(projectPHIDs=[projectphid], status="status-open", limit=3000)
 
#Store list of tasks and depends-on as a list of parent-childs
tasklist = [];
depends = {"ROOT":[]};
for key in tasks:
	task = tasks[key];
	taskid = task['objectName'];
	tasklist += [taskid];
	taskdependson = task['dependsOnTaskPHIDs'];
	for dtask in taskdependson:
		if dtask in tasks:
			dependee = tasks[dtask]['objectName'];
		else:
			dependee = "outside";
		depends.setdefault(dependee, []);
		depends[dependee] += [taskid];

#Round up all the orphans
for taskid in tasklist:
	if not taskid in depends:
		depends['ROOT'] += [taskid];

#Output lists to gephi csv input file
fout = open('taskgephi.csv', "wb");
csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC); 
for task in depends:
	csvout.writerow([task] + depends[task])
fout.close()

