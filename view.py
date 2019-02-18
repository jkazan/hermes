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

    def initUI(self):
        self.setWindowTitle("Hermes")
        # Window size
        self.resize(1024, 768)
        self.setMinimumSize(800, 450)

        # Central layout
        w_central, hbox_central = self.setupCentralLayout()

        # Set central widget
        self.setCentralWidget(w_central)

        # Sidebar
        self.sidebar = Sidebar()

        # Jira page
        self.jira_ui = JiraUI()
        self.jira_ui.hide()

        # Install page
        self.install_ui = InstallUI()
        self.install_ui.hide()

        # Settings page
        self.settings_ui = SettingsUI()
        self.settings_ui.hide()

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

    def setTheme(self, colors):
        self.jira_ui.setTheme(colors)
        self.install_ui.setTheme(colors)
        self.settings_ui.setTheme(colors)
        self.sidebar.setTheme(colors)
        self.setStyleSheet("background-color:"+colors["main"]+";")

    def setupCentralLayout(self):
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        return widget, layout

    def getSidebarButtons(self):
        return self.sidebar.getButtons()

    def getSidebar(self):
        return self.sidebar
