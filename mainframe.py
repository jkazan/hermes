import os
import time
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from jira import HJira
from dialog import Login
import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.loading_done = QtCore.pyqtSignal(int)
        theme = "dark"
        self.top_menus = []
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.movie = QtGui.QMovie(self.path + "loading.gif")
        # self.movie.start()
        self.empty = QtWidgets.QPushButton()
        self.l_loading = QtWidgets.QLabel() # widget for holding movie
        self.logged_in = False
        if theme == "dark":
            self.colors = {
                "window" : "black",
                "side" : "black",
                "main" : "rgba(15, 15, 15, 255)",
                "top" : "rgba(31, 81, 60, 255)",
                }
        elif theme == "light":
            self.colors = {
                "window" : "rgba(100, 100, 100, 255)",
                "side" : "rgba(100, 100, 100, 255)",
                "main" : "white",
                "top" : "rgba(224, 195, 174, 255)",
                }

        self.title = "Hermes"
        self.jira = HJira()

        self.initUI()

    def initUI(self):
        # Main window
        self.setupMainWindow()

        # Central layout
        w_central, hbox_central = self.setupCentralLayout(self.colors["window"])

        # Side Menu
        w_side_menu, vbox_side_menu, side_buttons = self.setupSideMenu(self.colors["side"])

        # Main field
        w_main_field, vbox_main_field = self.setupMainField(self.colors["main"])

        # Set central widget
        self.setCentralWidget(w_central)

        # Add side menu and main field
        hbox_central.addWidget(w_side_menu)
        hbox_central.addWidget(w_main_field)

        # Jira top menu
        self.jira_top_menu = TopMenu(self.colors["top"], {
            "Tickets" : self.path+"tickets.png",
            "Graph" : self.path+"graph.png",
            "Log Work" : self.path+"log.png",
            "Comments" : self.path+"comments.png",
            })
        b_graph = self.jira_top_menu.buttons[1]
        # b_graph.clicked.connect(self.graph)
        self.top_menus.append(self.jira_top_menu)
        vbox_main_field.addWidget(self.jira_top_menu)
        # vbox_main_field.addStretch(10)

        # Install top menu
        self.install_top_menu = TopMenu(self.colors["top"], {
            "e3" : self.path+"e3.png",
            "css" : self.path+"css.png",
            "plcfactory" : self.path+"settings.png",
            "beast" : self.path+"settings.png",
            })
        side_buttons["install"].clicked.connect(lambda:self.showTop(self.install_top_menu))
        self.top_menus.append(self.install_top_menu)
        vbox_main_field.addWidget(self.install_top_menu)

        # Settings top menu
        self.settings_top_menu = TopMenu(self.colors["top"], {
            "User" : self.path+"e3.png",
            "Theme" : self.path+"css.png",
            "Whatever" : self.path+"settings.png",
            })
        # side_buttons["settings"].clicked.connect(self.showTop(self.settings_top_menu))
        side_buttons["settings"].clicked.connect(lambda:self.showTop(self.settings_top_menu))
        self.top_menus.append(self.settings_top_menu)
        vbox_main_field.addWidget(self.settings_top_menu)

        vbox_main_field.addStretch(10)

        self.show()

    def setupMainWindow(self):
        self.setWindowTitle(self.title)

        # Window size
        self.resize(1024, 768)
        self.setMinimumSize(800, 400)

        # Center window
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setProperty("windowOpacity", 0.95);

    def setupCentralLayout(self, color):
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        widget.setLayout(layout)
        widget.setStyleSheet("background-color:"+color+";")
        return widget, layout

    def setupSideMenu(self, color):
        widget = QtWidgets.QWidget(self)
        widget.setFixedWidth(85)
        widget.setStyleSheet("background-color:"+color+";")
        layout = QtWidgets.QVBoxLayout(widget)

        # Jira button in side menu
        b_jira, l_jira = self.createButton("Jira", self.path + "jira.png")
        b_jira.clicked.connect(self.login)

        # Install button in side menu
        b_install, l_install = self.createButton("Install", self.path + "install.png")
        # b_install.pressed.connect(self.install)

        # Settings button in side menu
        b_settings, l_settings = self.createButton("Settings", self.path + "settings.png")
        # b_settings.pressed.connect(self.settings)

        # Add all to layout
        layout.addWidget(b_jira)
        layout.addWidget(l_jira)
        layout.addStretch(1)

        layout.addWidget(b_install)
        layout.addWidget(l_install)
        layout.addStretch(1)

        layout.addWidget(b_settings)
        layout.addWidget(l_settings)
        layout.addStretch(1)

        # Stretch side menu to move buttons up
        layout.addStretch(10)

        # Add loading gif to side menu
        self.l_loading.setFixedHeight(60)
        self.l_loading.setAlignment(QtCore.Qt.AlignCenter)
        self.movie.setScaledSize(QtCore.QSize(40, 40))
        self.l_loading.setMovie(self.movie)
        self.l_loading.hide()
        self.empty.setIcon(QtGui.QIcon(self.path + "empty.png"))
        self.empty.setFixedHeight(60)
        self.empty.setStyleSheet("border: none;")
        layout.addWidget(self.l_loading)
        layout.addWidget(self.empty)

        side_buttons = {
            "jira" : b_jira,
            "install" : b_install,
            "settings" : b_settings,
            }

        return widget, layout, side_buttons

    def setupMainField(self, color):
        widget = QtWidgets.QWidget(self)
        widget.setStyleSheet("background-color:"+color+";")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        return widget, layout

    def createButton(self, label, icon_path):
        b = QtWidgets.QPushButton()
        b.setStyleSheet("border: none;")
        b.setIcon(QtGui.QIcon(icon_path))
        b.setIconSize(QtCore.QSize(64, 64))
        b.setCheckable(True)
        b.pressed.connect(lambda:self.pressed(icon_path))
        b.released.connect(lambda:self.released(icon_path))

        l = QtWidgets.QLabel(label)
        l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        l.setStyleSheet("color:white;")
        l.setAlignment(QtCore.Qt.AlignCenter)

        return b, l

    def pressed(self, i):
        b = self.sender()
        split = i.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self, i):
        b = self.sender()
        b.setIcon(QtGui.QIcon(i))

    def login(self):
        if not self.jira.loggedin:
            b_login = QtWidgets.QPushButton()
            login_dialog = Login(self.jira, self.jira_top_menu)

    def showTop(self, menu):
        self.hideTops()
        menu.show()

    def hideTops(self):
        for menu in self.top_menus:
            menu.hide()


