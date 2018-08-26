#-------------------------------------------------------------------------------
# Name:        mineSweeperOnline interfacer
# Purpose:
#
# Author:      TimRo
#
# Created:     22/08/2018
# Copyright:   (c) TimRo 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class mineSweeperOnline():
    def __init__(self):
        self.driverLocation = "C:\\Users\\TimRo\\chromedriver\\chromedriver.exe"
        self._driver = webdriver.Chrome(self.driverLocation)
        self._driver.get("http://minesweeperonline.com")
        self._gameElements = self._driver.find_element_by_id("game")

        #Default Settings
        self._height = 16
        self._width = 30
        self._totalMines = 99

    def setDifficulty(self, **args):
        """
        Params: **args
        All Params:
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
        level = 4

        for arg in args:
            lowercase = arg.lower()
            if(lowercase == "level"):
                level = int(args[arg])
            if(lowercase == "height"):
                self._height = int(args[arg])
            if(lowercase == "width"):
                self._width = int(args[arg])
            if(lowercase == "mines"):
                self._totalMines = int(args[arg])

        levelDict = {}
        #               [Level,    H, W, Bombs]
        levelDict[1] = ["beginner", 9, 9, 10]
        levelDict[2] = ["intermediate", 16, 16, 40]
        levelDict[3] = ["expert", 16, 30, 99]
        levelDict[4] = ["custom", 20, 30, 145]

        link = self._driver.find_element_by_id("options-link")
        link.click()
        options = self._driver.find_element_by_id("options-form")
        item = options.find_element_by_id(levelDict[level][0])
        item.click()

        if(level == 4):
            customDict = {"custom_height":self._height, "custom_width":self._width,"custom_mines":self._totalMines}
            for custom in customDict:
                item = options.find_element_by_id(custom)
                item.clear()
                item.send_keys(str(customDict[custom]))

        submitButton = options.find_element_by_class_name("dialogText")
        submitButton.click()

    def getTileState(self, x,y):
        """
        INPUT: x, y (ints)
        OUTPUT: tileVal int (8 - -2)
        <Class naming on website>:
            square blank
            square open# (# = tile bomb number)
            square bombflagged

        - Returns that string value (tileVal)
        """

        xString = str(x)
        yString = str(y)
        tile = self._gameElements.find_element_by_id("{0}_{1}".format(yString, xString))
        raw = tile.get_attribute("class")
        lastWord = raw.split(" ")[1].strip()
        lastRaw = raw[-1:]
        tileVal = lastWord
        unicode_val = ord(lastRaw)
        if((unicode_val >= 48) and (unicode_val <= 56)): #If its a 0 - 8
            tileVal = lastRaw
        return(tileVal)


    def clickTile(self, x, y):
        """
        INPUT: x, y (ints)
        Result: Clicks Tile
        """
        xString = str(x)
        yString = str(y)
        tile = self._gameElements.find_element_by_id("{0}_{1}".format(yString, xString))
        tile.click()

    def flagTile(self, x, y):
        """
        INPUT: x, y (ints)
        Result: Flags Tile
        """
        xString = str(x)
        yString = str(y)
        tile = self._gameElements.find_element_by_id("{0}_{1}".format(yString, xString))
        action = ActionChains(self._driver)
        action.move_to_element(tile).perform()
        action.context_click().perform()


    def getGameState(self):
        """
        Returns face "mood" as string
        """
        face = self._gameElements.find_element_by_id("face")
        mood = face.get_attribute("class")
        return(mood)

    def isGameOver(self):
        """
        True = game over
        False = game on
        """
        mood = self.getGameState()
        if((mood == "facesmile") or (mood == "faceooh")):
            return(False)
        else:
            return(True)

    def getTime(self):
        """
        Returns how many seconds since the game started as an int (capped at 999)
        Gets it from class name
        Classes are named time#. getTime() grabes that last chr
        """
        ones = self._gameElements.find_element_by_id("seconds_ones").get_attribute("class")[-1:]
        tens = self._gameElements.find_element_by_id("seconds_tens").get_attribute("class")[-1:]
        hundreds = self._gameElements.find_element_by_id("seconds_hundreds").get_attribute("class")[-1:]
        time = hundreds + tens + ones
        time = int(time)
        return(time)

    def getMinesRemaining(self):
        """
        Returns current mines remaining
        """
        ones = self._gameElements.find_element_by_id("mines_ones").get_attribute("class")[-1:]
        tens = self._gameElements.find_element_by_id("mines_tens").get_attribute("class")[-1:]
        hundreds = self._gameElements.find_element_by_id("mines_hundreds").get_attribute("class")[-1:]
        mines = hundreds + tens + ones
        mines = int(mines)
        return(mines)

    def closeWebpage(self):
        self._driver.close()
    def getBoardHeight(self):
        return(self._height)
    def getBoardWidth(self):
        return(self._width)
    def getBoardTotalMines(self):
        return(self._totalMines)

def main():
    pass
if __name__ == '__main__':
    main()


