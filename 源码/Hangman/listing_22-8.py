# Listing_22-8.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Hangman game using PyQt

import sys
from PyQt4 import QtCore, QtGui, uic
import random

form_class = uic.loadUiType("hangman.ui")[0]

# Find the locations(s) of guessed letters in the secret word
def find_letters(letter, a_string):                                  
    locations = []                                                   
    start = 0                                                        
    while a_string.find(letter, start, len(a_string)) != -1:         
        location = a_string.find(letter, start, len(a_string))       
        locations.append(location)                                   
        start = location + 1                                         
    return locations                                                 

# Replace dashes with letters when the player guesses a letter correctly                                                                 
def replace_letters(string, locations, letter):
    new_string = ''                                                  
    for i in range (0, len(string)):                                 
        if i in locations:                                           
            new_string = new_string + letter                         
        else:                                                        
            new_string = new_string + string[i]                      
    return new_string                                                

# Replace letters with dashes at the start of the program
def dashes(word):                                                  
    letters = "abcdefghijklmnopqrstuvwxyz"                           
    new_string = ''                                                  
    for i in word:                                                   
        if i in letters:                                             
            new_string += "-"                                        
        else:                                                        
            new_string += i                                          
    return new_string                                                

class MyWidget(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.btn_guess.clicked.connect(self.btn_guess_clicked)           # Connect event handlers
        self.actionExit.triggered.connect(self.menuExit_selected)        #
        self.pieces = [self.head, self.body, self.leftarm, self.leftleg,    # Parts of the man 
                       self.rightarm, self.rightleg]                        #
        self.gallows = [self.line1, self.line2, self.line3, self.line4]  # Parts of the gallows
        self.pieces_shown = 0
        self.currentword = ""
        
        #Get the word list
        f=open("words.txt", 'r')  
        self.lines = f.readlines()
        f.close()                 
        self.new_game()           
   
    def new_game(self):
        self.guesses.setText("")
        self.currentword = random.choice(self.lines)     # Randomly pick a word from the list
        self.currentword = self.currentword.strip()
        for i in self.pieces:                                           # Hide the man
            i.setFrameShadow(QtGui.QFrame.Plain)                        #
            i.setHidden(True)                                           #
        for i in self.gallows:                                           
            i.setFrameShadow(QtGui.QFrame.Plain)                         
        self.word.setText(dashes(self.currentword))   # Call the function to replace letters with dashes
        self.pieces_shown = 0
    
    # Let the player guess a letter or word    
    def btn_guess_clicked(self):
        guess = str(self.guessBox.text())                                  
        if str(self.guesses.text()) != "":                                 
            self.guesses.setText(str(self.guesses.text())+", "+guess)      
        else:                                                              
            self.guesses.setText(guess)                                    
        if len(guess) == 1:                                              # Guess a letter
            if guess in self.currentword:                                #
                locations = find_letters(guess, self.currentword)        #
                self.word.setText(replace_letters(str(self.word.text()), #
                                                  locations,guess))      #
                if str(self.word.text()) == self.currentword:            #
                    self.win()                                           #
            else:                                                          
                self.wrong()                                               
        else:                                                            # Guess a word
            if guess == self.currentword:                                #
                self.win()                                               #
            else:                                                        #
                self.wrong()                                             #
        self.guessBox.setText("")                                          

    def win(self):                                                #Display a dialog if player wins
        QtGui.QMessageBox.information(self,"Hangman","You win!")  #
        self.new_game()                                           #
    
        # handle a wrong guess
    def wrong(self):
        self.pieces_shown += 1                                            
        for i in range(self.pieces_shown):                              # Reveal another piece of the man
            self.pieces[i].setHidden(False)                             #
        if self.pieces_shown == len(self.pieces):                         
            message = "You lose.  The word was " + self.currentword     # Player lost
            QtGui.QMessageBox.warning(self,"Hangman", message)          #
            self.new_game()
    
    def menuExit_selected(self):
        self.close()

app = QtGui.QApplication(sys.argv)
myapp = MyWidget(None)
myapp.show()
app.exec_()

