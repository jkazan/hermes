import os
from functools import partial
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from view import View
from dialog import Login
from jira import HJira
from photoviewer import PhotoViewer

class Controller(QtCore.QObject):
    loading_signal = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        app = QtWidgets.QApplication([])
        self.view = View()
        self.view.show()
        self.jira_ui = self.view.getUI("Jira")
        self.install_ui = self.view.getUI("Install")
        self.settings_ui = self.view.getUI("Settings")
        self.boot_ui = self.view.getUI("Boot")
        self.side_buttons = self.view.getSidebarButtons()
        self.jira = HJira()
        self.calc = External(self.view.getSidebar().getLoadingGif(), self.loading_signal)
        self.calc.start()

        #TODO: Implement below and exchange self.uis
        # self.uis = {
        #     "Jira" : self.jira_ui,
        #     "Install" : self.install_ui,
        #     "Settings" : self.settings_ui,
        #                 }
        self.uis = [self.jira_ui, self.install_ui, self.settings_ui, self.boot_ui]



        self.uiControl()

        app.exec_()

    def uiControl(self):
        path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        paths = [path+"jira.png", path+"install.png", path+"settings.png"]
        uis = [self.jira_ui, self.install_ui, self.settings_ui]
        self.setSidebarConnections(self.side_buttons, paths, uis)

        b_jira = self.side_buttons[0]
        b_jira.clicked.connect(self.login)
        self.connectJiraTop()

        setting_theme = self.settings_ui.getTheme()
        setting_theme.toggled.connect(lambda:self.toggleTheme(setting_theme))

    def setSidebarConnections(self, b, p, ui):
        for i in range(len(b)):
            b[i].pressed.connect(partial(self.pressed, b[i], p[i]))
            b[i].released.connect(partial(self.released, b[i], p[i]))
            b[i].clicked.connect(partial(self.showUI, ui[i]))

    def login(self):
        if not self.jira.loggedin:
            b_login = QtWidgets.QPushButton()
            login_dialog = Login(self.jira, self.jira_ui, self.uis)

    def pressed(self, b, p):
        split = p.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self, b, p):
        b.setIcon(QtGui.QIcon(p))

        #TODO: move this to clicked_
        # layout = self.view.getJiraUI().getMainField().getLayout()
        # items = (layout.itemAt(i) for i in range(layout.count()))
        # for w in items:
        #     # w.hide()
        #     print(w) #TODO: this is never called

    def showUI(self, ui):
        if ui == self.jira_ui:
                if not self.jira.loggedin:
                    return

        for i in self.uis:
            if i != ui:
                i.hide()

        ui.show()

    def toggleTheme(self, light):
        if light.isChecked():
            self.view.setTheme("light")
        else:
            self.view.setTheme("dark")

    def connectJiraTop(self):
        buttons = self.jira_ui.getTopMenu().getButtons()
        for b in buttons:
            if b.objectName() == "Tickets":
                b.clicked.connect(self.tickets)
            elif b.objectName() == "Graph":
                b.clicked.connect(self.graph)

    def showMainField(self, main_fields, name):
        for key, field in main_fields.items():
            field.hide()
        main_fields[name].show()


    def graph(self):
        self.showMainField(self.jira_ui.getMainFields(), "graph")
        b_go = self.jira_ui.getButtons()["graphGo"]
        b_go.clicked.connect(self.getGraph)

    def getGraph(self):
        # args = "hej"
        # self.calc = External(self.view.getSidebar().getLoadingGif(), self.loading_signal)
        # self.calc.signal.connect(self.loading)
        self.loading_signal.emit(True)


        main_field = self.jira_ui.getMainFields()["graph"]
        ticket = self.jira_ui.getGraphParams()
        graph_path = self.jira.graph(ticket)

        # Remove widgets from a layout
        self.clearLayout(main_field.getLayout())

        widget = QtWidgets.QWidget()
        viewer = PhotoViewer(widget, self.jira_ui.frameSize())
        viewer.setPhoto(QtGui.QPixmap(graph_path))
        VBlayout = QtWidgets.QVBoxLayout(widget)
        VBlayout.addWidget(viewer)

        main_field.getLayout().addWidget(widget)
        self.loading_signal.emit(False)

    def loading(self):
        print("loading")

    def clearLayout(self, layout):
        for i in reversed(range(1,layout.count())):
            widgetToRemove = layout.takeAt(i).widget() #
            layout.removeWidget(widgetToRemove) # remove it from the layout list
            if widgetToRemove is not None:
                widgetToRemove.setParent(None) # remove it from the gui

    def tickets(self):
        self.showMainField(self.jira_ui.getMainFields(), "ticket")

        b_go = self.jira_ui.getButtons()["ticketGo"]
        b_go.clicked.connect(self.getTickets)

    def getTickets(self):
        main_field = self.jira_ui.getMainFields()["ticket"]
        key, target = self.jira_ui.getTicketParam()
        tickets, issue_types, summaries, progress = self.jira.tickets(key, target)
        fields = [tickets, issue_types, summaries, progress]

        # Remove widgets from a layout
        self.clearLayout(main_field.getLayout())

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

        
        main_field.getLayout().addWidget(scroll)
        scroll.setWidget(lc)

        QtWidgets.QScroller.grabGesture(
            scroll.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture
        )

        # main_field.getLayout().setContentsMargins(0,0,0,0)


class External(QtCore.QThread):
    """
    Runs a external thread.
    """
    # signal = QtCore.pyqtSignal(bool)

    def __init__(self, gif, signal, parent=None):
        super(External, self).__init__(parent)
        self.gif = gif
        self.signal = signal
        self.signal.connect(self.loading)

    def loading(self, loading):
        if loading:
            self.gif.start()
        else:
            self.gif.stop()

    def run(self):
        print("run new thread")



if __name__ == '__main__':
    controller = Controller()

    # Remove widgets from a layout
    # for i in reversed(range(layout.count())):
    # widgetToRemove = layout.takeAt(i).widget()
    # # remove it from the layout list
    # layout.removeWidget(widgetToRemove)
    # # remove it from the gui
    # widgetToRemove.setParent(None)
