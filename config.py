# Copyright 2023 Clement L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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