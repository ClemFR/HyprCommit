import os
import json

# Path to the directory containing the data files
data_dir = os.path.join(os.path.dirname(__file__), "data")

authors_json = os.path.join(data_dir, "authors.json")

git_editor_path = os.path.join(os.path.dirname(__file__), "editor_script.py")

settings = os.path.join(data_dir, "settings.json")


# Check if the data directory / files exist and create them if not
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

if not os.path.exists(authors_json):
    with open(authors_json, "w") as file:
        file.write("[]")



# ==================== Settings ====================

if not os.path.exists(settings):
    default_settings = {"last_project": os.path.expanduser("~"), "gh_api_key": "null"}

    with open(settings, "w") as file:
        file.write(json.dumps(default_settings, indent=4))


def set_last_project(path):
    global settings
    with open(settings, "r") as file:
        loaded_settings = json.load(file)

    loaded_settings["last_project"] = path

    with open(settings, "w") as file:
        file.write(json.dumps(loaded_settings, indent=4))


def get_last_project():
    global settings
    with open(settings, "r") as file:
        loaded_settings = json.load(file)

    return loaded_settings["last_project"]

def get_gh_api_key():
    global settings
    with open(settings, "r") as file:
        loaded_settings = json.load(file)

    return loaded_settings["gh_api_key"]