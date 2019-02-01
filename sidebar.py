import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class Sidebar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground) # Otherwise can't style
        self.__path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.movie = QtGui.QMovie(self.__path + "loading.gif")
        self.__buttons = []
        self.__labels = []
        self.initUI()

    def initUI(self):
        self.setFixedWidth(85)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,5,0,0)
        layout.setSpacing(40)
        bl = ["Jira", "Install", "Settings"]

        for label in bl:
            b = self.createButton(label, self.__path + label.lower()+".png")
            layout.addWidget(b)
        layout.addStretch(20) # Push buttons up

        # Add loading gif
        self.movie.setScaledSize(QtCore.QSize(40, 40))
        l_loading = QtWidgets.QLabel() # widget for holding movie
        l_loading.setFixedHeight(40)
        l_loading.setAlignment(QtCore.Qt.AlignCenter)
        l_loading.setMovie(self.movie)
        layout.addWidget(l_loading) #TODO: cleanup

    def createButton(self, label, icon_path):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        b = QtWidgets.QPushButton()
        b.setStyleSheet("border: none;")
        b.setIcon(QtGui.QIcon(icon_path))
        b.setIconSize(QtCore.QSize(64, 64))
        b.setCheckable(True)
        self.__buttons.append(b)

        l = QtWidgets.QLabel(label)
        l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        l.setAlignment(QtCore.Qt.AlignCenter)
        self.__labels.append(l)
        layout.addWidget(b)
        layout.addWidget(l)
        layout.addStretch(1)

        return container

    def getButtons(self):
        return self.__buttons

    def setFontColor(self, color):
        for l in self.__labels:
            l.setStyleSheet("color:"+color+";")

    def getLoadingGif(self):
        return self.movie
