#-------------------------------------------------------------------------------
# Name:        mineSolver
# Purpose:     To solve minesweeper using the minesweeperonline object to
#              interface with minesweeper.com
#
# Author:      finnbarr1
#
# Created:     22/08/2018
#-------------------------------------------------------------------------------

from mineSweeperOnline import mineSweeperOnline
from mineSweeperOnline import UnexpectedAlertError
from datetime import datetime
from fileManagement import fileManagement
import time

class mineSolver():
    def __init__(self, **args):
        """
        Params: **args
        All Params:
            No Param will result in level 3 being selected
            level = (1-3)
            Or custom:
                height = ??
                width = ??
                mines = ??

        Dificulty levels are:
            1 - Beginner
            2 - Intermediate
            3 - Expert
            Custom (input your own values)
        """
        self._game = mineSweeperOnline()
        self._height = self._game.getBoardHeight()
        self._width = self._game.getBoardWidth()
        self._area = self._height * self._width

        self._totalMines = self._game.getBoardTotalMines()
        self._remaingBlankSquares = 0
        self._fieldDict = {}
        self._firstX = int(self._width/2)
        self._firstY = int(self._height/2)
        self._island = []
        self._flag = 0


    def resetGame(self):
        self._game.reset()
        location = self.convertToLocation(self._firstX,self._firstY)
        self._island = [location]
        self._createDict()

    def convertToXY(self, num):
        y = int(num/self._width) + 1
        x = int(num % self._width) + 1
        return(x,y)

    def convertToLocation(self, x,y):
        location = ((x-1) + (self._width)*(y-1))
        return(location)


    def _createDict(self):
        self._remaingBlankSquares = 0
        for location in range(0, self._area):
            self._fieldDict[location] = "blank"
            self._remaingBlankSquares += 1

    def _updateDict(self):
        """
        Returns if game is over
        """
        visitedLocations = {} #So we dont hit the same location twice
        blankSquares = 0
        neighbors = [(-1,1),(0,1),(1,1),(-1,0),(1,0),(-1,-1),(0,-1),(1,-1)]
        stack = []
        for homeLocation in self._island:
            if(homeLocation not in visitedLocations):
                stack.append(homeLocation)

                #Initialization
                x,y = self.convertToXY(homeLocation)
                state = self._game.getTileState(x,y) #origin state
                visitedLocations[homeLocation] = False #Puts origin in dict with value false to indicate its not a blank square
                self._fieldDict[homeLocation] = state
                dictionarySize = 1 #Speedy way to know the size of visitedLocations

                gameOverList = ["bombrevealed","bombdeath"]
                if(state in gameOverList): #means game over
                    return(False)

                while(stack):
                    homeLocation = stack.pop()
                    x,y = self.convertToXY(homeLocation)
                    for neighbor in neighbors:
                        i,j = neighbor
                        inBounds = ((i+x > 0) and (j+y > 0) and (i+x < self._width+1) and (j+y < self._height+1)) #In the confinds of the game
                        neighborLocation = self.convertToLocation(x+i, j+y)
                        inDict = neighborLocation in visitedLocations
                        if(inBounds and not inDict):
                            neighborState = ""
                            if(self._fieldDict[neighborLocation] == "blank"):
                                neighborState = self._game.getTileState(x+i,y+j)
                                self._fieldDict[neighborLocation] = neighborState
                            else: #Every nonBlank tile is static no need to update it (saves time)
                                neighborState = self._fieldDict[neighborLocation]
                            neighborBlank = False
                            if(neighborState in gameOverList): #means game over
                                return(False)
                            if(neighborState == "blank"):
                                blankSquares += 1
                                neighborBlank = True
                            visitedLocations[neighborLocation] = neighborBlank #Puts neighbor as a key in dict
                            dictionarySize += 1
                            if(not neighborBlank):
                                stack.append(neighborLocation)

        self._remaingBlankSquares = self._area - (dictionarySize - blankSquares) #finds total blank squares remaing on board
        return(True)


    def _getPercentages(self):
        """
        Returns location with lowest probability of being a mine
        """
        lowestPercent = 2.0
        lowestX = 1#int(self._width/2)
        lowestY = 1#int(self._height/2)
        percentDict = {}

        for location in range(0, self._area):
            state = self._fieldDict[location]
            unicode_val = ord(state[0])
            if((unicode_val >= 49) and (unicode_val <= 56)): #if its a 1-8
                x,y = self.convertToXY(int(location))
                blanks = 0
                self._flags = 0
                number = int(state)
                temp = []
                neighbors = [(-1,1),(0,1),(1,1),(-1,0),(1,0),(-1,-1),(0,-1),(1,-1)]
                for offset in neighbors:
                    i,j = offset
                    inBounds = ((i+x > 0) and (j+y > 0) and (i+x < self._width+1) and (j+y < self._height+1))

                    if(inBounds):
                        offsetLocation = ((x+i) + (self._width)*(y+j-1))
                        if(self._fieldDict[offsetLocation-1] == "blank"):
                            blanks+=1
                            temp.append(offsetLocation)
                        if(self._fieldDict[offsetLocation-1] == "bombflagged"):
                            self._flags+=1
                if(blanks != 0): #takes out solved parts
                    percent = (number - self._flags)/blanks
                    for offset in temp:
                        offset = offset - 1
                        if(offset in percentDict):
                            if((percent == 0) or (percentDict[offset] == 0)):
                                percentDict[offset] = 0
                            elif(percent > percentDict[offset]):
                                percentDict[offset] = percent
                        else:
                            percentDict[offset] = percent

        return(percentDict)

    def _returnLowest(self, percentDict, lowest, flagsPlaced):
        output = []
        for item in percentDict:
            if(percentDict[item] == lowest):
                x,y = self.convertToXY(item)
                output.append((x,y))
                if(lowest != 0):
                    if(flagsPlaced): #No need to take an unnessary risk return an empty list
                        return([])
                    else:
                        return(output) #If lowest is above 0, only return 1 location to click
        return(output)

    def _findSafestCick(self, percentDict, flagsPlaced):
        lowest = 2.0
        output = []
        for item in percentDict:
            if(percentDict[item] < lowest):
                lowest = percentDict[item]
        if(not flagsPlaced): #If flags were NOT just placed on the board
            #Compare to percentage for a random click
            mines = self._game.getMinesRemaining()
            randomPercent = (mines) / (self._remaingBlankSquares)
            print("Lowest:", lowest)
            print("Random:", randomPercent)
            if(randomPercent < lowest):
                if(len(percentDict) > 0): #Selects Random(ish) square
                    """
                    Builds a dict of forbidden tiles (ones that are already clicked, flagged or next to a tile)
                    Then picks the first board location that is not in that dict
                    If everything is forbidden then pick the forbidden tile with the lowest chance of it being a bomb
                    """
                    finalx = 0
                    finaly = 0
                    neighbors = [(-1,1),(0,1),(1,1),(-1,0),(1,0),(-1,-1),(0,-1),(1,-1)]
                    forbidden = {}
                    for square in self._fieldDict:
                        if(self._fieldDict[square] != "blank"):
                            forbidden[square] = True
                    for square in percentDict:
                        forbidden[square] = True

                    for rando in range(0,self._area):
                        if(rando not in forbidden):
                            self._island.append(rando)
                            x,y = self.convertToXY(rando)
                            output.append((x,y))
                            return(output)
                    #Only makes it here if all non forbidden squares are taken
                    ans = list(percentDict.keys())[0]
                    finalx, finaly = self.convertToXY(ans)
                    output.append((finalx,finaly))
                    return(output)
                else: #First time through
                    output.append((self._firstX, self._firstY))  #Start at predifined location
                    return(output)
            else: #Returns 1 lowest tile (unless its 0, then it get all 0 tiles)
                output = self._returnLowest(percentDict, lowest, flagsPlaced)
                return(output)
        else: #If flags were just placed on the board click on all 0s
            self._returnLowest(percentDict, lowest, flagsPlaced)
            return(output)

    def _checkForFlagging(self, percentDict):
        flagList = []
        for item in percentDict:
            percent = percentDict[item]
            if(percent == 1.0):
                flagList.append(item)
        return(flagList)
    def getMinesRemaining(self):
        return(self._game.getMinesRemaining())
    def getTime(self):
        return(self._game.getTime())
    def resetWeb():
        self._game.closeWebpage()
        self._game.open()
    def solve(self):
        times = []

        self._createDict()
        gameOn = True
        while(gameOn):

            percentDict = self._getPercentages()
            flagList = self._checkForFlagging(percentDict)
            flagsPlaced = False
            while(flagList):
                flagsPlaced = True
                flagLocation = flagList.pop()
                x,y = self.convertToXY(flagLocation)
                self._game.flagTile(x,y)
                #Updates the board before clicking anything on screen

            outputList = self._findSafestCick(percentDict, flagsPlaced)
            print("{0} item(s) to be clicked...".format(len(outputList)))
            for coordinates in outputList:
                x,y = coordinates
                self._game.clickTile(x,y)

            print("updating....")
            gameOn = self._updateDict() #returns False if there is a bomb on screen
            if(self._flag >= self._totalMines):  #Sometimes the game is over even when no bombs are on screen
                gameOn = False
        time.sleep(1) #Serves no purpose other than to give time for the user to see how it lost/won
    def acceptAlert(self):
        self._game.acceptAlert()

