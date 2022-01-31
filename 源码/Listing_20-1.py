# Listing_20-1.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Minimum code for a PyQt program

import sys
from PyQt4 import QtCore, QtGui, uic     # Import the Qt libraries we need

form_class = uic.loadUiType("MyFirstGui.ui")[0]   # Load the UI we created in Designer

# Class definition for the main window
class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
app = QtGui.QApplication(sys.argv)   # PtQt program to show our window
myWindow = MyWindowClass()           # Make an instance of the window class
myWindow.show()                         # Start the program and 
app.exec_()                             #   display the GUI window
