import os
import json
import requests
import operator
from PyQt5 import QtWidgets
from PyQt5 import QtCore

class TicketWorker(QtCore.QThread):
    loading_signal = QtCore.pyqtSignal(bool)
    data_signal = QtCore.pyqtSignal(list)

    def __init__(self, jiraui, jira, parent=None):
        super(TicketWorker, self).__init__(parent)
        self.jiraui = jiraui
        self.jira = jira

    def run(self):
        self.loading_signal.emit(True)

        main_field = self.jiraui.getMainFields()["tickets"]
        key, target = self.jiraui.getTicketParam()

        try:
            tickets, issue_types, summaries, progress = self.jira.tickets(key, target)
        except (TypeError, AttributeError):
            self.data_signal.emit([None])
            self.loading_signal.emit(False)
            return

        fields = [tickets, issue_types, summaries, progress]

        self.data_signal.emit(fields)
        self.loading_signal.emit(False)


class GraphWorker(QtCore.QThread):
    loading_signal = QtCore.pyqtSignal(bool)
    data_signal = QtCore.pyqtSignal(str)

    def __init__(self, jiraui, jira, parent=None):
        super(GraphWorker, self).__init__(parent)
        self.jiraui = jiraui
        self.jira = jira

    def run(self):
        self.loading_signal.emit(True)

        main_field = self.jiraui.getMainFields()["graph"]
        viewer = main_field.getGraphViewer()
        ticket = self.jiraui.getGraphParams()
        graph_path = self.jira.graph(ticket)
        self.data_signal.emit(str(graph_path))
        self.loading_signal.emit(False)


class LogWorker(QtCore.QThread):
    loading_signal = QtCore.pyqtSignal(bool)
    data_signal = QtCore.pyqtSignal(requests.models.Response, int)

    def __init__(self, jiraui, jira, parent=None):
        super(LogWorker, self).__init__(parent)
        self.jiraui = jiraui
        self.jira = jira
        self.__path = os.path.dirname(os.path.abspath(__file__))+"/jira.user"

    def run(self):
        self.loading_signal.emit(True)

        main_field = self.jiraui.getMainFields()["log"]
        edit_fields = main_field.getEditFields()

        log_commands = []
        for i in range(len(edit_fields["tickets"])):
            if edit_fields["tickets"][i].text():
                response = self.jira.log(
                    edit_fields["tickets"][i].text(),
                    edit_fields["time"][i].text(),
                    edit_fields["comments"][i].text()
                    )
                self.data_signal.emit(response, i)

        # sorted_tickets = sorted(json_data["ticket_history"].items(),
        #                             key=operator.itemgetter(1), reverse=True)


        self.loading_signal.emit(False)
