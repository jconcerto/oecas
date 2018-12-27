import configparser


config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()

def del_catalogue():   
    config.read("config.ini")    
    print("----- DELETING CATALOGUE DATA -----")
    cat_list = [x for x in config.sections() if 'CATALOGUE' in x]
    while True:
        count = 1
        print("You may enter 'cancel' at any time to exit.")
        for cat in cat_list:
            print(str(count) + ". " + config.get(cat, "name"))
            count += 1
        print("Enter number of the catalogue to delete: ", end="")

        num_input = input()
        if num_input == "cancel":
            break
        elif int(num_input) <= len(cat_list):
            cat_to_delete = cat_list[int(num_input) - 1]
            cat_name = config.get(cat, "name")
            yesno = ""
            while True:
                print("\nDelete " + cat_name + "? (y/n): ", end="")
                yesno = input().lower()
                if yesno == "yes" or yesno == "y" or yesno == "no" or yesno == "n" or yesno == "cancel":
                    break
            if yesno == "cancel":
                break
            elif yesno == "yes" or yesno == "y":
                
                remove_conf(cat_to_delete)
                
                print(cat_name + " deleted.")
                break
        else:
            print("Invalid input\n")        

    print("-----------------------------------")
    return

def info_catalogues():
    config.read("config.ini")
    print("----- VIEWING CATALOGUES INFO -----")
    print("\n")
    cat_list = [x for x in config.sections() if 'CATALOGUE' in x]
    for cat in cat_list:
        print("[" + cat + "]")
        for option in config.options(cat):
            print(option + " = " + config.get(cat, option))
        print("\n")
    print("-----------------------------------")
    return

def edit_catalogues():
    config.read("config.ini")
    print("----- EDITING CATALOGUE CONFIG DATA -----")
    
    cat_list = [x for x in config.sections() if 'CATALOGUE' in x]
    num_input = ""
    while True:
        count = 1
        print("You may enter 'cancel' at any time to exit.")
        for cat in cat_list:
            print(str(count) + ". " + config.get(cat, "name"))
            count += 1
        print("Enter number of the catalogue to edit: ", end="")

        num_input = input()
        if num_input == "cancel":
            break
        elif int(num_input) <= len(cat_list):
            cat_to_edit = cat_list[int(num_input) - 1]
            print("Type 'skip' to move to the next section.")
            print("Enter the full name of the catalogue: ", end="")
            cat_name = input()   
            if cat_name == "cancel":
                break
            elif cat_name == "skip":
                cat_name = config.get(cat_to_edit, "name")

            cat_short = ""
            while True:
                print("Enter a short file name for the catalogue (alphanumeric only): ", end="")
                cat_short = input()
                if cat_short == "cancel":
                    break
                elif cat_exists(cat_short):
                    print("Name already exists, please try again.")            
                elif cat_short.isalnum():
                    break
                else:
                    print("Invalid characters for short name, please try again.")
            if cat_short == "cancel":
                break
            elif cat_short == "skip":
                cat_short = cat_to_edit.lstrip("CATALOGUE_").lower()
                
            print("Enter the url link to csv file: ", end="")
            url_link = input()
            if url_link == "cancel":
                break
            elif url_link == "skip":
                url_link = config.get(cat_to_edit, "url")
    
            yesno = ""
            while True:
                
                print("\nCATALOGUE NAME: " + cat_name)
                print("SHORT FILE NAME: " + cat_short)
                print("URL: " + url_link)
                print("Is this info correct? (y/n): ", end="")
                yesno = input().lower()
                if yesno == "yes" or yesno == "y" or yesno == "no" or yesno == "n" or yesno == "cancel":
                    break
            print("\n")
            if yesno == "cancel":
                break        
            elif yesno == "yes" or yesno == "y":
                
                remove_conf(cat_to_edit)
                add_conf(cat_name, cat_short, url_link)
                
                print("Added catalogue data to config.ini")
                break
            break
        else:
            print("Invalid input\n")

    print("------------------------------------------")
    return

def add_catalogue():
    config.read("config.ini")
    TEMP_FOLDER = config.get("DIRECTORIES", "temp_data")
    TEMPLATES = config.get("DIRECTORIES", "templates")
    LOCAL_FOLDER = config.get("DIRECTORIES", "local_repo")
    PP_FOLDER = config.get("DIRECTORIES", "pp_scripts")
    
    print("----- ADDING NEW CATALOGUE -----")
    while True:
    
        print("You may enter 'cancel' at any time to exit.")
        print("Enter the full name of the catalogue: ", end="")
        cat_name = input()   
        if cat_name == "cancel":
            break

        cat_short = ""
        while True:
            print("Enter a short file name for the catalogue (alphanumeric only): ", end="")
            cat_short = input()
            if cat_short == "cancel":
                break
            elif cat_exists(cat_short):
                print("Name already exists, please try again.")            
            elif cat_short.isalnum():
                break
            else:
                print("Invalid characters for short name, please try again.")
        if cat_short == "cancel":
            break

        print("Enter the url link to csv file: ", end="")
        url_link = input()
        if url_link == "cancel":
            break

        yesno = ""
        while True:
            
            print("\nCATALOGUE NAME: " + cat_name)
            print("SHORT FILE NAME: " + cat_short)
            print("URL: " + url_link)
            print("Is this info correct? (y/n): ", end="")
            yesno = input().lower()
            if yesno == "yes" or yesno == "y" or yesno == "no" or yesno == "n" or yesno == "cancel":
                break
        print("\n")
        if yesno == "cancel":
            break        
        elif yesno == "yes" or yesno == "y":
            
            # Create template
            template_name = TEMPLATES + "/" + cat_short + "_template.xml"
            print("Created template in: ", end="")
            print(template_name)
            
            # Create repo
            repo_name = LOCAL_FOLDER + "/parsed_" + cat_short
            print("Created temporary repo folder in: ", end="")
            print(repo_name)
            
            # Create post-processing script
            pp_name = PP_FOLDER + "/pp_" + cat_short + ".py"
            print("Created post-processing script in: ", end="")
            print(pp_name)
            
            add_conf(cat_name, cat_short, url_link)
            
            print("Added catalogue data to config.ini")
            break
    print("--------------------------------")

'''
Checks if a catalogue name already exists
'''
def cat_exists(cat_name):
    config.read("config.ini")
    cat_list = [x.lstrip("CATALOGUE_") for x in config.sections() if 'CATALOGUE' in x]
    for cat in cat_list:
        if cat.lower() == cat_name.lower():
            return True
    return False

'''
Deletes a catalogue from configuration file
'''
def remove_conf(cat_name):
    with open("config.ini", "r") as f:
        config.readfp(f)
    config.remove_section(cat_name)
    with open("config.ini", "w") as f:
        config.write(f)

'''
Adds a catalogue to configuration file
'''
def add_conf(cat_name, cat_short, cat_url):
    # Writing to config file
    with open("config.ini", "a") as cwriter:
        cwriter.write("\n")
        cwriter.write("[CATALOGUE_" + cat_short.upper() + "]")
        cwriter.write("\n")
        cwriter.write("name        = " + cat_name)
        cwriter.write("\n")
        cwriter.write("url         = " + cat_url)
        cwriter.write("\n")
        cwriter.write("filename    = " + cat_short + ".csv")
        cwriter.write("\n")
        cwriter.write("template    = " + cat_short + "_template.xml")
        cwriter.write("\n")
        cwriter.write("parsed_dir  = " + "parsed_" + cat_short)
        cwriter.write("\n")
        cwriter.write("pp_script   = " + "pp_" + cat_short + ".py")
    cwriter.close()
