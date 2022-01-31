# pythonbattle.py
# Copyright Warren & Carter Sande, 2013
# Released under MIT license   http://www.opensource.org/licenses/mit-license.php
# Version $version  ----------------------------

# This is the PythonBattle program that runs the AI's against each other.
# It generates the play grid using Pygame and runs the battle.

import pygame #ASCII/PYGAME
import time
pygame.init() #ASCII/PYGAME

class OutOfTurnError(Exception):
    """ A custom exception describing a state in which a robot moves out of turn"""
    def __init__(self,botname):
        self.botname = botname
    def __str__(self):
        return "Robot "+self.botname+" tried to call function when it wasn't his turn"

class RobotIsDefeatedError(Exception):
    """ A custom exception describing a state in which a robot moves while it
is defeated."""
    def __init__(self,botname):
        self.botname = botname
    def __str__(self):
        return "Robot "+self.botname+" tried to call function while defeated"


class Robot:
    """A player in the battle. 
    Rotation values:
    0: Up
    1: Right
    2: Down
    3: Left

    Note: All methods starting with _ are PRIVATE. Do not
    call them under any circumstances.  """
    def __init__(self,name,ai,position,rotation):
        self.name = name
        self.ai = ai
        ai.robot = self
        self.position = position
        self.rotation = rotation
        self.health = 100
    def _spaceInFront(self):
        if self.rotation == 0:
            return (self.position[0],self.position[1]-1)
        elif self.rotation == 1:
            return (self.position[0]+1,self.position[1])
        elif self.rotation == 2:
            return (self.position[0],self.position[1]+1)
        elif self.rotation == 3:
            return (self.position[0]-1,self.position[1])
    def _getSpace(self,space):
        global field
        if space == self.position:
            return "me"
        else:
            for i in field:
                if i.position == space:
                    return "bot"
        if space[0]<1:
            return "wall"
        elif space[1]<1:
            return "wall"
        elif space[0]>10:
            return "wall"
        elif space[1]>10:
            return "wall"
        else:
            return "clear"
    def _goForth(self):
        if self._getSpace(self._spaceInFront()) == "clear":
            self.position = self._spaceInFront()
            return "success"
        else:
            return self._getSpace(self._spaceInFront())
    def _goBack(self):
        self._turnLeft()
        self._turnLeft()
        if self._getSpace(self._spaceInFront()) == "clear":
            self.position = self._spaceInFront()
            self._turnRight()
            self._turnRight()
            return "success"
        else:
            result = self._getSpace(self._spaceInFront())
            self._turnRight()
            self._turnRight()
            return result
    def _turnLeft(self):
        self.rotation -= 1
        self.rotation %= 4
        return "success"
    def _turnRight(self):
        self.rotation += 1
        self.rotation %= 4
        return "success"
    def _attack(self):
        global field
        for i in field:
            if i.position == self._spaceInFront():
                i.takeDamage(10)
                return "success"
        return self._getSpace(self._spaceInFront())
    def _beforeMove(self):
        """Check if the robot is moving out of turn or while defeated."""
        global state
        if (state != self.name) and (state != "win"):
            raise OutOfTurnError,self.name
        elif state == "win":
            raise RobotIsDefeatedError,self.name
    def _afterMove(self):
        """When a robot has moved, changes the state of the game so it's the
other robot's turn."""
        global field, state
        if state == self.name:
            for i in field:
                if i.name != self.name:
                    state = i.name
    def calculateCoordinates(self,distance=1,direction=None,position=None):
        """Convenience function for calculating positions.
        Returns the coordinates of the position described."""
        if direction == None:
            directionToCheck = self.rotation
        else:
            directionToCheck = direction
        if position == None:
            locationToReturn = self.position
        else:
            locationToReturn = position
        directionToCheck %= 4
        for i in range(distance):
            if directionToCheck == 0:
                locationToReturn= (locationToReturn[0],locationToReturn[1]-1)
            elif directionToCheck == 1:
                locationToReturn= (locationToReturn[0]+1,locationToReturn[1])
            elif directionToCheck == 2:
                locationToReturn= (locationToReturn[0],locationToReturn[1]+1)
            elif directionToCheck == 3:
                locationToReturn= (locationToReturn[0]-1,locationToReturn[1])
        return locationToReturn
    def lookInFront(self):
        "Looks at the space in front of the robot"
        return self.lookAtSpace(self.calculateCoordinates())
    def lookAtSpace(self,space):
        "Checks a space"
        return self._getSpace(space)
    def takeDamage(self,damage):
        "Don't call. Makes this robot take damage."
        global state, field
        self.health -= damage
        if self.health <= 0:
            state = "win"
    def attack(self):
        "Attacks"
        self._beforeMove()
        result = self._attack()
        self._afterMove()
        return result
    def goBack(self):
        "Moves backwards"
        self._beforeMove()
        result = self._goBack()
        self._afterMove()
        return result
    def goForth(self):
        "Moves forwards"
        self._beforeMove()
        result = self._goForth()
        self._afterMove()
        return result
    def turnLeft(self):
        "turns left"
        self._beforeMove()
        result = self._turnLeft()
        self._afterMove()
        return result
    def doNothing(self):
        "Does nothing, ending the turn"
        self._beforeMove()
        result = "success"
        self._afterMove()
        return result
    def turnRight(self):
        "Turns right"
        self._beforeMove()
        result = self._turnRight()
        self._afterMove()
        return result
    def locateEnemy(self):
        "Returns the coordinates of an enemy"
        global field
        for i in field:
            if i.name != self.name:
                return i.position, i.rotation