def main():
    game = mineSolver()
    needReset = False
    fileLocation = "scores.csv"
    file = fileManagement(fileLocation) #csv with all game scores
    while(True):
        game.resetGame()
        start = int(time.time())
        try:
            game.solve()
        except UnexpectedAlertError:  #WEBPAGE BRINGS UP ALERT WHEN YOU WIN UGHHHHHH
            needReset = True #Easy way to handle these pesky alerts
        mines = 0
        now = datetime.now()
        try:
            mines = game.getMinesRemaining()
            gameTime = game.getTime() #We try to use the official game time
            if(gameTime >= 999): #Official game time maxes out at 999 seconds so we will use ours insted if this happens
                finish = int(time.time()) #If we are forced we will use our own measured time elapsed
                gameTime = finish - start
        except UnexpectedAlertError: #UGHHHH I HATE WEBPAGE ALERTS
            print("Alert on screen!")
            game.acceptAlert()
            finish = int(time.time()) #If we are forced we will use our own measured time elapsed
            gameTime = finish - start
            needReset = True #Easy way to handle these pesky alerts
            file.appendToFile("ALERT ACCEPTED SUCCESFULLY\n")
        string = ("{0},{1},{2}\n".format(str(now),str(mines),str(gameTime)))
        file.appendToFile(string)
        print(string)
        #if(needReset):
        #    game.resetWeb()


if __name__ == '__main__':
    main()

