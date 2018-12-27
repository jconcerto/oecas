#!/bin/python
import urllib
import os
import xml.etree.ElementTree as ET 

#####################
# Helper functions
#####################

# Check for directory
def ensure_empty_dir(tdir):
	if os.path.exists(tdir):
		for fileName in os.listdir(tdir):
			os.remove(tdir+"/"+fileName)
	else:
		os.makedirs(tdir)

# check if directory exits, if not, create it
def ensure_dir_exists(tdir):
    if not os.path.exists(tdir):
        os.makedirs(tdir)

# Nicely indents the XML output 
def indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Removes empty nodes from the tree
def removeemptytags(elem):

    toberemoved = []    
    for child in elem:
        if child is None:
            toberemoved.append(child)
        elif len(child) == 0:
            if not child.text:
                toberemoved.append(child)
            elif len(child.text) == 0 and len(child.attrib) == 0:
                toberemoved.append(child)
    for child in toberemoved:
        elem.remove(child)
    for child in elem:
        removeemptytags(child)