def drawBattlefield(bot1, bot2):
    """draws a battlefield with ASCII.
    Replace all instances of drawBattlefieldPygame with this function
    to draw the battlefield in ASCII art.

    Does not draw red or blue squares."""
    output = ""
    for row in range(12):
        for column in range(12):
            if row in [0,11]:
                #draw wall
                output += "--"
            elif column in [0,11]:
                #draw wall
                output += "||"
            elif (column,row) == bot1.position:
                #draw robot 1
                output += ["^",">","V","<"][bot1.rotation]+"1"
            elif (column,row) == bot2.position:
                #draw robot 2
                output += ["^",">","V","<"][bot2.rotation]+"2"
            else:
                output += "  "
        output += "\n"
    print output
    #Display robot health
    print "Bot 1's Health:",bot1.health
    print "Bot 2's Health:",bot2.health

def drawBattlefieldPygame(bot1, bot2):
    """draws the battlefield with Pygame"""
    global state, redsquares, bluesquares, bot1img, bot2img, namefont, ai1name, ai2name

    #Get the display surface
    screen = pygame.display.get_surface()
    
    
    #If the Pygame window isn't open, open it.
    if screen == None:
        screen = pygame.display.set_mode((640,480))
    #Clear the screen
    screen.fill((0,0,0))
    #Draw colored squares
    for i in redsquares:
        pygame.draw.rect(screen,(64,0,0),((  (i[0]-1)*48,(i[1]-1)*48  ),(48,48)))
    for i in bluesquares:
        pygame.draw.rect(screen,(0,0,64),(((i[0]-1)*48,(i[1]-1)*48),(48,48)))
    #draw grid lines
    for i in range(1,10):
        pygame.draw.line(screen,(50,50,50),(0,i*48),(480,i*48),5)
        pygame.draw.line(screen,(50,50,50),(i*48,0),(i*48,480),5)
    
    #Get the screen positions of the robots
    bot1pos = ((bot1.position[0]-1)*48,(bot1.position[1]-1)*48)
    bot2pos = ((bot2.position[0]-1)*48,(bot2.position[1]-1)*48)
    #Draw the robots on the screen
    screen.blit(pygame.transform.rotate(bot1img,-90*bot1.rotation),bot1pos)
    screen.blit(pygame.transform.rotate(bot2img,-90*bot2.rotation),bot2pos)
    #Write the names of the robots on the screen
    screen.blit(namefont.render(ai1name,True,(255,0,0),(0,0,0)),(480,0))
    screen.blit(namefont.render(ai2name,True,(0,0,255),(0,0,0)),(480,40))
    #Draw the robot's health bars
    pygame.draw.rect(screen,(0,255,0),((480,20),(int(bot1.health*160/100.0),10)))
    pygame.draw.rect(screen,(0,255,0),((480,60),(int(bot2.health*160/100.0),10)))
    pygame.display.flip()
    #If the game is over...
    if state == "win":
        running = True
        #wait for the user to close the window
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
    else:
        #Otherwise, add a delay between frames
        time.sleep(0.1)

