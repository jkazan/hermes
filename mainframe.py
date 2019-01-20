# import os
# import sys
from PyQt5 import QtWidgets
# from PyQt5 import QtGui
# from PyQt5 import QtCore
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel
# from PyQt5.QtGui import QIcon, QPixmap
# from PyQt5.QtCore import Qt, QSize
# from jira import HJira
# from dialog import Login, Dialog

# from photoviewer import PhotoViewer

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        theme = "dark"
        if theme == "dark":
            self.colors = {
                "window" : "black",
                "side" : "black",
                "main" : "rgba(15, 15, 15, 255)",
                }
        else:
            self.colors = {
                "window" : "rgba(100, 100, 100, 255)",
                "side" : "rgba(100, 100, 100, 255)",
                "main" : "white",
                }

        self.title = 'Hermes'
        self.initUI()


    def initUI(self):
        # Main window
        self.setupMainWindow()

        # Central layout
        w_central, hbox_central = self.setupCentralLayout(self.colors["window"])

        # Side Menu
        w_side_menu, vbox_side_menu = self.setupSideMenu(self.colors["side"])

        # Main field
        w_main_field, vbox_main_field = self.setupMainField(self.colors["main"])

        self.setCentralWidget(w_central)
        hbox_central.addWidget(w_side_menu)
        hbox_central.addWidget(w_main_field)

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
        return widget, layout

    def setupMainField(self, color):
        widget = QtWidgets.QWidget(self)
        widget.setStyleSheet("background-color:"+color+";")
        layout = QtWidgets.QVBoxLayout(widget)
        return widget, layout






#         self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
#         self.top_menus = []
#         self.initUI()
#         self.b1 = QtWidgets.QPushButton()
#         self.hjira = HJira()

#     def initUI(self):
#         self.setupMainWindow()

#         # Central layout
#         central_widget, layout = self.setupCentralLayout()

#         # Side menu
#         side_menu, side_menu_container = self.sideMenu()
#         layout.addWidget(side_menu_container)
#         side_menu.setContentsMargins(5,15,0,0)

#         # Main field
#         self.main_field, self.main_field_container = self.mainField()
#         layout.addWidget(self.main_field_container)
#         self.main_field.setContentsMargins(0,0,0,0)

#         # Jira top menu
#         self.jira_top_menu = TopMenu({
#             "Tickets" : self.path+"tickets.png",
#             "Graph" : self.path+"graph.png",
#             "Log Work" : self.path+"log.png",
#             "Comments" : self.path+"comments.png",
#             })
#         b_graph = self.jira_top_menu.buttons[1]
#         b_graph.clicked.connect(self.graph)
#         self.top_menus.append(self.jira_top_menu)
#         self.main_field.addWidget(self.jira_top_menu)

#         # Install top menu
#         self.install_top_menu = TopMenu({
#             "e3" : self.path+"e3.png",
#             "css" : self.path+"css.png",
#             "plcfactory" : self.path+"settings.png",
#             "beast" : self.path+"settings.png",
#             })
#         self.top_menus.append(self.install_top_menu)
#         self.main_field.addWidget(self.install_top_menu)

#         # Settings top menu
#         self.settings_top_menu = TopMenu({
#             "User" : self.path+"e3.png",
#             "Theme" : self.path+"css.png",
#             "Whatever" : self.path+"settings.png",
#             })
#         self.top_menus.append(self.settings_top_menu)
#         self.main_field.addWidget(self.settings_top_menu)

#         # Main field bottom
#         self.main_field_bottom_container = QWidget()
#         self.main_field_bottom_container.setStyleSheet(
#             "background-color: rgba(15, 15, 15, 255);")
#         self.main_field_bottom = QtWidgets.QGridLayout(self.main_field_bottom_container)

#         # Jira button in side menu
#         b_jira = self.createButton("jira", "jira.png",
#                                        self.showTopMenu,[self.jira_top_menu])

#         b_jira.pressed.connect(self.login) #TODO: do this for the function send
#                                            #to createButton too

