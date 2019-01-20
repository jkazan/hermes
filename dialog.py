import os
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from jira import HJira
import threading
import time
import json

class Login(QtWidgets.QDialog):
    def __init__(self, hjira, login_icon_path, cancel_icon_path,
                     checkmark_icon_path, parent=None):
        super(Login, self).__init__(parent)
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.user_file = "jira.user"
        self.login_thread = LoginThread(self)
        self.remembered = False
        self.login_ok = False
        self.hjira = hjira
        self.icon_paths = [login_icon_path, cancel_icon_path, checkmark_icon_path]
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
        self.l_title = QtWidgets.QLabel(self.diag_title)
        self.l_title.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.l_title.setStyleSheet("color:white;")
        self.l_title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.l_title)

        # Edit layout
        edit_layout_container = QtWidgets.QWidget(self)
        edit_layout = QtWidgets.QVBoxLayout(edit_layout_container)

        # Username
        self.ef_user = self.createEditField("Username")
        edit_layout.addWidget(self.ef_user)
        self.edit_fields.append(self.ef_user)

        # Password
        self.ef_pass = self.createEditField("Password")
        self.ef_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        edit_layout.addWidget(self.ef_pass)
        self.edit_fields.append(self.ef_pass)

        # Check if remembered
        if os.path.isfile(self.path+self.user_file):
            with open(self.path+self.user_file, 'r') as f:
                json_data = json.load(f)
                #TODO: try getting the user, user may have corrupted the file!
                self.remembered_user = json_data['user']
                self.ef_user.insert(self.remembered_user)
                # edit_layout_container.setTabOrder(self.ef_pass, self.ef_user)
                self.remembered = True
                self.ef_pass.setFocus()

        # Add edit layout to main
        main_layout.addWidget(edit_layout_container)

        # Checkbox
        checkbox_container = QtWidgets.QWidget(self)
        checkbox_container.setFixedHeight(35)
        checkbox_layout = QtWidgets.QHBoxLayout(checkbox_container)
        self.c_remember = QtWidgets.QCheckBox("Remember me")
        self.c_remember.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.c_remember.setStyleSheet("""
            QCheckBox {
            color:white;
            }

            QCheckBox::indicator {
            background-color:rgba(16, 50, 100, 200);
            width: 16px;
            height: 16px;
            }

            QCheckBox::indicator:checked {
            image: url("""+checkmark_icon_path+""");
            }
            """)
        if self.remembered:
            self.c_remember.setCheckState(2)
        # self.c_remember.setStyleSheet("color:white;")
        # self.c_remember.stateChanged.connect(self.remember)
        checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
        checkbox_layout.addWidget(self.c_remember)
        main_layout.addWidget(checkbox_container)

        # Button layout
        button_layout_container = QtWidgets.QWidget(self)
        button_layout_container.setFixedHeight(50)

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
        s = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Expanding)
        main_layout.addItem(s)

        # Add loading gif
        self.l_loading = QtWidgets.QLabel()
        self.l_loading.setAlignment(QtCore.Qt.AlignCenter)
        path = os.path.dirname(os.path.abspath(__file__))+'/'
        self.movie = QtGui.QMovie(path + "loading.gif")
        self.movie.setScaledSize(QtCore.QSize(40, 40))
        self.l_loading.setMovie(self.movie)
        main_layout.addWidget(self.l_loading)

        # Fix window size to fit content)
        self.setFixedSize(main_layout.sizeHint())

        # Execute
        self.exec_()

    def createEditField(self, text):
        ef = QtWidgets.QLineEdit()
        ef.setPlaceholderText(text)
        ef.setFixedWidth(220)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        ef.setStyleSheet("background-color: rgba(16, 50, 100, 200); color:white; border: none;")

        return ef

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
        icon_path = self.icon_paths[self.buttons.index(b)]
        split = icon_path.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self):
        b = self.sender()
        icon_path = self.icon_paths[self.buttons.index(b)]
        b.setIcon(QtGui.QIcon(icon_path))

    def login(self):
        # Check if not remembered, but want to remember
        if not self.remembered or self.ef_user.text() != self.remembered_user:
            if self.c_remember.isChecked:
                with open(self.path+'/'+self.user_file, 'w') as f:
                    f.write('{"user":"'+self.ef_user.text()+'"}')

        self.movie.start()
        self.l_loading.setVisible(True)
        self.login_thread.start()

    def loginOk(self):
        return self.login_thread.loginOk()

