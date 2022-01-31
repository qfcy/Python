# Listing_20-4.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Temperature-conversion program with menus

import sys
from PyQt4 import QtCore, QtGui, uic

form_class = uic.loadUiType("tempconv_menu.ui")[0]     # Load the temperature conversion UI  

class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.btn_CtoF.clicked.connect(self.btn_CtoF_clicked)       # Bind the event handlers 
        self.btn_FtoC.clicked.connect(self.btn_FtoC_clicked)       #   to the buttons
        self.actionC_to_F.triggered.connect(self.btn_CtoF_clicked)  # Bind Convert menu item 
        self.actionF_to_C.triggered.connect(self.btn_FtoC_clicked)  #   event handlers
        self.actionExit.triggered.connect(self.menuExit_selected)  # Bind Exit menu item event handlers
        
    def btn_CtoF_clicked(self):                             # CtoF button event handler
        cel = float(self.editCel.text())                    #
        fahr = cel * 9 / 5.0 + 32                           #
        self.spinFahr.setValue(int(fahr + 0.5))             #
          
    def btn_FtoC_clicked(self):                             # FtoC button event handler
        fahr = self.spinFahr.value()                        #
        cel = (fahr - 32) * 5 / 9.0                         #
        self.editCel.setText(str(cel))                      #

    def menuExit_selected(self):               # Flie-Exit Menu event handler
        self.close()                           # 
        
app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_() 
