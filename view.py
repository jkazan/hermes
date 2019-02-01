import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from jira import HJira
from jiraui import JiraUI
from installui import InstallUI
from settingsui import SettingsUI
from sidebar import Sidebar

class View(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setTheme("dark")

    def initUI(self):
        self.setWindowTitle("Hermes")
        # Window size
        self.resize(1024, 768)
        self.setMinimumSize(800, 400)

        # Central layout
        w_central, hbox_central = self.setupCentralLayout()
        hbox_central.setContentsMargins(0,0,0,0)
        hbox_central.setSpacing(0)

        # Set central widget
        self.setCentralWidget(w_central)

        # Sidebar
        self.sidebar = Sidebar()

        # Jira page
        self.jira_ui = JiraUI()

        # Install page
        self.install_ui = InstallUI()

        # Settings page
        self.settings_ui = SettingsUI()

        # Boot page
        self.boot_ui = QtWidgets.QWidget()

        # Add side menu and main field
        hbox_central.addWidget(self.sidebar)
        hbox_central.addWidget(self.jira_ui)
        hbox_central.addWidget(self.install_ui)
        hbox_central.addWidget(self.settings_ui)
        hbox_central.addWidget(self.boot_ui)


        self.show()

    def getUI(self, name):
        if name.lower() == "jira":
            return self.jira_ui
        elif name.lower() == "install":
            return self.install_ui
        elif name.lower() == "settings":
            return self.settings_ui
        elif name.lower() == "boot":
            return self.boot_ui
        else:
            raise

    def setTheme(self, theme):
        if theme.lower() == "dark":
            self.colors = {
                "window" : "black",
                "side" : "black",
                "main" : "rgba(40, 40, 40, 255)",
                "top" : "rgba(36, 70, 122, 255)",
                "font" : "white",
                "edit" : "rgba(10, 10, 10, 255)",
                }
        elif theme == "light":
            self.colors = {
                "window" : "rgba(100, 100, 100, 255)",
                "side" : "rgba(226, 176, 115, 255)",
                "main" : "white",
                "top" : "rgba(211, 242, 255)",
                "font" : "black",
                "edit" : "rgba(229, 207, 167, 255)",
                }

        uis = [self.jira_ui, self.install_ui, self.settings_ui]
        for ui in uis:
            ui.getTopMenu().setStyleSheet("background-color:"+self.colors["top"]+";")
            ui.getTopMenu().setFontColor(self.colors["font"])
            ui.setTheme(self.colors)
            for key, field in ui.getMainFields().items():
                field.setStyleSheet("background-color:"+self.colors["main"]+";")

        self.setStyleSheet("background-color:"+self.colors["main"]+";")
        self.sidebar.setStyleSheet("background-color:"+self.colors["side"]+";")
        self.sidebar.setFontColor(self.colors["font"])


    def setupCentralLayout(self):
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout()
        widget.setLayout(layout)
        return widget, layout

    def getSidebarButtons(self):
        return self.sidebar.getButtons()

    def getJiraUI(self):
        return self.jira_ui

    def getSidebar(self):
        return self.sidebar
