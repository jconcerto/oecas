#!/usr/bin/python 
import urllib.request
import os
import xml.etree.ElementTree as ET 
import xmltools
import filecmp
import inspect
from importlib.machinery import SourceFileLoader
from csv import reader

'''
Downloads the raw exoplanet data file and stores it in a temporary folder.
The raw file can be csv or xml format.
'''
def get(url, temp_folder, output_filename):
    identical = False
    print("Retrieving external catalogue data [%s]..." % output_filename)
    xmltools.ensure_dir_exists(temp_folder)
    output_filepath = temp_folder + '/' + output_filename
    dl_file, headers = urllib.request.urlretrieve(url, output_filepath)
    print("Download complete.")
    '''
    # check if file already exists
    if os.path.exists(output_filepath):
        # compare with existing file to see if we need to do parsing
        identical = filecmp.cmp(dl_file, output_filepath)
        print("File is identical to local copy")
        os.remove(dl_file)
    else:
        # parent the downloaded file to the output directory path
        os.rename(dl_file, output_filepath)
    '''
    return identical

'''
Parses the raw exoplanet file and stores it as xml inside LOCAL_REPO
'''
def parse(filename, local_repo, temp_folder, template):

    update_count = 0
    file_count = 0
    print("Parsing...")

    # delete old data
    xmltools.ensure_empty_dir(local_repo)

    # Read the external exoplanet data file
    external_file = open(temp_folder + '/' + filename)
    header = [x.strip() for x in external_file.readline().split(",")]

    # Get template xml file
    template_tree = ET.parse(template)
    template_root = template_tree.getroot()
    missing = missing_column_list(template_root, header)
    if len(missing) > 0:
        print("**WARNING**: Template contains %d columns which could not be found and were skipped: " % len(missing), end="")
        print(missing)

    # Start reading each line of csv file
    for line in reader(external_file):

        # Create dictionary of header keys to corresponding data
        external_entry = dict(zip(header, [x.strip() for x in line]))
        
        # Get template xml file
        template_tree = ET.parse(template)
        template_root = template_tree.getroot()
        
        # Get system root from template tree
        system_root = template_root.find("system")
        system_tree = ET.ElementTree(system_root)
        
        # get exoplanet system name and file path
        system_name = external_entry[system_root[0].text]
        output_filepath = local_repo + "/" + system_name + ".xml"
        
        # Time to create the xml file. But first check if it already exists in
        # local repo so that we do not overwrite.
        if os.path.exists(output_filepath):
            system_tree = ET.parse(output_filepath)
            system_root = system_tree.getroot()
        else:
            format_xml(system_tree, external_entry)
            file_count += 1
        
        # Now to create star and planet xml files
        star_root = template_root.find("star")
        star_tree = ET.ElementTree(star_root)
        star_name = external_entry[star_root[0].text]
        
        if get_tree(system_root, "star", star_name) is None:
            format_xml(star_tree, external_entry)
            system_root.append(star_root)
        else:
            star_root = get_tree(system_root, "star", star_name)
        
        planet_root = template_root.find("planet")
        planet_tree = ET.ElementTree(planet_root)
        format_xml(planet_tree, external_entry)
        star_root.append(planet_root)
        
        # Remove empty tags and nicely indent them
        xmltools.removeemptytags(system_root)
        xmltools.indent(system_root)
        
        # Write to local_repo
        system_tree.write(output_filepath)
        
        update_count += 1
    external_file.close()
    print("Parse complete, %d entries updated with %d new files."
          % (update_count, file_count))

'''
Helper function which formats an xml file from a csv row
'''
def format_xml(template_tree, column_dict):
    
    for child in template_tree.iter():
        local_key = child.tag           # Name of xml tag in template
        local_value = ""                # Text inside column which we need to find
        local_attrib = dict()           # Attribute data of the current tag
        external_key = child.text       # Column in csv file which corresponds to the tag
        
        # Retrieve attribute data from csv file
        for key in child.attrib:
            if child.attrib[key] in column_dict:
                attrib_value = column_dict[child.attrib[key]]
                if attrib_value != "":
                    local_attrib[key] = attrib_value
        child.attrib = local_attrib

        # If no string specified in template, skip searching.
        if (external_key == "" or external_key is None):
            continue

        # Find corresponding entry in csv file
        elif (child.text in column_dict):
            child.text = column_dict[external_key.strip(' \t\n\r')]

'''
Gets the tree element in the given tree which contains a corresponding tag.
Returns null if it cannot be found.
'''
def get_tree(tree, tag, name):
    
    child_list = tree.findall(tag)
    for child in child_list:
        if (child[0].text == name or
            child[0].text.strip(' \t\n\r') == name.strip(' \t\n\r')):
            return child
    return None

'''
Checks each tag in a template and verifies if its corresponding column can
be found in headers. Returns a list of missing headers.
'''
def missing_column_list(template, headers):

    missing_columns = []

    for child in template.iter():
        
        # Check attributes first
        for key in child.keys():
            attrib_column = child.attrib[key]
            if attrib_column is None:
                continue
            attrib_column = attrib_column.strip(' \t\n\r')
            if attrib_column == '' or attrib_column in headers:
                continue
            else:
                missing_columns.append(key + "=" + attrib_column)
        
        # Now check text
        if child.text is None:
            continue
        child_text = child.text.strip(' \t\n\r')
        if child_text == '' or child_text in headers:
            continue
        else:
            missing_columns.append(child.tag + ":" + child_text)
    return missing_columns

'''
Does post processing to xml data fields. Converts numerical values to the right units,
converts dates to the right format, etc.
'''
def process_data(tree):

    for child in tree.iter():

        if child.text is None:
            continue

        child_text = child.text.strip(' \t\n\r')

        if child_text == "":
            continue
        elif child.tag == "declination":
            return True

'''
Does post processing to xml data fields. Calls all methods inside a specified
script name on xml files in a given folder. Ignores "private" python method
names in the format "__methodname__"
REQUIRED: All functions in the post processing script must take an xml tree
element as an input and return an xml tree element as an output.
'''
def post_process(xml_folder, script_name=""):
    
    if script_name == "":
        return

    print("Running post processing scripts...")
    
    # Get python module from script_name and all associated functions
    pp_script = SourceFileLoader("script_module", script_name).load_module()
    pp_funcs = inspect.getmembers(pp_script, inspect.isfunction)
    pp_funcs = [x for x in pp_funcs if inspect.getmodule(x[1]) == pp_script]
    
    # Run functions on each xml file
    for xml_file in os.listdir(xml_folder):
        filepath = xml_folder + "/" + xml_file
        xml_tree = ET.parse(filepath)
        for pp_function in pp_funcs:
            pp_function[1](xml_tree)
        xml_tree.write(filepath)
    print("Post processing done.")
