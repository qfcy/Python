# TIO_CH24_3.py
# Copyright Warren & Csrter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# Answer to Try It Out Question 3, Chapter 24

# Virtual Pet program with Pause button

import sys, pickle,datetime
from PyQt4 import QtCore, QtGui, uic

formclass, baseclass = uic.loadUiType("virtualpet_pause.ui")  # use the UI with the Pause button
                                                              #   and label added

class MyForm(baseclass, formclass):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # initialize values
        self.doctor = False                                            
        self.walking = False                                           
        self.sleeping = False                                          
        self.playing = False                                           
        self.eating = False
        self.paused = False        # Added this attribute for Paused
        self.time_cycle = 0                                            
        self.hunger = 0                                                
        self.happiness  = 8                                            
        self.health = 8                                                
        self.forceAwake = False

        # lists of images for animations
        self.sleepImages = ["sleep1.gif","sleep2.gif","sleep3.gif",   
                            "sleep4.gif"]                             
        self.eatImages = ["eat1.gif", "eat2.gif"]                     
        self.walkImages = ["walk1.gif", "walk2.gif", "walk3.gif",     
                           "walk4.gif"]                               
        self.playImages = ["play1.gif", "play2.gif"]                  
        self.doctorImages = ["doc1.gif", "doc2.gif"]                  
        self.nothingImages  = ["pet1.gif", "pet2.gif", "pet3.gif"]    
        
        self.imageList = self.nothingImages
        self.imageIndex = 0
        
        # connect event handlers to toolbar buttons
        self.actionStop.triggered.connect(self.stop_Click)             
        self.actionFeed.triggered.connect(self.feed_Click)             
        self.actionWalk.triggered.connect(self.walk_Click)             
        self.actionPlay.triggered.connect(self.play_Click)             
        self.actionDoctor.triggered.connect(self.doctor_Click)
        self.btnPause.clicked.connect(self.btnPause_Click)
        
        # set up timers
        self.myTimer1 = QtCore.QTimer(self)                     
        self.myTimer1.start(500)                                
        self.myTimer1.timeout.connect(self.animation_timer)     
                                                                
        self.myTimer2 = QtCore.QTimer(self)                     
        self.myTimer2.start(5000)                               
        self.myTimer2.timeout.connect(self.tick_timer)          
                                                  
        filehandle = True
        try:                                      # try to open pickle file  
            file = open("savedata_vp.pkl", "r")        
        except:                                        
            filehandle = False                         
        if filehandle:
            save_list = pickle.load(file)     # read from pickle file, if open
            file.close()
        else:                     # use default values if pickle file not open
            save_list = [8, 8, 0, datetime.datetime.now(), 0, False]   #added Pause state
                                                                       # to the default save list
        self.happiness = save_list[0]     
        self.health    = save_list[1]     
        self.hunger    = save_list[2]     
        timestamp_then = save_list[3]     
        self.time_cycle = save_list[4]
        self.paused = save_list[5]          # recall the "paused" state
        if self.paused:
            self.btnPause.setText("Resume")
            self.lblPaused.setText("Paused")
        else:
            self.btnPause.setText("Pause")
            self.lblPaused.setText("")
        self.progressBar_1.setProperty("value", (8-self.hunger)*(100/8.0)) 
        self.progressBar_2.setProperty("value", self.happiness*(100/8.0))  
        self.progressBar_3.setProperty("value", self.health*(100/8.0))

        if not self.paused:                 # check if paused
            # check how long since program was last run
            difference = datetime.datetime.now() - timestamp_then    
            ticks = difference.seconds / 50                          
            
            # simulate all ticks that happened during down time
            for i in range(0, ticks):
                self.time_cycle += 1                                    
                if self.time_cycle == 60:                               
                    self.time_cycle = 0                                 
                if self.time_cycle <= 48:       # awake       
                    self.sleeping = False                               
                    if self.hunger < 8:                                 
                        self.hunger += 1                                
                else:                           # sleeping              
                    self.sleeping = True                                
                    if self.hunger < 8 and self.time_cycle % 3 == 0:    
                        self.hunger += 1                                
                if self.hunger == 7 and (self.time_cycle % 2 ==0) and self.health > 0:                
                    self.health -= 1                                    
                if self.hunger == 8 and self.health > 0:                
                    self.health -=1                                     
        
        # use correct animation - awake or sleeping
        if self.sleeping:                                 
            self.imageList = self.sleepImages             
        else:                                             
            self.imageList = self.nothingImages           
    
    # check if pet is sleeping before doing an action
    def sleep_test(self):                                                
        if self.sleeping:                                                
            result = (QtGui.QMessageBox.warning(self, 'WARNING',         
"Are you sure you want to wake your pet up?  He'll be unhappy about it!",
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,        
                    QtGui.QMessageBox.No))                               
                                                                         
            if result == QtGui.QMessageBox.Yes:                          
                self.sleeping = False                                    
                self.happiness -= 4                                      
                self.forceAwake = True                                   
                return True                                              
            else:                                                        
                return False                                             
        else:                                                            
            return True                                                  

    # Doctor button event handler
    def doctor_Click(self):                                 
        if self.sleep_test():                               
            self.imageList = self.doctorImages              
            self.doctor = True                              
            self.walking = False                            
            self.eating = False                             
            self.playing = False                            

    # Feed button event handler    
    def feed_Click(self):                                   
        if self.sleep_test():                               
            self.imageList = self.eatImages                 
            self.eating = True                              
            self.walking = False                            
            self.playing = False                            
            self.doctor = False                             

    # Play button event handler          
    def play_Click(self):                                   
        if self.sleep_test():                               
            self.imageList = self.playImages                
            self.playing = True                             
            self.walking = False                            
            self.eating = False                             
            self.doctor = False                             

    # Walk button event handler            
    def walk_Click(self):                                   
        if self.sleep_test():                               
            self.imageList = self.walkImages                
            self.walking = True                             
            self.eating = False                             
            self.playing = False                            
            self.doctor = False                             

    # Stop button event handler                    
    def stop_Click(self):                                   
        if not self.sleeping:                               
            self.imageList = self.nothingImages             
            self.walking = False                            
            self.eating = False                             
            self.playing = False                            
            self.doctor = False

    def btnPause_Click(self, event):
        self.paused = not self.paused
        if self.paused:
            self.btnPause.setText("Resume")
            self.lblPaused.setText("Paused")
        else:
            self.btnPause.setText("Pause")
            self.lblPaused.setText("")

    # animation timer event handler        
    def animation_timer(self):
        if not self.paused:
            if self.sleeping and not self.forceAwake:                          
                self.imageList = self.sleepImages                              
            self.imageIndex += 1                                               
            if self.imageIndex >= len(self.imageList):                         
                self.imageIndex = 0                                            
            icon = QtGui.QIcon()                                               
            
            #update (animate) the pet's image
            current_image = self.imageList[self.imageIndex]                 
            icon.addPixmap(QtGui.QPixmap(current_image),                    
                           QtGui.QIcon.Disabled, QtGui.QIcon.Off)           
            self.petPic.setIcon(icon)
            self.progressBar_1.setProperty("value", (8-self.hunger)*(100/8.0)) 
            self.progressBar_2.setProperty("value", self.happiness*(100/8.0))  
            self.progressBar_3.setProperty("value", self.health*(100/8.0))

    # 5-second tick timer event handler    
    def tick_timer(self):                                                  
        if not self.paused:
            self.time_cycle += 1                                               
            
            # check if sleeping or awake
            if self.time_cycle == 60:                                          
                self.time_cycle = 0                                            
            if self.time_cycle <= 48 or self.forceAwake:                       
                self.sleeping = False                                          
            else:                                                              
                self.sleeping = True                                           
            if self.time_cycle == 0:                                           
                self.forceAwake = False                                        
            
            # add or subtract units depending on activity
            if self.doctor:                                          
                self.health += 1                                     
                self.hunger += 1                                     
            elif self.walking and (self.time_cycle % 2 == 0):        
                self.happiness += 1                                  
                self.health += 1                                     
                self.hunger += 1                                     
            elif self.playing:                                       
                self.happiness += 1                                  
                self.hunger += 1                                     
            elif self.eating:                                        
                self.hunger -= 2                                     
            elif self.sleeping:                                      
                if self.time_cycle % 3 == 0:                         
                    self.hunger += 1                                 
            else:                                                    
                self.hunger += 1                                     
                if self.time_cycle % 2 == 0:                         
                    self.happiness -= 1                              

            # make sure values are not out of range        
            if self.hunger > 8:  self.hunger = 8                               
            if self.hunger < 0:  self.hunger = 0                               
            if self.hunger == 7 and (self.time_cycle % 2 ==0) :                
                self.health -= 1                                               
            if self.hunger == 8:                                               
                self.health -=1                                                
            if self.health > 8:  self.health = 8                               
            if self.health < 0:  self.health = 0                               
            if self.happiness > 8:  self.happiness = 8                         
            if self.happiness < 0:  self.happiness = 0                         
            
            # update progress bars
            self.progressBar_1.setProperty("value", (8-self.hunger)*(100/8.0)) 
            self.progressBar_2.setProperty("value", self.happiness*(100/8.0))  
            self.progressBar_3.setProperty("value", self.health*(100/8.0))     

    def closeEvent(self, event):
        file = open("savedata_vp.pkl", "w")                     
        save_list = [self.happiness, self.health, self.hunger, datetime.datetime.now(),
                     self.time_cycle, self.paused]  #added the paused state to the pickled data

        pickle.dump(save_list, file)                            
        event.accept()
                
    def menuExit_selected(self):
        self.close()

app = QtGui.QApplication(sys.argv)
myapp = MyForm()
myapp.show()
app.exec_()       
