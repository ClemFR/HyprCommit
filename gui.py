import json
import time

from PySide6.QtCore import Qt, QObject, QEvent, QUrl, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, \
    QScrollArea, QMessageBox, QLineEdit, QFileDialog, QComboBox, QMenu, QMainWindow

import githubapi
import models.author as author
import config
import customgit

class Accueil(QDialog):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowTitle("Accueil")
        self.action = None

    def setupUi(self):
        # create a vertical layout
        self.verticalLayout = QVBoxLayout()

        # Add a welcome text
        label = QLabel("Bienvenue sur HyprCommit !")
        label.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(label)

        # create an horizontal layout
        self.horizontalLayout = QHBoxLayout()

        self.btn_open_git = QPushButton("Ouvrir un projet Git. . .")
        self.horizontalLayout.addWidget(self.btn_open_git)

        self.btn_author_presets = QPushButton("Créer des presets d'auteurs. . .")
        self.horizontalLayout.addWidget(self.btn_author_presets)

        # Add the horizontal layout to the vertical layout
        self.verticalLayout.addLayout(self.horizontalLayout)

        # set the layout to the dialog
        self.setLayout(self.verticalLayout)

        # connect the buttons to same functions
        self.btn_open_git.clicked.connect(lambda: self.btn_clicked("git"))
        self.btn_author_presets.clicked.connect(lambda: self.btn_clicked("author"))

    def clearAction(self):
        self.action = None
        print("clear")

    def btn_clicked(self, type):
        if type == "git":
            print("git")
            self.action = Git.get_instance()
        elif type == "author":
            print("author")
            self.action = Author.get_instance()
        self.close()

    def show(self) -> None:
        super().show()
        self.action = None

    @staticmethod
    def get_instance():
        if not hasattr(Accueil, "_instance"):
            Accueil._instance = Accueil()
        return Accueil._instance


