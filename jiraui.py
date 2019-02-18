import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from topmenu import TopMenu
from mainfield import MainField, TicketField, GraphField, LogField

class JiraUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0 ,0 ,0)
        layout.setSpacing(0)
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.main_fields = {}

        self.top_menu = TopMenu({
            "Tickets" : self.path+"tickets.png",
            "Graph" : self.path+"graph.png",
            "Log" : self.path+"log.png",
            "Comments" : self.path+"comments.png",
            })

        empty_field = MainField()
        empty_field.show()

        self.main_fields["tickets"] = TicketField()
        self.main_fields["graph"] = GraphField(self.frameSize())
        self.main_fields["log"] = LogField(self.frameSize())

        layout.addWidget(self.top_menu)
        layout.addWidget(empty_field)
        layout.addWidget(self.main_fields["tickets"])
        layout.addWidget(self.main_fields["graph"])
        layout.addWidget(self.main_fields["log"])

    def getTopMenu(self):
        return self.top_menu

    def getMainFields(self):
        return self.main_fields

    # def getButtons(self):
    #     return self.TopMenu

    def setTheme(self, colors):
        self.main_fields["tickets"].setTheme(colors)
        self.main_fields["graph"].setTheme(colors)
        self.main_fields["log"].setTheme(colors)
        self.top_menu.setTheme(colors)

    def getTicketParam(self):
        radiobuttons = self.main_fields["tickets"].getRadiobuttons()
        edit_fields = self.main_fields["tickets"].getEditFields()
        if radiobuttons[0].isChecked():
            return edit_fields[0].text(), "assignee"
        else:
            return edit_fields[0].text(), "project"

    def getGraphParams(self):
        return self.main_fields["graph"].getEditFields()[0].text()
