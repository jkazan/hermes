import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from topmenu import TopMenu
from mainfield import MainField

class SettingsUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0 ,0 ,0)
        layout.setSpacing(0)
        self.path = os.path.dirname(os.path.abspath(__file__))+'/imgs/'
        self.main_fields = {}

        self.top_menu = TopMenu({
            "First" : self.path+"tickets.png",
            "Second" : self.path+"graph.png",
            "Third" : self.path+"comments.png",
            })

        main_field = MainField()
        main_field.show()
        self.main_fields["temp"] = main_field

        layout.addWidget(self.top_menu)
        layout.addStretch(1)
        layout.addWidget(main_field)
        layout.addStretch(10)

        main_layout = main_field.getLayout()
        self.rb = QtWidgets.QRadioButton("Light Theme")
        self.rb.setFont(QtGui.QFont("Monospace", 10, QtGui.QFont.Bold))
        main_layout.addWidget(self.rb)


    def getTopMenu(self):
        return self.top_menu

    def getMainFields(self):
        return self.main_fields

    def getTheme(self):
        return self.rb

    def setTheme(self, colors):
        self.rb.setStyleSheet("""
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
