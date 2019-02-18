import os
import json
import operator
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from photoviewer import PhotoViewer

class MainField(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.__path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.setAttribute(QtCore.Qt.WA_StyledBackground) # Otherwise can't style
        self.__layout = QtWidgets.QVBoxLayout(self)
        self.hide()

    def getLayout(self):
        return self.__layout

    def setMainTheme(self, colors):
        self.setStyleSheet("background-color:"+colors["main"]+";")

    def setRadiobuttonTheme(self, rb_list, colors):
        for rb in rb_list:
            rb.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            rb.setStyleSheet("""
            QRadioButton{ color: """+colors["font"]+""";}

            QRadioButton::indicator {
                width:                  20px;
                height:                 20px;
            }

            QRadioButton::indicator:checked {
                image: url("""+self.__path+"""radiobutton_checked.png);
            }

            QRadioButton::indicator:unchecked {

                image: url("""+self.__path+"""radiobutton_unchecked.png);
            }
            """)

    def setEditFieldTheme(self, ef_list, colors):
        for ef in ef_list:
            ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            ef.setStyleSheet("""
            color:"""+colors["font"]+""";
            border: 2px solid rgba(36, 70, 122, 200);
            background-color: """+colors["edit"]+""";
            """)

    def setLabelTheme(self, label_list, colors):
        for label in label_list:
            label.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            label.setStyleSheet("color:"+colors["font"]+";")

    def setScrollTheme(self, scroll):
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

                        QScrollBar:horizontal {
                        border: none;
                        margin: 0px 0px 0px 0px;
                        }

                        QScrollBar::handle:horizontal {
                        background: rgba(16, 50, 100, 200);
                        width: 15px;
                        }

                        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                        border: none;
                        background: none;
                        }

                        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                        background: none;
                        }
                        """)

    def setCompleterTheme(self, completers, colors):
        for c in completers:
            c.popup().setStyleSheet("""
            color:"""+colors["font"]+""";
            border: 2px solid rgba(36, 70, 122, 200);
            background-color: """+colors["completer"]+""";
            """)
            c.popup().setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))

    def pressed(self, b, p):
        split = p.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self, b, p):
        b.setIcon(QtGui.QIcon(p))


class TicketField(MainField):
    def __init__(self):
        super().__init__()
        self.__path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.__edit_fields = []
        self.__radiobuttons = []
        self.__completers = []
        self.__scroll_area = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        container.setFixedHeight(60)

        top_layout = QtWidgets.QHBoxLayout(container)
        top_layout.setContentsMargins(0,0,0,0)

        # Radiobutton
        rb_user = QtWidgets.QRadioButton("User")
        rb_user.setChecked(True)
        rb_project = QtWidgets.QRadioButton("Project")
        self.__radiobuttons.append(rb_user)
        self.__radiobuttons.append(rb_project)

        # ID
        ef = QtWidgets.QLineEdit()
        ef.setPlaceholderText("username or project id")
        completer = QtWidgets.QCompleter()
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        ef.setFixedWidth(220)
        ef.setCompleter(completer)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        self.__edit_fields.append(ef)
        self.__completers.append(completer)
        self.updateCompleter()

        # Go pushbutton
        self.b_go = QtWidgets.QPushButton()
        self.b_go.setStyleSheet("border: none;")
        self.b_go.setIcon(QtGui.QIcon(self.__path+"go.png"))
        self.b_go.setIconSize(QtCore.QSize(40, 40))
        self.b_go.setCheckable(True)
        self.b_go.pressed.connect(lambda:self.pressed(self.b_go, self.__path+"go.png"))
        self.b_go.released.connect(lambda:self.released(self.b_go, self.__path+"go.png"))

        top_layout.addWidget(ef)
        top_layout.addWidget(rb_user)
        top_layout.addWidget(rb_project)
        top_layout.addWidget(self.b_go)
        top_layout.addStretch(20)

        # Grid layout for ticket info
        ticket_container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(ticket_container)
        self.grid.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.setContentsMargins(0,0,0,0)

        self.__scroll_area.setWidgetResizable(True) # Will make it centered
        self.__scroll_area.setWidget(ticket_container)

        QtWidgets.QScroller.grabGesture(
            self.__scroll_area.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture
        )

        # Add all widgets
        self.getLayout().addWidget(container)
        self.getLayout().addWidget(self.__scroll_area)

    def updateCompleter(self):
        json_path = os.path.dirname(os.path.abspath(__file__))+'/jira.user'
        with open(json_path, "r") as f:
            json_data = json.load(f)
        sorted_tickets = sorted(json_data["assignee_history"], reverse=True)

        string_list = QtCore.QStringListModel(sorted_tickets)
        self.__completers[0].setModel(string_list)


    def getTicketParam(self):
        if self.__radiobuttons[0].isChecked():
            return self.__edit_fields[0].text(), "assignee"
        else:
            return self.__edit_fields[0].text(), "project"

    def setTheme(self, colors):
        self.setMainTheme(colors)
        self.setRadiobuttonTheme(self.__radiobuttons, colors)
        self.setEditFieldTheme(self.__edit_fields, colors)
        self.setScrollTheme(self.__scroll_area)
        self.setCompleterTheme(self.__completers, colors)

    def getButton(self):
        return self.b_go

    def getRadiobuttons(self):
        return self.__radiobuttons

    def getEditFields(self):
        return self.__edit_fields

    def clearLayout(self):
        for i in reversed(range(1, self.grid.count())):
            widgetToRemove = self.grid.takeAt(i).widget() #
            self.grid.removeWidget(widgetToRemove) # remove it from the layout list
            if widgetToRemove is not None:
                widgetToRemove.setParent(None) # remove it from the gui

    def getTicketLayout(self):
        return self.grid


class GraphField(MainField):
    def __init__(self, frame_size):
        super().__init__()
        self.__path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.__edit_fields = []
        self.__completers = []
        self.frame_size = frame_size

        top_container = QtWidgets.QWidget()
        top_container.setFixedHeight(60)

        top_layout = QtWidgets.QHBoxLayout(top_container)
        top_layout.setContentsMargins(0,0,0,0)

        # ID
        json_path = os.path.dirname(os.path.abspath(__file__))+'/jira.user'
        with open(json_path, "r") as f:
            json_data = json.load(f)
        sorted_tickets = sorted(json_data["graph_history"], reverse=True)

        ef = QtWidgets.QLineEdit()
        ef.setPlaceholderText("Epic ID")
        completer = QtWidgets.QCompleter(sorted_tickets)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        ef.setFixedWidth(220)
        ef.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        ef.setCompleter(completer)
        self.__edit_fields.append(ef)
        self.__completers.append(completer)

        # Go pushbutton
        self.b_go = QtWidgets.QPushButton()
        self.b_go.setStyleSheet("border: none;")
        self.b_go.setIcon(QtGui.QIcon(self.__path+"go.png"))
        self.b_go.setIconSize(QtCore.QSize(40, 40))
        self.b_go.setCheckable(True)
        self.b_go.pressed.connect(lambda:self.pressed(self.b_go, self.__path+"go.png"))
        self.b_go.released.connect(lambda:self.released(self.b_go, self.__path+"go.png"))

        top_layout.addWidget(ef)
        top_layout.addWidget(self.b_go)
        top_layout.addStretch(20)

        # Graph viewer widget
        viewer_widget = QtWidgets.QWidget()
        self.viewer = PhotoViewer(viewer_widget, self.frame_size)
        VBlayout = QtWidgets.QVBoxLayout(viewer_widget)
        VBlayout.setContentsMargins(0,0,0,0)
        # VBlayout.setSpacing(0)
        VBlayout.addWidget(self.viewer)

        # Add all widgets
        self.getLayout().addWidget(top_container)
        self.getLayout().addWidget(viewer_widget)

    def setTheme(self, colors):
        self.setMainTheme(colors)
        self.setEditFieldTheme(self.__edit_fields, colors)
        scene = QtWidgets.QGraphicsScene()
        scene.setForegroundBrush(QtGui.QColor(255, 0, 0, 127))
        self.viewer.setBackgroundBrush(QtGui.QColor(*colors["graph"]))
        self.setCompleterTheme(self.__completers, colors)
        # self.viewer.setBackgroundBrush(QtGui.QBrush(colors["graph"], QtCore.Qt.SolidPattern))

    def getGraphViewer(self):
        return self.viewer

    def getButton(self):
        return self.b_go

    def getEditFields(self):
        return self.__edit_fields


class LogField(MainField):
    def __init__(self, frame_size):
        super().__init__()
        self.__path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.__ticket_edit_fields = []
        self.__time_edit_fields = []
        self.__comment_edit_fields = []
        self.__labels = []
        self.__completers = []
        self.__confirm_icons = []
        self.__scroll_area = QtWidgets.QScrollArea()

        # Grid layout for edit fields
        log_container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(log_container)
        self.grid.setAlignment(QtCore.Qt.AlignCenter)
        # self.grid.setContentsMargins(20,0,0,50)

        self.__scroll_area.setWidgetResizable(True) # Will make it centered
        self.__scroll_area.setWidget(log_container)

        QtWidgets.QScroller.grabGesture(
            self.__scroll_area.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture
        )

        # Add labels
        headers = ["Ticket ID", "Time worked", "Comment"]
        for i in range(len(headers)):
            label = QtWidgets.QLabel(headers[i])
            label.setStyleSheet("color:white;")
            self.grid.addWidget(label,0,i)
            self.__labels.append(label)

        # Not combining these loops with above because tab order gets messed up
        placeholders = ["ICSHWI-750", "1d 14h 23m", "This is a comment"]
        json_path = os.path.dirname(os.path.abspath(__file__))+'/jira.user'
        with open(json_path, "r") as f:
            json_data = json.load(f)
            #TODO: try getting the user, user may have corrupted the file!
        sorted_tickets_stats = sorted(json_data["log_history"].items(),
                                    key=operator.itemgetter(1), reverse=True)
        sorted_tickets = [x[0] for x in sorted_tickets_stats]

        # Add edit fields
        for i in range(10):
            for k in range(len(headers)+1):
                ef = QtWidgets.QLineEdit()

                if i == 0 and k < len(headers):
                    ef.setPlaceholderText(placeholders[k])

                if k%4 == 0:
                    completer = QtWidgets.QCompleter(sorted_tickets)
                    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
                    ef.setFixedWidth(130)
                    ef.setCompleter(completer)
                    self.__ticket_edit_fields.append(ef)
                    self.__completers.append(completer)
                elif k%4 == 1:
                    ef.setFixedWidth(170)
                    self.__time_edit_fields.append(ef)
                elif k%4 == 2:
                    ef.setFixedWidth(500)
                    self.__comment_edit_fields.append(ef)
                else:
                    confirm_icon = QtWidgets.QLabel()
                    confirm_icon.setFixedWidth(20)
                    self.__confirm_icons.append(confirm_icon)
                    self.grid.addWidget(confirm_icon,i+1,k)
                    continue

                self.grid.addWidget(ef,i+1,k)

        # Clear form pushbutton
        self.b_clear = QtWidgets.QPushButton()
        self.b_clear.setStyleSheet("border: none;")
        self.b_clear.setIcon(QtGui.QIcon(self.__path+"clear.png"))
        self.b_clear.setIconSize(QtCore.QSize(90, 30))
        # self.b_clear.setCheckable(True)
        self.b_clear.pressed.connect(lambda:self.pressed(self.b_clear, self.__path+"clear.png"))
        self.b_clear.released.connect(lambda:self.released(self.b_clear, self.__path+"clear.png"))

        # Layout for clear button
        clear_container = QtWidgets.QWidget()
        clear_layout = QtWidgets.QHBoxLayout(clear_container)
        clear_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.grid.setContentsMargins(0,0,0,0)
        clear_layout.addWidget(self.b_clear)

        self.grid.addWidget(clear_container,11,0)

        # Send pushbutton
        self.b_send = QtWidgets.QPushButton()
        self.b_send.setStyleSheet("border: none;")
        self.b_send.setIcon(QtGui.QIcon(self.__path+"send.png"))
        self.b_send.setIconSize(QtCore.QSize(40, 40))
        self.b_send.setCheckable(True)
        self.b_send.pressed.connect(lambda:self.pressed(self.b_send, self.__path+"send.png"))
        self.b_send.released.connect(lambda:self.released(self.b_send, self.__path+"send.png"))

        # Add all widgets
        self.getLayout().addWidget(self.__scroll_area)
        self.getLayout().addWidget(self.b_send)

    def setTheme(self, colors):
        self.setMainTheme(colors)
        self.setEditFieldTheme(self.__ticket_edit_fields, colors)
        self.setEditFieldTheme(self.__time_edit_fields, colors)
        self.setEditFieldTheme(self.__comment_edit_fields, colors)
        self.setLabelTheme(self.__labels, colors)
        self.setScrollTheme(self.__scroll_area)
        self.setCompleterTheme(self.__completers, colors)

    def getSendButton(self):
        return self.b_send

    def getClearButton(self):
        return self.b_clear

    def getEditFields(self):
        return {
            "tickets" : self.__ticket_edit_fields,
            "time" : self.__time_edit_fields,
            "comments" : self.__comment_edit_fields
            }

    def getEditFieldGrid(self):
        return self.grid

    def getConfirmIcons(self):
        return self.__confirm_icons
