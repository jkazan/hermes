import os
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from jira import HJira
from dialog import Login

from photoviewer import PhotoViewer

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Hermes'
        self.path = os.path.dirname(os.path.abspath(__file__))+'/'
        self.initUI()
        self.b1 = QtWidgets.QPushButton()
        self.hjira = HJira()

    def initUI(self):
        self.setupMainWindow()

        # Central layout
        central_widget, layout = self.setupCentralLayout()

        # Side menu
        side_menu, side_menu_container = self.sideMenu()
        layout.addWidget(side_menu_container)

        # Main field
        self.main_field, self.main_field_container = self.mainField()
        layout.addWidget(self.main_field_container)
        self.main_field.setContentsMargins(0,0,0,0)

        # Jira top menu
        self.jira_top_menu_container = QWidget()
        self.jira_top_menu_container.hide()
        self.jira_top_menu_container.setStyleSheet(
            "background-color: rgba(31, 60, 81, 255);")
        jira_top_menu = QtWidgets.QHBoxLayout(self.jira_top_menu_container)
        self.jira_top_menu_container.setFixedHeight(90)
        self.main_field.addWidget(self.jira_top_menu_container)

        # Install top menu
        self.install_top_menu_container = QWidget()
        self.install_top_menu_container.hide()
        self.install_top_menu_container.setStyleSheet(
            "background-color: rgba(31, 60, 81, 255);")
        install_top_menu = QtWidgets.QHBoxLayout(self.install_top_menu_container)
        self.install_top_menu_container.setFixedHeight(90)
        self.main_field.addWidget(self.install_top_menu_container)

        # Main field bottom
        self.main_field_bottom_container = QWidget()
        self.main_field_bottom_container.setStyleSheet(
            "background-color: rgba(15, 15, 15, 255);")
        self.main_field_bottom = QtWidgets.QGridLayout(self.main_field_bottom_container)

        # Jira button in side menu
        b_jira = self.createButton("jira", "jira.png", self.showJira,[])
        b_jira.pressed.connect(self.login)

        l_jira = self.createButtonLabel("Jira")
        side_menu.addWidget(b_jira)
        side_menu.addWidget(l_jira)
        side_menu.addStretch(1)

        # Install button in side menu
        b_install = self.createButton("install", "install.png", self.showInstall,[])
        l_install = self.createButtonLabel("Install")
        side_menu.addWidget(b_install)
        side_menu.addWidget(l_install)
        side_menu.addStretch(1)

        # Settings button in side menu
        b_settings = self.createButton("settings", "settings.png")
        l_settings = self.createButtonLabel("Settings")
        side_menu.addWidget(b_settings)
        side_menu.addWidget(l_settings)
        side_menu.addStretch(1)

        # Stretch side menu to move buttons up
        side_menu.addStretch(10)

        # Jira top menu
        b_tickets = self.createButton("tickets",
                                          "tickets.png",
                                          self.tickets,
                                          [self.main_field_bottom])

        b_graph = self.createButton("graph",
                                        "graph.png",
                                        self.graph,
                                        [self.main_field_bottom])

        b_log = self.createButton("log",
                                      "log.png",
                                      self.graph,
                                      [self.main_field_bottom])

        b_comments = self.createButton("comments",
                                           "comments.png",
                                           self.graph,
                                           [self.main_field_bottom])

        jira_top_menu.addWidget(b_tickets)
        jira_top_menu.addWidget(b_graph)
        jira_top_menu.addWidget(b_log)
        jira_top_menu.addWidget(b_comments)

        # Install top menu
        b_e3 = self.createButton("e3", "e3.png")
        b_css = self.createButton("css", "css.png")
        b_plcfactory = self.createButton("plcf", "install.png")
        b_beast = self.createButton("beast", "install.png")
        install_top_menu.addWidget(b_e3)
        install_top_menu.addWidget(b_css)
        install_top_menu.addWidget(b_plcfactory)
        install_top_menu.addWidget(b_beast)





        self.main_field.addWidget(self.main_field_bottom_container)
        self.jira_top_menu_container.show()
        self.setCentralWidget(central_widget)
        self.show()

    def setupMainWindow(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        # Window size
        self.resize(1024, 768)
        self.setMinimumSize(800, 400)
        # self.setMaximumSize(1920, 1080)

        # Center window
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        # self.setStyleSheet("background-color: rgba(53, 53, 53, 255);");
        self.setProperty("windowOpacity", 0.95);

    def setupCentralLayout(self):
        # Central widget for the main window
        central_widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        central_widget.setLayout(layout)
        central_widget.setStyleSheet("background-color:black;")
        return central_widget, layout

    def sideMenu(self):
        side_menu_container = QWidget(self)
        side_menu_container.setFixedWidth(90)
        side_menu_container.setStyleSheet("background-color:black;")
        side_menu = QtWidgets.QVBoxLayout(side_menu_container)
        return side_menu, side_menu_container

    def mainField(self):
        self.main_field_container = QWidget(self)
        self.main_field_container.setStyleSheet("background-color: rgba(15, 15, 15, 255);")
        self.main_field = QtWidgets.QVBoxLayout(self.main_field_container)
        return self.main_field, self.main_field_container

    def createButton(self, name, icon, function=None, args=None):
        b = QtWidgets.QPushButton()
        b.setStyleSheet("border: none;")
        b.setIcon(QIcon(self.path + icon))
        b.setIconSize(QSize(64, 64))
        b.setCheckable(True)
        b.pressed.connect(lambda:self.pressed(b, name))
        b.released.connect(lambda:self.released(b, name))

        if function is not None:
            b.clicked.connect(lambda:function(*args))

        return b

    def createButtonLabel(self, label):
        l = QLabel(label)
        l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        l.setStyleSheet("color:white;")
        l.setAlignment(Qt.AlignCenter)
        return l

    def tickets(self, layout):
        tickets, issue_types, summaries, progress = self.hjira.tickets()
        for i in range(len(tickets)):
            lticket = QLabel(tickets[i])
            lticket.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            lticket.setStyleSheet("color:white;")
            lticket.setAlignment(Qt.AlignCenter)

            lissue = QLabel(issue_types[i])
            lissue.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            lissue.setStyleSheet("color:white;")
            lissue.setAlignment(Qt.AlignCenter)

            lprogress = QLabel(progress[i])
            lprogress.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            lprogress.setStyleSheet("color:white;")
            lprogress.setAlignment(Qt.AlignCenter)

            lsummary = QLabel(summaries[i])
            lsummary.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            lsummary.setStyleSheet("color:white;")
            lsummary.setAlignment(Qt.AlignCenter)

            layout.addWidget(lticket, i, 0, Qt.AlignLeft)
            layout.addWidget(lissue, i, 1, Qt.AlignLeft)
            layout.addWidget(lprogress, i, 2, Qt.AlignLeft)
            layout.addWidget(lsummary, i, 3, Qt.AlignLeft)

    def graph(self, layout):
        inp = QtWidgets.QInputDialog(self)

        ##### SOME SETTINGS
        inp.setInputMode(QtWidgets.QInputDialog.TextInput)
        inp.setFixedSize(300, 20)
        inp.setOption(QtWidgets.QInputDialog.UsePlainTextEditForTextInput)
        p = inp.palette()
        p.setColor(inp.backgroundRole(), QtCore.Qt.darkCyan)
        inp.setPalette(p)

        inp.setWindowTitle('Epic')
        inp.setLabelText('Enter Epic:')

        if inp.exec_() == QtWidgets.QDialog.Accepted:
            text = inp.textValue()
            file_name = self.hjira.graph(text)
            viewer = PhotoViewer(self)
            viewer.setPhoto(QtGui.QPixmap(file_name))
            # viewer._zoom += 1
            # viewer._zoom -= 1
            viewer.fitInView()
            layout.addWidget(viewer)
        else:
            return

        inp.deleteLater()


        # diag = QtWidgets.QInputDialog(self)
        # p = diag.palette()
        # p.setColor(diag.backgroundRole(), QtCore.Qt.red)
        # diag.setPalette(p)

        # diag.setStyleSheet("background-color:blue;")
        # text, ok = diag.getText(self, 'Text Input Dialog', 'Enter Epic:')

        # pw = QtGui.QLineEdit()
        # setEchoMode(QtGui.QLineEdit.Password)

        # if ok:
        #     file_name = self.hjira.graph(text)
        #     print(file_name)
        #     viewer = PhotoViewer(self)
        #     viewer.setPhoto(QtGui.QPixmap(file_name))
        #     # viewer._zoom += 1
        #     # viewer._zoom -= 1
        #     viewer.fitInView()
        #     layout.addWidget(viewer)


    def pressed(self, b, i):
        b.setIcon(QIcon(self.path + i + '_pressed.png'))

    def released(self, b, i):
        b.setIcon(QIcon(self.path + i + '.png'))

    def test(self):
        print("yes")

    def login(self):
        path = os.path.dirname(os.path.abspath(__file__))+'/'
        login = Login(self.hjira, path+"login.png", path+"cancel.png")

    def showInstall(self):
        self.jira_top_menu_container.hide()
        self.install_top_menu_container.show()

    def showJira(self):
        self.jira_top_menu_container.show()
        self.install_top_menu_container.hide()

    def btnstate(self, b, i):
        print("{} button pressed " .format(i))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    test = Login()
    sys.exit(app.exec_())
