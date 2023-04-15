import sys

from PySide6.QtWidgets import QApplication

from gui import Accueil, Git, Author


class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.window = Accueil.get_instance()
        self.window.show()


    def run(self):
        self.exec()

        loop = True
        while loop:
            if self.window.action is not None:
                self.window = self.window.action
                self.window.show()
                self.exec()

            else:
                loop = False





if __name__ == '__main__':
    # Create the Qt Application
    app = App(sys.argv)

    # Run the main Qt loop
    sys.exit(app.run())