#Create Font object
namefont = pygame.font.Font(None,25)
#Get names of competitors
ai1name = raw_input("Enter red AI: ")
ai2name = raw_input("Enter blue AI: ")
#Dynamically import the robots as modules
ai1 = __import__(ai1name) 
ai2 = __import__(ai2name)
#Create the two Robot objects with the two AI objects
field = [Robot("red",ai1.AI(),(10,5),3),Robot("blue",ai2.AI(),(1,5),1)]
redsquares = []
bluesquares = []
state = "red"

pygame.display.set_mode((640,480))
#Load graphics, draw initial battlefield
bot1img = pygame.image.load("DozerRed.png").convert_alpha()
bot2img = pygame.image.load("DozerBlue.png").convert_alpha()
drawBattlefieldPygame(field[0],field[1]) #ASCII/PYGAME


numberOfTurns = 0

while state != "win":
    #color squares
    if not (field[0].position[0],field[0].position[1]) in redsquares:
        redsquares.append((field[0].position[0],field[0].position[1]))
        while (field[0].position[0],field[0].position[1]) in bluesquares:
            bluesquares.remove((field[0].position[0],field[0].position[1]))
    if not (field[1].position[0],field[1].position[1]) in bluesquares:
        bluesquares.append((field[1].position[0],field[1].position[1]))
        while (field[1].position[0],field[1].position[1]) in redsquares:
            redsquares.remove((field[1].position[0],field[1].position[1]))
    
    drawBattlefieldPygame(field[0],field[1]) #ASCII/PYGAME
    for i in field:
        try: # Prevent PythonBattle from crashing when AI code fails
            i.ai.turn()
        except Exception,e:
            print i.name,"failed with error:"
            print e
    numberOfTurns += 1
    if numberOfTurns == 1000:
        #If the battle runs longer than ~1.6 min, pull the plug
        state = "stalemate"
        break
#Color squares one last time
if not (field[0].position[0],field[0].position[1]) in redsquares:
    redsquares.append((field[0].position[0],field[0].position[1]))
    while (field[0].position[0],field[0].position[1]) in bluesquares:
        bluesquares.remove((field[0].position[0],field[0].position[1]))
if not (field[1].position[0],field[1].position[1]) in bluesquares:
    bluesquares.append((field[1].position[0],field[1].position[1]))
    while (field[1].position[0],field[1].position[1]) in redsquares:
        redsquares.remove((field[1].position[0],field[1].position[1]))
if state == "stalemate":
    drawBattlefieldPygame(field[0],field[1])#ASCII/PYGAME
    print "Turn limit reached!"
    #If either robot has higher health, it wins
    if field[0].health > field[1].health:
        print "Red wins!"
    elif field[1].health > field[0].health:
        print "Blue wins!"
    else:
        #Otherwise, whoever has the most squares wins
        print "Stalemate detected!"
        print "Counting colored squares..."
        time.sleep(2) #Pause for dramatic effect...
        if len(redsquares) > len(bluesquares):
            print "The winner is Red with",len(redsquares),"squares!"
            print "(Blue had",len(bluesquares),"squares)"
        elif len(redsquares) < len(bluesquares):
            print "The winner is Blue with",len(bluesquares),"squares!"
            print "(Red had",len(redsquares),"squares)"
        else:
            print "Tie! Both opponents had",len(redsquares),"squares."
    state = "win"
else:
    #print who wins
    if field[0].health > field[1].health:
        print "Red wins with",field[0].health,"health!"
    if field[1].health > field[0].health:
        print "Blue wins with",field[1].health,"health!"
drawBattlefieldPygame(field[0],field[1])     #ASCII/PYGAME
pygame.quit() #ASCII/PYGAME