# class External(QtCore.QThread):
#     def __init__(self, mainwindow, parent=None):
#         self.mainwindow = mainwindow
#         self.mainwindow.movie.start()
#     def run(self):
#         self.mainwindow.loading_done.connect(stopLoading)

#     def stopLoading(self, value):
#         if self.mainwindow.jira.loggedin:
#             # self.mainwindow.showTop(self.mainwindow.jira_top_menu)
#             self.mainwindow.top_menus[0].show()
#         self.mainwindow.movie.stop()


class TopMenu(QtWidgets.QWidget):
    def __init__(self, color, spec):
        super().__init__()
        self.color = color
        self.spec = spec
        self.buttons = []
        self.icon_paths = []
        self.initUI()

    def initUI(self):
        self.hide()
        self.setStyleSheet("background-color: "+self.color+";")
        self.setFixedHeight(100)
        menu_layout = QtWidgets.QHBoxLayout(self)
        menu_layout.setContentsMargins(0,0,0,0)
        menu_layout.setSpacing(0)

        for label, icon_path in self.spec.items():
            vbc = QtWidgets.QWidget()
            vb = QtWidgets.QVBoxLayout(vbc)
            vb.setContentsMargins(0,5,0,0)

            b = self.createButton(icon_path)

            l = QtWidgets.QLabel(label)
            l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            l.setStyleSheet("color:white;")
            l.setAlignment(QtCore.Qt.AlignCenter)

            vb.addWidget(b)
            vb.addWidget(l)
            menu_layout.addWidget(vbc)

    def pressed(self, b, i):
        name = i.split('.',1)
        print(name[0] + '_pressed.png')
        b.setIcon(QtGui.QIcon(name[0] + '_pressed.png'))

    def released(self, b, i):
        name = i.split('.',1)
        b.setIcon(QtGui.QIcon(name[0] + '.png'))

    def createButton(self, icon_path):
        b = QtWidgets.QPushButton()
        b.setStyleSheet("border: none;")
        b.setIcon(QtGui.QIcon(icon_path))
        b.setIconSize(QtCore.QSize(64, 64))
        b.setCheckable(True)
        b.pressed.connect(lambda:self.pressed(b, icon_path))
        b.released.connect(lambda:self.released(b, icon_path))
        self.buttons.append(b)

        return b

    def buttons(self):
        return self.buttons