class Git(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowTitle("Git")
        self.action = Accueil.get_instance()

    def setupUi(self):
        # create a vertical layout
        self.verticalLayout = QVBoxLayout()

        # Create horizontal layout
        line_git_path = QHBoxLayout()
        line_git_path.addWidget(QLabel("Chemin du projet Git : "))
        self.git_path_edit = QLineEdit()
        line_git_path.addWidget(self.git_path_edit)

        fb = QPushButton("...")
        fb.clicked.connect(self.file_browser)
        line_git_path.addWidget(fb)

        load = QPushButton("Charger")
        load.clicked.connect(self.load_git)
        line_git_path.addWidget(load)

        self.verticalLayout.addLayout(line_git_path)

        # Add the layout to the dialog
        self.setLayout(self.verticalLayout)

    def setupUi_gitBranches(self):
        # create a dropdown menu
        self.branches = self.git.get_branches()
        self.branches_dropdown = QComboBox()
        self.branches_dropdown.addItems(self.branches)

        branches_horizontal = QHBoxLayout()
        branches_horizontal.addWidget(QLabel("Branche : "))
        branches_horizontal.addWidget(self.branches_dropdown)
        current = self.git.get_current_branch()
        self.branches_dropdown.setCurrentText(current)
        self.branches_dropdown.currentTextChanged.connect(self.checkout)

        btn_branches = QPushButton("Charger les commits")
        btn_branches.clicked.connect(self.setupUi_gitCommit)
        branches_horizontal.addWidget(btn_branches)

        self.verticalLayout.addLayout(branches_horizontal)

    def setupUi_gitCommit(self):
        commits = self.git.get_all_commits()

        # create a table
        if hasattr(self, "table"):
            self.verticalLayout.removeWidget(self.table)

        self.table = QTableWidget()

        # Set the number of rows and columns
        self.table.setColumnCount(5)

        # Add the headers
        self.table.setHorizontalHeaderLabels(["Auteur", "Mail", "Date", "Message", ""])

        # Add the commits
        for i in range(len(commits)):
            self.table_add_line(commits[i], i)

        # Add the table if it doesn't exist inn the layout
        self.verticalLayout.addWidget(self.table)

    def table_add_line(self, commit, index):
        self.table.insertRow(index)
        self.table.setItem(index, 0, QTableWidgetItem(str(commit.author)))
        self.table.setItem(index, 1, QTableWidgetItem(str(commit.author.email)))
        self.table.setItem(index, 2, QTableWidgetItem(str(commit.authored_datetime)))
        self.table.setItem(index, 3, QTableWidgetItem(str(commit.message).strip()))

        btn = QPushButton("Editer. . . ")
        btn.clicked.connect(lambda: self.edit_commit(commit.hexsha))
        self.table.setCellWidget(index, 4, btn)

    def reject(self) -> None:
        def dialog_clicked(btn):
            if btn.text() == "&Yes":
                self.close()

        # Spawn a dialog to ask if the user really wants to quit
        print("reject")
        dialog = QMessageBox()
        dialog.setWindowTitle("Quitter")
        dialog.setText("Voulez-vous vraiment quitter ?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        dialog.setIcon(QMessageBox.Question)
        dialog.buttonClicked.connect(dialog_clicked)
        dialog.exec()

    def file_browser(self):
        print("file browser")
        fb = QFileDialog()
        fb.setFileMode(QFileDialog.Directory)
        fb.setOption(QFileDialog.ShowDirsOnly)
        url = QUrl.fromLocalFile(config.get_last_project())
        fb.setDirectoryUrl(url)
        fb.exec()

        self.git_path_edit.setText(fb.selectedFiles()[0])
        self.load_git()

    def load_git(self):
        try:
            self.git = customgit.Git(self.git_path_edit.text())
            config.set_last_project(self.git_path_edit.text())
            self.setupUi_gitBranches()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", "Le chemin spécifié n'est pas un projet Git valide.")
            raise e

    def checkout(self):
        if not self.git.set_branch(self.branches_dropdown.currentText()):
            QMessageBox.warning(self, "Erreur", "Impossible de changer de branche.")

    def edit_commit(self, commit_hash):
        amender = Amender(commit_hash, self.git)
        self.hide()
        amender.show()
        amender.exec()
        self.show()

        # update the table
        self.setupUi_gitCommit()

    @staticmethod
    def get_instance():
        if not hasattr(Git, "_instance"):
            Git._instance = Git()
        return Git._instance


class Author(QDialog):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowTitle("Author")
        self.action = Accueil.get_instance()

    def setupUi(self):
        # create a vertical layout
        self.verticalLayout = QVBoxLayout()

        # Add a button to search on github centered
        self.btn_search = QPushButton("Rechercher sur Github")
        self.btn_search.clicked.connect(self.search_github)
        self.verticalLayout.addWidget(self.btn_search)

        # Load all existing authors
        all = author.load_all(config.authors_json)

        # create a table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.delegate = author.TableDelegate()
        self.table.setItemDelegate(self.delegate)

        # Add the headers
        self.table.setHorizontalHeaderLabels(["Nom", "Email", " "])

        # Add the authors
        for i in range(len(all)):
            self.add_table_line(all[i].name, all[i].email)

        # Add the table to a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.table)

        # Add the scroll area to the vertical layout
        self.verticalLayout.addWidget(scroll)

        # Add a button to add a new author
        self.btn_add_author = QPushButton("Ajouter une ligne")

        # connect the button to the add function
        self.btn_add_author.clicked.connect(lambda: self.add_table_line(None, None))

        # Add a button to save the authors
        self.btn_save_authors = QPushButton("Sauvegarder les auteurs")

        # connect the button to the save function
        self.btn_save_authors.clicked.connect(self.save_authors)

        # Create an horizontal layout
        self.horizontalLayout = QHBoxLayout()

        # Add the buttons to the horizontal layout
        self.horizontalLayout.addWidget(self.btn_add_author)
        self.horizontalLayout.addWidget(self.btn_save_authors)

        # Add the horizontal layout to the vertical layout
        self.verticalLayout.addLayout(self.horizontalLayout)

        # set the layout to the dialog
        self.setLayout(self.verticalLayout)

    def add_table_line(self, name, email):
        self.table.insertRow(self.table.rowCount())
        if name is not None and email is not None:
            self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(name))
            self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(email))

        # Add a button to remove the author
        btn = QPushButton(" - ")
        self.table.setCellWidget(self.table.rowCount() - 1, 2, btn)

        # connect the button to the remove function
        btn.clicked.connect(lambda: self.remove_table_line(self.table.rowCount() - 1))

    def remove_table_line(self, row):
        self.table.removeRow(row)
        # Update all existing buttons in the table
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 2).clicked.connect(lambda: self.remove_table_line(i))

    def save_authors(self):
        # Create a list of authors
        authors = []
        for i in range(self.table.rowCount()):
            authors.append(author.Author(self.table.item(i, 0).text(), self.table.item(i, 1).text()))

        with open(config.authors_json, "w") as f:
            f.write(json.dumps([a.__dict__ for a in authors], indent=4))

        self.delegate.set_saved()

    def closeEvent(self, event):
        if not self.delegate.is_saved():
            reply = QMessageBox.question(self, 'Message',
                                         "Voulez-vous sauvegarder les modifications ?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.save_authors()

        super().closeEvent(event)

    def search_github(self):
        search_wdw = GithubSearch()
        search_wdw.show()
        search_wdw.exec()

        if search_wdw.username is not None and search_wdw.email_selected is not None:
            self.add_table_line(search_wdw.username, search_wdw.email_selected)


    @staticmethod
    def get_instance():
        if not hasattr(Author, "_instance"):
            Author._instance = Author()
        return Author._instance


class Amender(QDialog):

    def __init__(self, commit_hash, git):
        super().__init__()
        self.git = git
        self.commit_hash = commit_hash
        self.setupUi()
        self.setWindowTitle("Amender")
        self.action = Git.get_instance()

    def setupUi(self):
        # create a vertical layout
        self.verticalLayout = QVBoxLayout()

        # Create a table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setItemDelegate(author.TableDelegateList())

        # Add the headers
        self.table.setHorizontalHeaderLabels(["Nom / Email", "Date", "Message", "Hash"])

        commits = self.git.get_all_commit_amend(self.commit_hash)
        for i in range(len(commits)):
            self.add_table_line(str(commits[i].author), commits[i].author.email, str(commits[i].authored_datetime), str(commits[i].message).strip(), commits[i].hexsha)

        # Add the table to a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.table)

        # Add the scroll area to the vertical layout
        self.verticalLayout.addWidget(scroll)

        # create a button to update the project with the new modifications
        self.btn_update = QPushButton("Envoyer la purée...")
        self.btn_update.clicked.connect(self.update)

        # Add the button to the vertical layout
        self.verticalLayout.addWidget(self.btn_update)

        # Add the vertical layout to the dialog
        self.setLayout(self.verticalLayout)

    def add_table_line(self, name, email, date, message, hash):
        self.table.insertRow(self.table.rowCount())
        print(f"Adding {name} {email} {date} {message} {hash}")

        self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(f"{name} <{email}>"))
        self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(date))
        self.table.setItem(self.table.rowCount() - 1, 2, QTableWidgetItem(message))
        self.table.setItem(self.table.rowCount() - 1, 3, QTableWidgetItem(hash))

    def update(self):
        # backup the current branch
        self.git.backup_project()

        # detect if the commit is the first commit of the project
        if self.git.get_first_commit() == self.commit_hash:
            self.git.init_amend("", root=True)
            print(f"Amending root because first commit (hash = {self.commit_hash})")
        else:
            self.git.init_amend(self.commit_hash)

        # loop into the table to get the new commits in reversed order
        for i in range(self.table.rowCount() - 1, -1, -1):
            author = self.table.item(i, 0).text()
            date = self.table.item(i, 1).text()
            message = self.table.item(i, 2).text()

            self.git.amend_next(author, date, message)

        # displaying success popup
        QMessageBox.information(self, "Succès", "Le projet a été mis à jour avec succès !\n En cas de problème, vous pouvez toujours revenir à la version précédente en utilisant la backup")

        # close the dialog
        self.close()


