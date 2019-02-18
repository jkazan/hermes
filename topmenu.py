import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class TopMenu(QtWidgets.QWidget):
    def __init__(self, spec):
        super().__init__()
        self.spec = spec
        self.__buttons = []
        self.__labels = []
        self.initUI()
        self.setFixedHeight(95)

    def initUI(self):
        menu_layout = QtWidgets.QHBoxLayout(self)
        menu_layout.setContentsMargins(0,0,0,0)
        menu_layout.setSpacing(0)

        for label, icon_path in self.spec.items():
            vbc = QtWidgets.QWidget()
            vb = QtWidgets.QVBoxLayout(vbc)
            vb.setContentsMargins(0,5,0,5)
            vb.setSpacing(0)
            b = self.createButton(icon_path, label)
            l = QtWidgets.QLabel(label)
            l.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
            l.setAlignment(QtCore.Qt.AlignCenter)
            self.__labels.append(l)

            vb.addWidget(b)
            vb.addWidget(l)
            menu_layout.addWidget(vbc)

    def createButton(self, icon_path, name):
        b = QtWidgets.QPushButton(objectName=name)
        b.setStyleSheet("border: none;")
        b.setIcon(QtGui.QIcon(icon_path))
        b.setIconSize(QtCore.QSize(64, 64))
        b.setCheckable(True)
        b.pressed.connect(lambda:self.pressed(b, icon_path))
        b.released.connect(lambda:self.released(b, icon_path))
        self.__buttons.append(b)

        return b

    def getButtons(self):
        return self.__buttons

    def setTheme(self, colors):
        self.setStyleSheet("background-color:"+colors["top"]+";")

        for l in self.__labels:
            l.setStyleSheet("color:"+colors["font"]+";")

    def pressed(self, b, p):
        split = p.split(".")
        pressed_icon_path = split[0] + "_pressed." + split[1]
        b.setIcon(QtGui.QIcon(pressed_icon_path))

    def released(self, b, p):
        b.setIcon(QtGui.QIcon(p))


