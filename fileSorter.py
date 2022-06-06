import pandas as pd
import shutil
import json
import re
from os import listdir, remove, mkdir
from os.path import isfile, join, exists
import sys

dataFolderPaths = ["../FP_BeliefState_SMAcomp", "../BeliefState_ProbSwitch"]
schemaFolder = "../schemaFolder/"
sortFolder = "../sortFolder/"
resultFolder = "../resultFolder/"

allSchemaDict = {}

# sets up the schemaFolder (containing all the options), the sortFolder, the resultFolder
def setup():
    try:
        mkdir("../schemaFolder")
        print("schemaFolder created.")
    except FileExistsError:
        print("schemaFolder ready.")
    try:
        mkdir("../sortFolder")
        print("sortFolder created.")
    except FileExistsError:
        print("sortFolder ready.")
    try:
        mkdir(resultFolder)
        print("destFolder created.")
    except FileExistsError:
        print("destFolder ready.")
    try:
        df = pd.DataFrame()
        f = open("../resultFolder/MasterSheet.csv", "x")
        df.to_csv("../resultFolder/MasterSheet.csv")
        f.close()
    except FileExistsError:
        print("MasterSheet ready.")




# edits the JSON file of the given option to add or remove options,
# toggle whether the field is optional, or delete the set of options
def edit_options(edit_mode, schema_name, value=""):
    if not exists(schemaFolder + schema_name):
        print("This file does not exist.")
    else:
        if edit_mode.lower() == "add":
            dict_current = json.load(schemaFolder + schema_name)
            dict_current[schema_name].append(value)
            with open(schemaFolder + schema_name + '.json', 'w') as f:
                json.dump(dict_current, f)
        elif edit_mode.lower() == "remove":
            dict_current = json.load(schemaFolder + schema_name)
            dict_current[schema_name].remove(value)
            with open(schemaFolder + schema_name + '.json', 'w') as f:
                json.dump(dict_current, f)
        elif edit_mode.lower() == "delete":
            remove(schemaFolder + schema_name)
        elif edit_mode.lower() == "toggle_optional":
            dict_current = json.load(schemaFolder + schema_name)
            dict_current["is_optional"] = not dict_current["is_optional"]
            if not dict_current["is_optional"]:
                print(schema_name + " is required.")
            else:
                print(schema_name + " is optional.")
            with open(schemaFolder + schema_name + '.json', 'w') as f:
                json.dump(dict_current, f)


def create_options(field_name):
    new_dict = {field_name: [], "is_optional": False}
    new_json = json.dumps(new_dict)
    # will overwrite if it finds a file with the same name
    with open(schemaFolder + field_name + '.json', 'w') as f:
        json.dump(new_dict, f)


def get_all_schema():
    full_dict = {}
    for filename in listdir(schemaFolder):
        f = join(schemaFolder, filename)
        # checking if it is a file
        if isfile(f):
            this_dict = json.load(f)
            full_dict[filename[:-4]] = this_dict
    return full_dict


def get_df():
    this_dataframe = pd.read_csv("../resultFolder/MasterSheet.csv")
    return this_dataframe


def save_df(df):
    pd.to_csv("../resultFolder/MasterSheet.csv")


def process_func(processmode):
    if processmode == 0: # process original folders only
        process_files_into_pd(dataFolderPaths)
    elif processmode == 1:
        process_files_into_pd(["../sortFolder/"])



def process_files_into_pd(folderList):
    full_dict = get_all_schema()
    df = get_df()
    FPvalue = False
    for folderName in folderList:
        for filename in listdir(folderName):
            this_object = {}
            # f = join(folderName, filename)
            current_file = filename
            current_file = current_file.replace(' ', '')
            current_file = current_file.replace('-', '_')
            current_decomped = current_file.split('_')
            for field in full_dict:
                for poss_value in full_dict[field][field]:
                    isfound = False
                    if bool(re.search(poss_value, current_file)) and not isfound:
                        this_object[field] = re.search(poss_value, current_file).group()
                        isfound = True
                if not (field in this_object) and not full_dict[field]["is_optional"]:
                    shutil.copyfile(join(folderName, filename), "../sortFolder/" + filename)
                    break
            df = df.append(this_object)
            if filename in listdir(sortFolder):
                remove(join(sortFolder, filename))
        save_df(df)
    report_savefolder()
    # make some note of this run so that the save folder can be used next time


def report_savefolder():
    print("The following files have been unprocessed and stored in sortFolder: \n")
    filelist = listdir(sortFolder)
    for filename in filelist:
        print(filename)
    print("\n" + len(filelist) + "files unprocessed.")



if sys.argv[1] == "setup":
    setup()
elif sys.argv[1] == "editOption":
    # fix this for user input
    if len(sys.argv) == 4:
        edit_options(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        edit_options(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Incorrect number of arguments.")
elif sys.argv[1] == "createOption":
    if len(sys.argv) == 3:
        create_options(sys.argv[2])
    else:
        print("Incorrect number of arguments.")
elif sys.argv[1] == "process":
    if len(sys.argv) == 3:
        create_options(sys.argv[2])
    else:
        print("Incorrect number of arguments.")
else:
    print('not ready yet')