class GithubSearch(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowTitle("Recherche Github")
        self.action = Author.get_instance()

        self.username = None
        self.email_selected = None


    def setupUi(self):
        # create a vertical layout
        self.verticalLayout = QVBoxLayout()

        # Create an input to search for a github user with a button to the right
        self.input = QLineEdit()
        self.input.setPlaceholderText("Rechercher un utilisateur Github")
        self.btn_search = QPushButton("Rechercher")
        self.btn_search.clicked.connect(self.search)

        # Add info button to the right of the input
        icon_info = QIcon().fromTheme("dialog-information")
        btn_infoapi = QPushButton(icon_info, "")
        btn_infoapi.setToolTip("Informations sur l'API GitHub")
        btn_infoapi.setStyleSheet("QToolTip { color: #000000; background-color: #ffffff; border: 1px solid black; }")
        btn_infoapi.clicked.connect(self.message_infoapi)

        # Create a horizontal layout to add the input and the button
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.input)
        horizontalLayout.addWidget(self.btn_search)
        horizontalLayout.addWidget(btn_infoapi)

        # Add the horizontal layout to the vertical layout
        self.verticalLayout.addLayout(horizontalLayout)

        # Create a table
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Email"])

        # Add the table to a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.table)

        # Add the scroll area to the vertical layout
        self.verticalLayout.addWidget(scroll)

        # Create a button to add the selected email to the author list
        btn_add = QPushButton("Ajouter")
        btn_add.clicked.connect(self.add_email)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(lambda: self.close())

        hboxlayout = QHBoxLayout()
        hboxlayout.addWidget(btn_cancel)
        hboxlayout.addWidget(btn_add)

        self.verticalLayout.addLayout(hboxlayout)

        # Add layout to the dialog
        self.setLayout(self.verticalLayout)

    def search(self):
        self.btn_search.setDisabled(True)

        if self.input.text().strip() != "":
            self.username = self.input.text()
            emails = githubapi.get_user_email(self.username)

            # check if email is a string or a list of string
            if emails is not None:
                if isinstance(emails, str):
                    emails = [emails]

                self.table.setRowCount(0)
                for email in emails:
                    self.table.insertRow(self.table.rowCount())
                    email_field = QTableWidgetItem(email)
                    # disable edit of the email
                    email_field.setFlags(email_field.flags() ^ Qt.ItemIsEditable)
                    self.table.setItem(self.table.rowCount() - 1, 0, email_field)
            else:
                QMessageBox.warning(self, "Erreur", f"Aucun email trouvé pour l'utilisateur {self.username}")
        self.btn_search.setEnabled(True)


    def add_email(self):
        # get current selected email in the table
        self.email_selected = self.table.item(self.table.currentRow(), 0).text()
        self.username = self.input.text()
        self.close()

    def message_infoapi(self, force_refresh=False):
        reponse, reponse_ok = githubapi.rate_limit(do_not_refresh=not force_refresh)
        if reponse_ok:
            QMessageBox.information(self, "Informations sur l'API GitHub", reponse)
        else:
            # messagebox with a button to force refresh
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(reponse)
            btn_ok = msg.addButton("Forcer le rafraîchissement", QMessageBox.AcceptRole)
            defbtn = msg.addButton("Annuler", QMessageBox.RejectRole)
            msg.setDefaultButton(defbtn)
            msg.show()
            msg.exec()
            if msg.clickedButton() == btn_ok:
                self.message_infoapi(force_refresh=True)





