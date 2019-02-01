import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from topmenu import TopMenu
from mainfield import MainField

class JiraUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0 ,0 ,0)
        layout.setSpacing(0)
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.main_fields = {}
        self.radiobuttons = []
        self.edit_fields = []
        self.buttons = {}

        self.top_menu = TopMenu({
            "Tickets" : self.path+"tickets.png",
            "Graph" : self.path+"graph.png",
            "Log Work" : self.path+"log.png",
            "Comments" : self.path+"comments.png",
            })

        empty_field = MainField()
        empty_field.show()

        ticket_field = self.createTicketField()
        self.main_fields["ticket"] = ticket_field

        graph_field = self.createGraphField()
        graph_field.hide()
        self.main_fields["graph"] = graph_field

        layout.addWidget(self.top_menu)
        layout.addWidget(empty_field)
        layout.addWidget(ticket_field)
        layout.addWidget(graph_field)
        ticket_field.getLayout().setContentsMargins(0,0,0,0)

    def getTopMenu(self):
        return self.top_menu

    def getMainFields(self):
        return self.main_fields

    def getGraphParams(self):
        return self.edit_fields[1].text()

    def createGraphField(self):
        field = MainField()
        container = QtWidgets.QWidget()
        container.setFixedHeight(60)

        layout = QtWidgets.QHBoxLayout(container)

        # ID
        ef = self.createEditField("Epic")
        self.edit_fields.append(ef)

        # Go pushbutton
        b_go = QtWidgets.QPushButton()
        b_go.setStyleSheet("border: none;")
        b_go.setIcon(QtGui.QIcon(self.path+"go.png"))
        b_go.setIconSize(QtCore.QSize(40, 40))
        b_go.setCheckable(True)
        b_go.pressed.connect(lambda:self.pressed(b_go, self.path+"go.png"))
        b_go.released.connect(lambda:self.released(b_go, self.path+"go.png"))
        self.buttons["graphGo"] = b_go

        layout.addWidget(ef)
        layout.addWidget(b_go)
        layout.addStretch(20)

        # Temporarily set an empty widget for layout purposes #TODO: can this benicer?
        # empty_container = QtWidgets.QWidget()
        # empty_layout = QtWidgets.QVBoxLayout(container)
        # empty_layout.addStretch(200)

        # Add edit field and radiobuttons to edit layout
        field.getLayout().addWidget(container)
        field.getLayout().addStretch(20) # To move the rest to the top

        return field

    def createTicketField(self):
        field = MainField()
        container = QtWidgets.QWidget()
        container.setFixedHeight(60)

        layout = QtWidgets.QHBoxLayout(container)
        # field.hide()

        # # Edit layout
        # edit_layout_container = QtWidgets.QWidget(self)
        # edit_layout = QtWidgets.QVBoxLayout(edit_layout_container)

        # ID
        ef = self.createEditField("username or project id")

        # Radiobutton
        rb_user = QtWidgets.QRadioButton("User")
        rb_user.setChecked(True)
        rb_project = QtWidgets.QRadioButton("Project")
        self.radiobuttons.append(rb_user)
        self.radiobuttons.append(rb_project)

        # Go pushbutton
        b_go = QtWidgets.QPushButton()
        b_go.setStyleSheet("border: none;")
        b_go.setIcon(QtGui.QIcon(self.path+"go.png"))
        b_go.setIconSize(QtCore.QSize(40, 40))
        b_go.setCheckable(True)
        b_go.pressed.connect(lambda:self.pressed(b_go, self.path+"go.png"))
        b_go.released.connect(lambda:self.released(b_go, self.path+"go.png"))
        self.buttons["ticketGo"] = b_go

        layout.addWidget(ef)
        layout.addWidget(rb_user)
        layout.addWidget(rb_project)
        layout.addWidget(b_go)
        layout.addStretch(20)

        # Add edit field and radiobuttons to edit layout
        field.getLayout().addWidget(container)
        field.getLayout().addStretch(20) # To move the rest to the top

        return field

    def getButtons(self):
        return self.buttons

    def getTicketParam(self):
        if self.radiobuttons[0].isChecked():
            return self.edit_fields[0].text(), "assignee"
        else:
            return self.edit_fields[0].text(), "project"

    def createEditField(self, text):
        ef = QtWidgets.QLineEdit()
        ef.setPlaceholderText(text)
        ef.setFixedWidth(220)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.edit_fields.append(ef)
        return ef

    def setTheme(self, colors):
        for rb in self.radiobuttons:
            rb.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            rb.setStyleSheet("""
            QRadioButton{ color: """+colors["font"]+""";}

            QRadioButton::indicator {
                width:                  20px;
                height:                 20px;
            }

            QRadioButton::indicator:checked {
                image: url("""+self.path+"""radiobutton_checked.png);
            }

            QRadioButton::indicator:unchecked {

                image: url("""+self.path+"""radiobutton_unchecked.png);
            }
            """)

        for ef in self.edit_fields:
            ef.setStyleSheet("""
            color:"""+colors["font"]+""";
            border: 2px solid rgba(36, 70, 122, 200);
            background-color: """+colors["edit"]+""";
            """)

    def pressed(self, b, p):
        split = p.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self, b, p):
        b.setIcon(QtGui.QIcon(p))

    def tickets(self):
        key, target = self.getTicketParam()
        tickets, issue_types, summaries, progress = self.jira.tickets(key, target)
        fields = [tickets, issue_types, summaries, progress]

        lc = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(lc)
        grid.setAlignment(QtCore.Qt.AlignCenter)
        # grid.setContentsMargins(40,0,0,0)
        for k in range(len(fields)):
            field = fields[k]
            for i in range(len(field)):
                label = QtWidgets.QLabel(field[i])
                label.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
                label.setStyleSheet("color:rgba(201, 14, 14, 255);")
                grid.addWidget(label,i,k)
            grid.setHorizontalSpacing(50)
        scroll = QtWidgets.QScrollArea()

        scroll.setStyleSheet("""
                        QScrollBar:vertical {
                        border: none;
                        margin: 0px 0px 0px 0px;
                        }

                        QScrollBar::handle:vertical {
                        background: rgba(16, 50, 100, 200);
                        width: 15px;
                        }

                        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        border: none;
                        background: none;
                        }

                        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: none;
                        }
                        """)

        scroll.setWidgetResizable(True) # Will make it centered
        # scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


        self.main_fields["ticket"].getLayout().addWidget(scroll)
        scroll.setWidget(lc)

        QtWidgets.QScroller.grabGesture(
            scroll.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture
        )

        self.main_fields["ticket"].getLayout().setContentsMargins(0,0,0,0)
        # tickets, issue_types, summaries, progress = self.jira.tickets("johanneskazantzidis")
        # fields = [tickets, issue_types, summaries, progress]

        # lc = QtWidgets.QWidget()
        # grid = QtWidgets.QGridLayout(lc)
        # grid.setAlignment(QtCore.Qt.AlignCenter)
        # # grid.setContentsMargins(40,0,0,0)
        # for k in range(len(fields)):
        #     field = fields[k]
        #     for i in range(len(field)):
        #         label = QtWidgets.QLabel(field[i])
        #         label.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        #         label.setStyleSheet("color:rgba(201, 14, 14, 255);")
        #         grid.addWidget(label,i,k)
        #     grid.setHorizontalSpacing(50)
        # scroll = QtWidgets.QScrollArea()

        # scroll.setStyleSheet("""
        #                 QScrollBar:vertical {
        #                 border: none;
        #                 margin: 0px 0px 0px 0px;
        #                 }

        #                 QScrollBar::handle:vertical {
        #                 background: rgba(16, 50, 100, 200);
        #                 width: 15px;
        #                 }

        #                 QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        #                 border: none;
        #                 background: none;
        #                 }

        #                 QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        #                 background: none;
        #                 }
        #                 """)

        # scroll.setWidgetResizable(True) # Will make it centered
        # # scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # # scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


        # self.jira_ui.getMainFields()[0].getLayout().addWidget(scroll)
        # scroll.setWidget(lc)

        # QtWidgets.QScroller.grabGesture(
        #     scroll.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture
        # )

        # self.jira_ui.getMainFields()[0].getLayout().setContentsMargins(0,0,0,0)
