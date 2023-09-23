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