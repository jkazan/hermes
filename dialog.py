import sys
import os
import time
import json

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton)
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

class External(QThread):
    """
    Runs a external thread.
    """
    loading_signal = pyqtSignal(bool)

    def __init__(self, jira, cmd, args, parent=None):
        super(External, self).__init__(parent)
        self.jira = jira
        self.cmd = cmd
        self.args = args
        self.response_ok = False

    def run(self):
        self.loading_signal.emit(True)
        login_ok = self.jira.login(*self.args)
        if login_ok:
            self.response_ok = True

        self.loading_signal.emit(False)

class Login(QDialog):
    """
    Simple dialog that consists of a Progress Bar and a Button.
    Clicking on the button results in the start of a timer and
    updates the progress bar.
    """
    def __init__(self, jira, jira_ui, uis):
        super().__init__()
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.movie = QtGui.QMovie(self.path + "imgs/loading.gif")
        self.jira = jira
        self.jira_ui = jira_ui
        self.uis = uis
        self.login_ok = False

        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: rgba(36, 70, 122, 200);")
        self.setWindowTitle("Login")

        # Main layout
        main_layout_container = QtWidgets.QWidget(self)
        main_layout_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        main_layout = QtWidgets.QVBoxLayout(main_layout_container)

        # Title
        self.l_title = QtWidgets.QLabel("Enter username and password")
        self.l_title.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.l_title.setStyleSheet("color:white;")
        self.l_title.setAlignment(QtCore.Qt.AlignCenter)

        # Edit layout
        edit_layout_container = QtWidgets.QWidget(self)
        edit_layout = QtWidgets.QVBoxLayout(edit_layout_container)

        # Username
        self.ef_user = self.createEditField("Username")

        # Password
        self.ef_pass = self.createEditField("Password")
        self.ef_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        # Add edit fields to edit layout
        edit_layout.addWidget(self.ef_user)
        edit_layout.addWidget(self.ef_pass)

        # Check if remembered
        file_path = os.path.dirname(os.path.abspath(__file__))+"/jira.user"
        remembered = False
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                #TODO: try getting the user, user may have corrupted the file!
                remembered_user = json_data['user']
                self.ef_user.insert(remembered_user)
                remembered = True

        # Checkbox
        checkbox_container = QtWidgets.QWidget(self)
        checkbox_container.setFixedHeight(35)
        checkbox_layout = QtWidgets.QHBoxLayout(checkbox_container)
        checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.c_remember = QtWidgets.QCheckBox("Remember me")
        self.c_remember.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.c_remember.setStyleSheet("""
            QCheckBox {
            color:white;
            }

            QCheckBox::indicator {
            background-color:rgba(16, 50, 100, 200);
            color:white;
            width: 14px;
            height: 14px;
            }

            QCheckBox::indicator:checked {
            image: url("""+self.path+"""checkmark.png);
            }
            """)
        if remembered:
            self.c_remember.setCheckState(2)

        checkbox_layout.addWidget(self.c_remember)

        # Button layout
        button_layout_container = QtWidgets.QWidget(self)
        button_layout_container.setFixedHeight(50)
        button_layout = QtWidgets.QHBoxLayout(button_layout_container)

        # Add login button
        b_login = QtWidgets.QPushButton()
        b_login.setStyleSheet("border: none;")
        b_login.setIcon(QtGui.QIcon(self.path+"login.png"))
        b_login.setIconSize(QtCore.QSize(100, 100))
        b_login.setCheckable(True)
        b_login.pressed.connect(lambda:self.pressed(self.path+"login.png"))
        b_login.released.connect(lambda:self.released(self.path+"login.png"))
        button_layout.addWidget(b_login)

        # Add cancel button
        b_cancel = QtWidgets.QPushButton()
        b_cancel.setStyleSheet("border: none;")
        b_cancel.setIcon(QtGui.QIcon(self.path+"cancel.png"))
        b_cancel.setIconSize(QtCore.QSize(100, 100))
        b_cancel.setCheckable(True)
        b_cancel.pressed.connect(lambda:self.pressed(self.path+"cancel.png"))
        b_cancel.released.connect(lambda:self.released(self.path+"cancel.png"))
        b_cancel.clicked.connect(self.close)
        button_layout.addWidget(b_cancel)

        # Add loading gif
        self.l_loading = QtWidgets.QLabel(self) # widget for holding movie

        self.l_loading.setFixedHeight(40)
        self.l_loading.setAlignment(QtCore.Qt.AlignCenter)
        self.movie.setScaledSize(QtCore.QSize(40, 40))
        self.l_loading.setMovie(self.movie)

        self.empty = QtWidgets.QPushButton(self) # widget for holding empty image
        self.empty.hide()
        self.empty.setIcon(QtGui.QIcon(self.path + "empty.png"))
        self.empty.setFixedHeight(40)
        self.empty.setStyleSheet("border: none;")

        main_layout.addWidget(self.l_title)
        main_layout.addWidget(edit_layout_container)
        main_layout.addWidget(checkbox_container)
        main_layout.addWidget(self.l_loading)
        main_layout.addWidget(self.empty)
        main_layout.addWidget(button_layout_container)

        # Fix window size to fit content)
        self.setFixedSize(main_layout.sizeHint())

        self.show()

        b_login.clicked.connect(self.onButtonClick)

    # def showHide(self):
    #     if self.l_loading.isVisible():
    #         self.l_loading.hide()
    #     else:
    #         self.l_loading.show()

    def onButtonClick(self):
        args = [self.ef_user.text(), self.ef_pass.text()]
        self.calc = External(self.jira, "login", args)
        self.calc.loading_signal.connect(self.loading)
        self.calc.start()

    def loading(self, load):
        if load:
            self.empty.hide()
            self.l_loading.show()
            self.movie.start()
        else:
            self.l_title.setStyleSheet("color:rgba(239, 64, 64, 255);")
            self.movie.stop()
            self.l_loading.hide()
            self.empty.show()

            if self.calc.response_ok:
                self.login_ok = True
                if self.c_remember.isChecked:
                    file_path = os.path.dirname(os.path.abspath(__file__)) + "/jira.user"

                    # Read current data
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                        json_data["user"] = self.ef_user.text()

                    # Save our changes to JSON file
                    with open(file_path, 'w') as f:
                        f.write(json.dumps(json_data))

                self.close()
                self.showMe()
            else:
                self.l_title.setText("Invalid credentials, try again!")

    def createEditField(self, text):
        ef = QtWidgets.QLineEdit()
        ef.setPlaceholderText(text)
        ef.setFixedWidth(220)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        ef.setStyleSheet("background-color: rgba(16, 50, 100, 200); color:white; border: none;")
        return ef

    def pressed(self, icon_path):
        b = self.sender()
        split = icon_path.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self, icon_path):
        b = self.sender()
        b.setIcon(QtGui.QIcon(icon_path))

    def showMe(self):
        for ui in self.uis:
                ui.hide()

        self.jira_ui.show()