#         l_jira = self.createButtonLabel("Jira")
#         side_menu.addWidget(b_jira)
#         side_menu.addWidget(l_jira)
#         side_menu.addStretch(1)

#         # Install button in side menu
#         b_install = self.createButton("install", "install.png",
#                                           self.showTopMenu,
#                                           [self.install_top_menu])

#         l_install = self.createButtonLabel("Install")
#         side_menu.addWidget(b_install)
#         side_menu.addWidget(l_install)
#         side_menu.addStretch(1)

#         # Settings button in side menu
#         b_settings = self.createButton("settings", "settings.png",
#                                            self.showTopMenu,
#                                            [self.settings_top_menu])

#         l_settings = self.createButtonLabel("Settings")
#         side_menu.addWidget(b_settings)
#         side_menu.addWidget(l_settings)
#         side_menu.addStretch(1)

#         # Stretch side menu to move buttons up
#         side_menu.addStretch(10)

#         # Add loading gif to side menu
#         self.l_loading = QtWidgets.QLabel()
#         self.l_loading.setAlignment(QtCore.Qt.AlignCenter)
#         path = os.path.dirname(os.path.abspath(__file__))+'/'
#         self.movie = QtGui.QMovie(path + "loading.gif")
#         self.movie.setScaledSize(QtCore.QSize(40, 40))
#         self.l_loading.setMovie(self.movie)
#         side_menu.addWidget(self.l_loading)


#         self.main_field.addWidget(self.main_field_bottom_container)
#         self.setCentralWidget(central_widget)
#         self.show()

#     def setupMainWindow(self):
#         self.setWindowTitle(self.title)
#         # self.setGeometry(self.left, self.top, self.width, self.height)

#         # Window size
#         self.resize(1024, 768)
#         self.setMinimumSize(800, 400)
#         # self.setMaximumSize(1920, 1080)

#         # Center window
#         qtRectangle = self.frameGeometry()
#         centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
#         qtRectangle.moveCenter(centerPoint)
#         self.move(qtRectangle.topLeft())
#         # self.setStyleSheet("background-color: rgba(53, 53, 53, 255);");
#         self.setProperty("windowOpacity", 0.95);

#     def setupCentralLayout(self):
#         # Central widget for the main window
#         central_widget = QtWidgets.QWidget(self)
#         layout = QtWidgets.QHBoxLayout()
#         layout.setContentsMargins(0,0,0,0)
#         central_widget.setLayout(layout)
#         central_widget.setStyleSheet("background-color:black;")
#         return central_widget, layout

#     def sideMenu(self):
#         side_menu_container = QWidget(self)
#         side_menu_container.setFixedWidth(85)
#         side_menu_container.setStyleSheet("background-color:black;")
#         side_menu = QtWidgets.QVBoxLayout(side_menu_container)
#         return side_menu, side_menu_container

#     def mainField(self):
#         self.main_field_container = QWidget(self)
#         self.main_field_container.setStyleSheet("background-color: rgba(15, 15, 15, 255);")
#         self.main_field = QtWidgets.QVBoxLayout(self.main_field_container)
#         return self.main_field, self.main_field_container

#     def createButton(self, name, icon, function=None, args=None):
#         b = QtWidgets.QPushButton()
#         b.setStyleSheet("border: none;")
#         b.setIcon(QIcon(self.path + icon))
#         b.setIconSize(QSize(64, 64))
#         b.setCheckable(True)
#         b.pressed.connect(lambda:self.pressed(b, name))
#         b.released.connect(lambda:self.released(b, name))

#         if function is not None:
#             b.clicked.connect(lambda:function(*args))

#         return b

#     def createButtonLabel(self, label):
#         l = QLabel(label)
#         l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
#         l.setStyleSheet("color:white;")
#         l.setAlignment(Qt.AlignCenter)
#         return l

#     def tickets(self, layout):
#         tickets, issue_types, summaries, progress = self.hjira.tickets()
#         for i in range(len(tickets)):
#             lticket = QLabel(tickets[i])
#             lticket.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
#             lticket.setStyleSheet("color:white;")
#             lticket.setAlignment(Qt.AlignCenter)