class LoginThread(QtCore.QThread):

    def __init__(self, w):
        QtCore.QThread.__init__(self)
        self.w = w
        self.login_ok = False

    def __del__(self):
        self.wait()

    def run(self):
        user = self.w.edit_fields[0].text()
        password = self.w.edit_fields[1].text()
        self.login_ok = self.w.hjira.login(user, password)
        if self.login_ok:
            self.w.l_loading.setVisible(False)
            self.w.close()
        else:
            self.w.l_loading.setVisible(False)
            self.w.l_title.setText("Invalid credentials, try again!")
            self.w.l_title.setStyleSheet("color:red;")

    def loginOk(self):
        return self.login_ok


class Dialog(QtWidgets.QDialog):
    def __init__(self, hjira, window_title, ok_icon_path, cancel_icon_path, parent=None):
        super(Dialog, self).__init__(parent)
        self.accepted = False
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        # self.thread = LoginThread(self)
        self.hjira = hjira
        self.icon_paths = [ok_icon_path, cancel_icon_path]
        self.setStyleSheet("background-color: rgba(36, 70, 122, 200);")
        self.setWindowTitle(window_title)
        self.diag_title = "Enter Jira ticket"
        # self.edit_labels = ["Username:", "Password:"]
        # self.edit_fields = []
        self.buttons = []

        # Main layout
        main_layout_container = QtWidgets.QWidget(self)
        main_layout_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        main_layout = QtWidgets.QVBoxLayout(main_layout_container)

        # Title
        self.l_title = QtWidgets.QLabel(self.diag_title)
        self.l_title.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.l_title.setStyleSheet("color:white;")
        self.l_title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.l_title)

        # Edit layout
        edit_layout_container = QtWidgets.QWidget(self)
        edit_layout = QtWidgets.QVBoxLayout(edit_layout_container)

        # Ticket
        self.ef_ticket = self.createEditField("Ticket")
        edit_layout.addWidget(self.ef_ticket)
        # self.edit_fields.append(self.ef_ticket)

        # Add edit layout to main
        main_layout.addWidget(edit_layout_container)

        # Button layout
        button_layout_container = QtWidgets.QWidget(self)
        button_layout_container.setFixedHeight(50)
        button_layout = QtWidgets.QHBoxLayout(button_layout_container)

        # Add ok button
        b_ok = self.createButton(ok_icon_path)
        b_ok.clicked.connect(self.ok)
        self.buttons.append(b_ok)
        button_layout.addWidget(b_ok)

        # Add cancel button
        b_cancel = self.createButton(cancel_icon_path)
        b_cancel.clicked.connect(self.close)
        button_layout.addWidget(b_cancel)
        self.buttons.append(b_cancel)

        # Add button layout to main
        main_layout.addWidget(button_layout_container)
        s = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Expanding)
        main_layout.addItem(s)

        # Add loading gif
        self.l_loading = QtWidgets.QLabel()
        self.l_loading.setAlignment(QtCore.Qt.AlignCenter)
        path = os.path.dirname(os.path.abspath(__file__))+'/'
        self.movie = QtGui.QMovie(path + "loading.gif")
        self.movie.setScaledSize(QtCore.QSize(40, 40))
        self.l_loading.setMovie(self.movie)
        main_layout.addWidget(self.l_loading)

        # Fix window size to fit content)
        self.setFixedSize(main_layout.sizeHint())

        # Execute
        self.exec_()

    def createEditField(self, text):
        ef = QtWidgets.QLineEdit()
        ef.setPlaceholderText(text)
        ef.setFixedWidth(220)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        ef.setStyleSheet("background-color: rgba(16, 50, 100, 200); color:white; border: none;")

        return ef

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
        icon_path = self.icon_paths[self.buttons.index(b)]
        split = icon_path.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self):
        b = self.sender()
        icon_path = self.icon_paths[self.buttons.index(b)]
        b.setIcon(QtGui.QIcon(icon_path))

    def ok(self):
        self.accepted = True
        self.close()
        # self.movie.start()
        # self.l_loading.setVisible(True)

    def text(self):
        return self.ef_ticket.text()
