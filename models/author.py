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

import json

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import QItemDelegate, QLineEdit, QComboBox, QDateTimeEdit

import config
import customgit


class Author:

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __str__(self):
        return self.name + " <" + self.email + ">"

    def serialize(self):
        return {
            "name": self.name,
            "email": self.email
        }


def load(json):
    name = json["name"]
    email = json["email"]

    return Author(name, email)


def load_all(path):
    authors = []

    with open(path, "r") as file:
        all_json = json.load(file)

    for author in all_json:
        authors.append(load(author))

    return authors


class TableDelegate(QItemDelegate):
    def __init__(self):
        super().__init__()
        self.saved_status = True

    def createEditor(self, parent, option, index):
        # create a line edit
        self.saved_status = False
        return QLineEdit(parent)

    def setEditorData(self, editor: QLineEdit, index):
        # set the value of the line edit to the value of the item
        editor.setText(index.data(Qt.DisplayRole))

    def setModelData(self, editor: QLineEdit, model, index):
        # set the value of the item from the editor
        model.setData(index, editor.text())

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def is_saved(self):
        return self.saved_status

    def set_saved(self):
        self.saved_status = True


class TableDelegateList(QItemDelegate):

    __doc__ = "This class is used to display a list of authors in a popup menu."

    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        # create a popup menu
        if index.column() == 0:
            return QComboBox(parent)
        elif index.column() == 1:
            # create a date picker
            return QDateTimeEdit(parent)
        elif index.column() == 3:
            # cannot edit the hash
            return None
        else :
            return QLineEdit(parent)

    def setEditorData(self, editor: QLineEdit | QComboBox | QDateTimeEdit, index):
        # add all the authors to the popup menu
        if index.column() == 0:
            authors = load_all(config.authors_json)
            for author in authors:
                editor.addItem(str(author))
        elif index.column() == 1:
            # set the value of the date picker to the value of the item
            timestamp = customgit.get_timestamp(index.data(Qt.DisplayRole))
            date = QDateTime()
            date.setSecsSinceEpoch(timestamp)
            editor.setDateTime(date)
            editor.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        elif index.column() == 3:
            # cannot edit the hash
            return None
        else:
            editor.setText(index.data(Qt.DisplayRole))

    def setModelData(self, editor: QLineEdit | QComboBox | QDateTimeEdit, model, index):
        # set the value of the item from the editor
        if index.column() == 0:
            model.setData(index, editor.currentText())
        elif index.column() == 1:
            date_str = customgit.get_date(editor.dateTime().toSecsSinceEpoch())
            model.setData(index, date_str)
        elif index.column() == 3:
            # cannot edit the hash
            return None
        else:
            model.setData(index, editor.text())

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
