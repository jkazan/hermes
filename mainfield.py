from PyQt5 import QtWidgets
from PyQt5 import QtCore

class MainField(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_StyledBackground) # Otherwise can't style
        self.layout = QtWidgets.QVBoxLayout(self)
        self.initUI()
        self.hide()

    def initUI(self):
        pass

    def getLayout(self):
        return self.layout
