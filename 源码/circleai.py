"""
AI Name: Circle AI

Made by: Carter

Strategy: Drive in circles.  Attack any robot in your path.

"""


class AI:
    def __init__(self):
        self.isFirstTurn = True
    def turn(self):
        if self.isFirstTurn:
            self.robot.turnRight()
            self.isFirstTurn = False
        elif self.robot.lookInFront() == "bot":
            self.robot.attack()
        elif self.robot.lookInFront()== "wall":
            self.robot.turnLeft()
        else:
            self.robot.goForth()