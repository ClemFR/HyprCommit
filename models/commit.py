from PySide6.QtWidgets import QItemDelegate, QLineEdit


class TableDelegate(QItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        # create a line edit
        print("createEditor")

    def setEditorData(self, editor: QLineEdit, index):
        # set the value of the line edit to the value of the item
        pass

    def setModelData(self, editor: QLineEdit, model, index):
        # set the value of the item from the editor
        pass

    def updateEditorGeometry(self, editor, option, index):
        # set the geometry of the editor
        pass
