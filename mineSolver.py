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
                flags = 0
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
                            flags+=1
                if(blanks != 0): #takes out solved parts
                    percent = (number - flags)/blanks
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

    def _findSafestCick(self, percentDict):
        lowest = 2.0
        output = []
        for item in percentDict:
            if(percentDict[item] < lowest):
                lowest = percentDict[item]
        #Compare to percentage for a random click
        mines = self._game.getMinesRemaining()
        randomPercent = (mines) / (self._remaingBlankSquares)
        print("Lowest:", lowest)
        print("Random:", randomPercent)
        if(randomPercent < lowest):
            if(len(percentDict) > 0):
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
        else:
            for item in percentDict:
                if(percentDict[item] == lowest):
                    x,y = self.convertToXY(item)
                    output.append((x,y))
                    if(lowest != 0):
                        return(output) #Stops it from click multipole with like a 50% of a failure
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
        """
        Returns True if a window reset is needed
        """
        times = []

        self._createDict()
        gameOn = True
        while(gameOn):

            percentDict = self._getPercentages()
            flagList = self._checkForFlagging(percentDict)
            if(not flagList):
                outputList = self._findSafestCick(percentDict)
                print("{0} item(s) to be clicked...".format(len(outputList)))
                for coordinates in outputList:
                    x,y = coordinates
                    self._game.clickTile(x,y)

            else:
                while(flagList):
                    flagLocation = flagList.pop()
                    x,y = self.convertToXY(flagLocation)
                    self._game.flagTile(x,y)
                    #Updates the board before clicking anything on screen
            print("updating....")
            gameOn = self._updateDict()
        time.sleep(1)
        return(False)

def main():
    game = mineSolver()
    needReset = False
    fileLocation = "scores.csv"
    file = fileManagement(fileLocation) #csv with all game scores
    while(True):
        game.resetGame()
        try:
            game.solve()
        except UnexpectedAlertError:  #WEBPAGE BRINGS UP ALERT WHEN YOU WIN UGHHHHHH
            needReset = True
        mines = game.getMinesRemaining()
        time = game.getTime()
        now = datetime.now()
        string = ("{0},{1},{2}\n".format(str(now),str(mines),str(time)))
        file.appendToFile(string)
        print(string)
        if(needReset):
            game.resetWeb()


if __name__ == '__main__':
    main()

