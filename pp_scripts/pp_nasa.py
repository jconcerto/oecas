import xml.etree.ElementTree as ET 
import re

def process_xml(xml_tree):
    
    for child in xml_tree.iter():
        if child.tag == "declination":
            tempdec = ""
            tempdec += child.text.split("d")[0] # hours
            tempdec += " " + child.text.split("d")[1].split("m")[0] # minutes
            tempdec += " %.2i" % (round(float(child.text.split("d")[1].split("m")[1].split("s")[0])))
            child.text = tempdec
        elif child.tag == "rightascension":
            tempra = ""
            tempra += child.text.split("h")[0] # hours
            tempra += " " + child.text.split("h")[1].split("m")[0] # minutes
            tempra += " %.2i" % (round(float(child.text.split("h")[1].split("m")[1].split("s")[0]))) # seconds
            child.text = tempra
        elif not child.text is None or not re.match("^\d+?\.\d+?$", child.text) is None:
            temp = child.text
            if "." in temp:
                temp = temp.rstrip("0")
            temp = temp.rstrip(".")
            child.text = temp
        
        # Remove trailing zeroes and signs from error values
        for key in child.attrib:
            if key == "errorminus":
                temp = child.attrib[key].replace("-", "")
                if "." in temp:
                    temp = temp.rstrip("0")
                temp = temp.rstrip(".")
                child.attrib[key] = temp
            elif key == "errorplus":
                temp = child.attrib[key].replace("+", "")
                if "." in temp:
                    temp = temp.rstrip("0")
                temp = temp.rstrip(".")
                child.attrib[key] = temp
                

def process_stars(xml_tree):
    
    star_list = [x for x in xml_tree.iter() if x.tag == "star"]
    for star in star_list:
        for child in star:
            if child.tag == "mass" or child.tag == "radius":
                temp = child.text
                if "." in temp:
                    temp = temp.rstrip("0")
                temp = temp.rstrip(".")
                child.text = temp

def process_planets(xml_tree):
    return