#             lissue = QLabel(issue_types[i])
#             lissue.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
#             lissue.setStyleSheet("color:white;")
#             lissue.setAlignment(Qt.AlignCenter)

#             lprogress = QLabel(progress[i])
#             lprogress.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
#             lprogress.setStyleSheet("color:white;")
#             lprogress.setAlignment(Qt.AlignCenter)

#             lsummary = QLabel(summaries[i])
#             lsummary.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
#             lsummary.setStyleSheet("color:white;")
#             lsummary.setAlignment(Qt.AlignCenter)

#             layout.addWidget(lticket, i, 0, Qt.AlignLeft)
#             layout.addWidget(lissue, i, 1, Qt.AlignLeft)
#             layout.addWidget(lprogress, i, 2, Qt.AlignLeft)
#             layout.addWidget(lsummary, i, 3, Qt.AlignLeft)

#     def graph(self):
#         d = Dialog(self.hjira, "Graph", self.path+"login.png",
#                        self.path+"cancel.png")

#         if d.accepted:
#             ticket = d.text()
#             file_name = self.hjira.graph(ticket)
#             viewer = PhotoViewer(self)
#             viewer.setPhoto(QtGui.QPixmap(file_name))
#             viewer.fitInView()
#             self.main_field_bottom.addWidget(viewer)
#         else:
#             return

#     def pressed(self, b, i):
#         b.setIcon(QIcon(self.path + i + '_pressed.png'))

#     def released(self, b, i):
#         b.setIcon(QIcon(self.path + i + '.png'))

#     def login(self):
#         if not self.hjira.loggedin:
#             login = Login(self.hjira, self.path+"login.png",
#                               self.path+"cancel.png", self.path+"checkmark.png")
#             if login.loginOk():
#                 self.showTopMenu(self.jira_top_menu)

#     def showTopMenu(self, menu):
#         self.hideTop()
#         menu.show()

#     def hideTop(self):
#         for menu in self.top_menus:
#             menu.hide()

# class TopMenu(QtWidgets.QWidget):
#     def __init__(self, spec):
#         super().__init__()
#         self.spec = spec
#         self.buttons = []
#         self.icon_paths = []
#         self.initUI()

#     def initUI(self):
#         self.hide()
#         self.setStyleSheet("background-color: rgba(31, 60, 81, 255);")
#         self.setFixedHeight(100)
#         menu_layout = QtWidgets.QHBoxLayout(self)
#         menu_layout.setContentsMargins(0,0,0,0)
#         menu_layout.setSpacing(0)

#         for label, icon_path in self.spec.items():
#             vbc = QtWidgets.QWidget()
#             vb = QtWidgets.QVBoxLayout(vbc)
#             vb.setContentsMargins(0,5,0,0)

#             b = self.createButton(icon_path)

#             l = QLabel(label)
#             l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
#             l.setStyleSheet("color:white;")
#             l.setAlignment(Qt.AlignCenter)

#             vb.addWidget(b)
#             vb.addWidget(l)
#             menu_layout.addWidget(vbc)

#     def pressed(self, b, i):
#         name = i.split('.',1)
#         print(name[0] + '_pressed.png')
#         b.setIcon(QIcon(name[0] + '_pressed.png'))

#     def released(self, b, i):
#         name = i.split('.',1)
#         b.setIcon(QIcon(name[0] + '.png'))

#     def createButton(self, icon_path):
#         b = QtWidgets.QPushButton()
#         b.setStyleSheet("border: none;")
#         b.setIcon(QIcon(icon_path))
#         b.setIconSize(QSize(64, 64))
#         b.setCheckable(True)
#         b.pressed.connect(lambda:self.pressed(b, icon_path))
#         b.released.connect(lambda:self.released(b, icon_path))
#         self.buttons.append(b)

#         return b

#     def buttons(self):
#         return self.buttons
