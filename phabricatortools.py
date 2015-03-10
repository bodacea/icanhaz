#!/usr/bin/env python
""" Scrape the ushahidi phabricator lists for dependencies

Phabricator API is described at: 

Example use: python phabricatortools.py PHID-PROJ-rbdn2wck434bye3sjpxc

Sara-Jayne Terp
2014
"""

from phabricator import Phabricator
import csv
import sys
import json


""" Get a task list from phabricator

Example use: setup_phab('PHID-PROJ-rbdn2wck434bye3sjpxc')
"""
def setup_phab(projectphid):
	phab = Phabricator()
	phab.update_interfaces()
	print "Fetching tasks from Phab"
	tasks = phab.maniphest.query(projectPHIDs=[projectphid], status="status-open", limit=3000)
 	return(phab, tasks)


""" Create task dependency list from Phab tasklist
"""
def create_dependency_list(tasks):
	#Store list of tasks and depends-on as a list of parent-childs
	tasklist = [];
	depends = {"ORPHANS":[]};
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
	#Round up all the orphans, e.g. tasks with no dependeees or dependents
	for taskid in tasklist:
		if not taskid in depends:
			depends['ORPHANS'] += [taskid];
	return(depends)


""" Remove branch from a dependency tree
"""
def get_tree_branch(tree, child):
	childbranch = None;
	#Get child's branch from tree
	for node in tree:
		print(node)
		if node == child:
			childbranch = tree[node]
			del tree[node]
			return childbranch
		else:
			childbranch = get_tree_branch(tree[node], child)
			if childbranch != None:
				return childbranch
	return childbranch



""" Make dependency tree from a dependency list
"""
def create_dependency_tree(dlist, rootname):
	treenodes = [];
	dtree = {};
	for parent in dlist:
		if parent not in treenodes:
			#If node isn't already in tree, add it at the top level
			treenodes += [parent];
			dtree.setdefault(parent, {});
	 		#Add children to tree
			for child in dlist[parent]:
				if child not in treenodes:
					dtree[parent].setdefault(child, {});
				else:
					childbranch = get_tree_node(dtree, parent, child);
					dtree[parent].setdefault(child, childbranch);
					#FIXIT: setdefault, then add childbranch?
		else:
			#If node is in the tree, find it and add children to it
			add_tree_branch(dtree, parent, dlist[parent])

	dtree.setdefault(rootname, dtree);
	return(dtree)


""" Write dependency list as a Gephi csv file
"""
def write_dependencies_to_gephicsv(depends):
	#Output task dependencies to Gephi csv file
	fout = open('taskgephi.csv', "wb");
	csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC); 
	for task in depends:
		csvout.writerow([task] + depends[task])
	fout.close()
	return()


""" Write dependency list as a json D3 tree 

Should work with all Mike Bostock's D3 tree visualisation code
Example format: https://gist.github.com/mbostock/4063550
"""
def write_dependencies_to_d3tree(dtree):
	#Form dependencies into tree

	#Output to json file
	with open("phabtasks.json", "w") as fout:
		json.dump(phabtree, fout, indent=4)
	fout.close();
	return()


""" Main 
"""
def main(argv):
	if len(argv) > 0:
		phab, tasks = setup_phab(argv[0]);
		depends = create_dependency_list(tasks);
		write_dependencies_to_gephicsv(depends);
	else:
		print("Please input a project PHID")

if __name__ == "__main__":
	main(sys.argv[1:])
