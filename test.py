import os
import json
from functools import partial
from topmenu import TopMenu
from jiraui import JiraUI
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from mainfield import TicketField
from sidebar import Sidebar
from view import View
from jira import HJira
from workers import TicketWorker, GraphWorker, LogWorker
from dialog import Login
import time

class TestClass(QtCore.QObject):
    loading_signal = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        app = QtWidgets.QApplication([])

        self.view = View()
        self.toggleTheme()
        self.uis = [self.view.getUI("Jira"),
                        self.view.getUI("Install"),
                        self.view.getUI("Settings"),
                        self.view.getUI("Boot"),
                        ]

        self.jira = HJira()
        self.connectJiraTop()
        self.jira_ticket_worker = TicketWorker(self.view.getUI("Jira"), self.jira)
        self.jira_graph_worker = GraphWorker(self.view.getUI("Jira"), self.jira)
        self.jira_log_worker = LogWorker(self.view.getUI("Jira"), self.jira)
        self.loading_signals_count = 0

        self.connectSidebar(self.uis)

        self.connectSettings()

        app.exec_()

    def connectSettings(self):
        radiobutton = self.view.getUI("Settings").getTheme()
        radiobutton.toggled.connect(self.toggleTheme)

    def toggleTheme(self):
        radiobutton = self.view.getUI("Settings").getTheme()
        if radiobutton.isChecked():
            self.view.setTheme({
                "window" : "white",
                "side" : "rgb(230, 230, 230)",
                "main" : "white",
                "top" : "rgb(142, 186, 255)",
                "font" : "black",
                "edit" : "rgb(206,255,171)",
                "graph": [245, 245, 245], # list because it's the input to QColor object
                "completer" : "rgb(142, 186, 255)",
                })
        else:
            self.view.setTheme({
                "window" : "black",
                "side" : "black",
                "main" : "rgb(40, 40, 40)",
                "top" : "rgb(36, 70, 122)",
                "font" : "white",
                "edit" : "rgba(10, 10, 10, 255)",
                "graph": [30, 30, 30],
                "completer" : "rgb(36, 70, 122)",
                })

    def connectSidebar(self, uis):
        buttons = self.view.getSidebar().getButtons()
        buttons[0].clicked.connect(self.login)
        for i in range(len(buttons)):
            buttons[i].clicked.connect(partial(self.showUI, uis[i]))

    def showUI(self, ui):
        if ui == self.view.getUI("Jira"):
            if not self.jira.loggedin:
                return

        for i in self.uis:
            if i != ui:
                i.hide()

        ui.show()


    def login(self):
        if not self.jira.loggedin:
            b_login = QtWidgets.QPushButton()
            login_dialog = Login(self.jira, self.view.getUI("Jira"), self.uis)

    def connectJiraTop(self):
        # Top menu buttons
        buttons = self.view.getUI("Jira").getTopMenu().getButtons()
        for b in buttons:
            if b.objectName() == "Tickets":
                b.clicked.connect(self.tickets)
            elif b.objectName() == "Graph":
                b.clicked.connect(self.graph)
            elif b.objectName() == "Log":
                b.clicked.connect(self.log)
            elif b.objectName() == "Comments":
                b.clicked.connect(self.comments)

        # Main field buttons
        b_tickets = self.view.getUI("Jira").getMainFields()["tickets"].getButton()
        b_tickets.clicked.connect(self.getTickets)
        b_graph = self.view.getUI("Jira").getMainFields()["graph"].getButton()
        b_graph.clicked.connect(self.getGraph)
        b_log = self.view.getUI("Jira").getMainFields()["log"].getSendButton()
        b_log.clicked.connect(self.getLog)
        b_clear_log = self.view.getUI("Jira").getMainFields()["log"].getClearButton()
        b_clear_log.clicked.connect(self.clearLog)

    def graph(self):
        self.showMainField("graph")

    def getGraph(self):
        self.toggleTheme()
        self.jira_graph_worker.loading_signal.connect(self.loading)
        self.jira_graph_worker.data_signal.connect(self.setGraphData)
        self.jira_graph_worker.start()

    def setGraphData(self, graph_path):
        # Check if ticket exists
        if graph_path == "None":
            main_field = self.view.getUI("Jira").getMainFields()["graph"]
            edit_field = main_field.getEditFields()[0]
            edit_field.setStyleSheet("background-color: red;")
            return

        viewer = self.view.getUI("Jira").getMainFields()["graph"].getGraphViewer()
        viewer.setPhoto(QtGui.QPixmap(graph_path))

    def log(self):
        self.showMainField("log")

    def getLog(self):
        self.toggleTheme()
        self.jira_log_worker.loading_signal.connect(self.loading)
        self.jira_log_worker.data_signal.connect(self.sendLogData)
        self.jira_log_worker.start()

    def clearLog(self):
        edit_fields = self.view.getUI("Jira").getMainFields()["log"].getEditFields()
        for col, efs in edit_fields.items():
            for ef in efs:
                ef.clear()

    def sendLogData(self, response, row):
        impath = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        json_path = os.path.dirname(os.path.abspath(__file__))+'/jira.user'

        edit_fields = self.view.getUI("Jira").getMainFields()["log"].getEditFields()
        confirm_icons = self.view.getUI("Jira").getMainFields()["log"].getConfirmIcons()
        if response.status_code == 201:
            # Open jira.user file and update statistics
            tickets = {} #TODO: is it right to init this like this?
            if os.path.isfile(json_path):
                with open(json_path, "r") as f:
                    json_data = json.load(f)
                    #TODO: try getting the user, user may have corrupted the file!

            for ef in edit_fields["tickets"]:
                if ef.text():
                    if ef.text() in json_data["log_history"]:
                        json_data["log_history"][ef.text()] += 1
                    else:
                        json_data["log_history"][ef.text()] = 1

            with open(json_path, 'w') as f:
                f.write(json.dumps(json_data))

            # Show check icon
            confirm_icons[row].setStyleSheet("""
                                  image: url("""+impath+"""check_icon.png);
                                  """)
        elif response.status_code == 400:
            edit_fields["time"][row].setStyleSheet("background-color: red;")
            confirm_icons[row].setStyleSheet("""
                    image: url("""+impath+"""fail.png);
                    """)
        elif response.status_code == 404:
            edit_fields["tickets"][row].setStyleSheet("background-color: red;")
            confirm_icons[row].setStyleSheet("""
                    image: url("""+impath+"""fail.png);
                    """)

    def comments(self):
        print("in comments")

    def tickets(self):
        self.showMainField("tickets")

    def getTickets(self):
        self.toggleTheme()
        self.jira_ticket_worker.loading_signal.connect(self.loading)
        self.jira_ticket_worker.data_signal.connect(self.setTicketData)
        self.jira_ticket_worker.start()

    def setTicketData(self, fields):
        main_field = self.view.getUI("Jira").getMainFields()["tickets"]
        edit_field = main_field.getEditFields()[0]
        # Check if assignee/project exists
        if fields[0] is None:
            edit_field.setStyleSheet("background-color: red;")
            return

        # Update completer string list
        json_path = os.path.dirname(os.path.abspath(__file__))+'/jira.user'
        if os.path.isfile(json_path):
            with open(json_path, "r") as f:
                json_data = json.load(f)
                json_data["assignee_history"].append(edit_field.text())

            with open(json_path, 'w') as f:
                f.write(json.dumps(json_data))

            main_field.updateCompleter()

        # Remove widgets from a layout
        main_field.clearLayout()

        grid = main_field.getTicketLayout()
        for k in range(len(fields)):
            field = fields[k]
            for i in range(len(field)):
                label = QtWidgets.QLabel(field[i])
                label.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
                label.setStyleSheet("color:rgba(201, 14, 14, 255);")
                grid.addWidget(label,i,k)
            grid.setHorizontalSpacing(50)

    def showMainField(self, name):
        main_fields = self.view.getUI("Jira").getMainFields()
        for key, field in main_fields.items():
            field.hide()

        main_fields[name].show()

    def loading(self, load):
        if load:
            self.loading_signals_count += 1
            self.view.getSidebar().getLoadingGif().show()
        else:
            self.loading_signals_count -= 1

        if self.loading_signals_count == 0:
            self.view.getSidebar().getLoadingGif().hide()


if __name__ == '__main__':
    test = TestClass()
