import os
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from jira import HJira

class Login(QtWidgets.QDialog):
    def __init__(self, hjira, login_icon_path, cancel_icon_path, parent=None):
        super(Login, self).__init__(parent)
        self.hjira = hjira
        self.button_icon_paths = [login_icon_path, cancel_icon_path]
        self.setStyleSheet("background-color: rgba(36, 70, 122, 200);")
        self.setWindowTitle("Login")
        self.diag_title = "Enter username and password"
        self.edit_labels = ["Username:", "Password:"]
        self.edit_fields = []
        self.buttons = []

        # Main layout
        main_layout_container = QtWidgets.QWidget(self)
        main_layout_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        main_layout = QtWidgets.QVBoxLayout(main_layout_container)

        # Title
        l_title = QtWidgets.QLabel(self.diag_title)
        l_title.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        l_title.setStyleSheet("color:white;")
        l_title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(l_title)

        # Edit layout
        edit_layout_container = QtWidgets.QWidget(self)
        edit_layout_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        edit_layout = QtWidgets.QGridLayout(edit_layout_container)

        # Username
        l_user, ef_user = self.createEditField("Username:")
        edit_layout.addWidget(l_user, 0, 0)
        edit_layout.addWidget(ef_user, 0, 1)
        self.edit_fields.append(ef_user)

        # Password
        l_pass, ef_pass = self.createEditField("Password:")
        ef_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        edit_layout.addWidget(l_pass, 1, 0)
        edit_layout.addWidget(ef_pass, 1, 1)
        self.edit_fields.append(ef_pass)

        # Add edit layout to main
        main_layout.addWidget(edit_layout_container)

        # Button layout
        button_layout_container = QtWidgets.QWidget(self)
        button_layout_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        button_layout = QtWidgets.QHBoxLayout(button_layout_container)

        # Add login button
        b_login = self.createButton(login_icon_path)
        b_login.clicked.connect(self.login)
        self.buttons.append(b_login)
        button_layout.addWidget(b_login)

        # Add cancel button
        b_cancel = self.createButton(cancel_icon_path)
        b_cancel.clicked.connect(self.close)
        button_layout.addWidget(b_cancel)
        self.buttons.append(b_cancel)

        # Add button layout to main
        main_layout.addWidget(button_layout_container)

        # Fix window size to fit content
        self.setFixedSize(main_layout.sizeHint())

        # Execute
        self.exec_()

    def createEditField(self, label):
        l = QtWidgets.QLabel(label)
        l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        l.setStyleSheet("color:white;")
        l.setAlignment(QtCore.Qt.AlignRight)

        ef = QtWidgets.QLineEdit()
        ef.setFixedWidth(220)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        ef.setStyleSheet("background-color: rgba(16, 50, 100, 200); color:white; border: none;")

        return l, ef

    def createButton(self, icon_path):
        b = QtWidgets.QPushButton()
        b.setStyleSheet("border: none;")
        b.setIcon(QtGui.QIcon(icon_path))
        b.setIconSize(QtCore.QSize(100, 100))
        b.setCheckable(True)
        b.pressed.connect(self.pressed)
        b.released.connect(self.released)
        return b

    def pressed(self):
        b = self.sender()
        icon_path = self.button_icon_paths[self.buttons.index(b)]
        split = icon_path.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self):
        b = self.sender()
        icon_path = self.button_icon_paths[self.buttons.index(b)]
        b.setIcon(QtGui.QIcon(icon_path))

    def login(self):
        self.hjira.login()
        self.close()
