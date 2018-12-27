import xml.etree.ElementTree as ET 
import re

def process_xml(xml_tree):
    
    for child in xml_tree.iter():
        if child.tag == "declination":
            tempdec = ""
            dec = float(child.text)
            tempdec += "%+.2i" %(dec) 
            minutes = dec % 1 * 60
            tempdec += " %.2i" % (minutes)
            seconds = round(minutes % 1 * 60)
            tempdec+= " %.2i" % (seconds)
            child.text = tempdec
        elif child.tag == "rightascension":
            tempra = ""
            ra = float(child.text)
            hours = ra / 360 * 24
            tempra += "%.2i" % (hours)
            minutes = hours % 1 * 60
            tempra += " %.2i" % (minutes)
            seconds = minutes % 1 * 60
            tempra += " %.2i" % (round(seconds))
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
            if child.tag == "altnames":
                names_list = [x.strip(' ') for x in child.text.split(',')]
                name_index = list(star).index(child)
                
                # Commented out because insert() is godawfully slow
                '''
                for altname in names_list:
                    name_element = ET.Element("name")
                    name_element.text = altname
                    star.insert(name_index, name_element)
                '''

def process_planets(xml_tree):
    
    planet_list = [x for x in xml_tree.iter() if x.tag == "planet"]
    for planet in planet_list:
        for child in planet:
            if child.tag == "discoverymethod":
                if child.text.lower() == "radial":
                    child.text = "RV"
                elif child.text.lower() == "imaging":
                    child.text = "imaging"
                elif child.text.lower() == "transit":
                    child.text = "transit"
            if child.tag == "lastupdate":
                child.text = child.text.replace("-","/")[2:]
    