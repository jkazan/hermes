import os
from PyQt5 import QtWidgets
from topmenu import TopMenu
from mainfield import MainField

class InstallUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0 ,0 ,0)
        layout.setSpacing(0)
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.main_fields = {}

        self.top_menu = TopMenu({
            "E3" : self.path+"e3.png",
            "CSS" : self.path+"css.png",
            "PLCFactory" : self.path+"install.png",
            "BEAST" : self.path+"install.png",
            })

        main_field = MainField()
        self.main_fields["e3"] = main_field


        layout.addWidget(self.top_menu)
        layout.addStretch(1)
        layout.addWidget(main_field)
        layout.addStretch(10)

    def getTopMenu(self):
        return self.top_menu

    def getMainFields(self):
        return self.main_fields

    def setTheme(self, colors):
        pass
