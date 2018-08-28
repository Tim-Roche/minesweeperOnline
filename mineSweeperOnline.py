#-------------------------------------------------------------------------------
# Name:        mineSweeperOnline interfacer
# Purpose:     To interface with minesweeper.com using selenium
#
# Author:      finnbarr1
#
# Created:     22/08/2018
#-------------------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException

class UnexpectedAlertError(UnexpectedAlertPresentException):
    pass

class mineSweeperOnline():
    def __init__(self):
        self.driverLocation = "C:\\Users\\TimRo\\chromedriver\\chromedriver.exe"
        self.open()

        #Default Settings
        self.height = 16
        self.width = 30
        self.totalMines = 99

    def open(self):
        self._driver = webdriver.Chrome(self.driverLocation)
        self._driver.get("http://minesweeperonline.com")
        self._gameElements = self._driver.find_element_by_id("game")

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
           (4) Custom (input your own values)
        """
        level = 4

        if("level" in args):
            level = int(args[arg])

        levelDict = {}
        levelDict[1] = "beginner"
        levelDict[2] = "intermediate"
        levelDict[3] = "expert"
        levelDict[4] = "custom"

        link = self._driver.find_element_by_id("options-link")
        link.click()
        options = self._driver.find_element_by_id("options-form")
        item = options.find_element_by_id(levelDict[level])
        item.click()

        if(level == 4):
            self.height = int(args["height"])
            self.width = int(args["width"])
            self.totalMines = int(args["totalMines"])
            customDict = {"custom_height":self.height, "custom_width":self.width,"custom_mines":self.totalMines}
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
        try:
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
        except UnexpectedAlertPresentException:
            raise UnexpectedAlertError(msg = "Unexpected Alert")


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

    def reset(self):
        face = self._gameElements.find_element_by_id("face")
        face.click()


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
        try:
            ones = self._gameElements.find_element_by_id("mines_ones").get_attribute("class")[-1:]
            tens = self._gameElements.find_element_by_id("mines_tens").get_attribute("class")[-1:]
            hundreds = self._gameElements.find_element_by_id("mines_hundreds").get_attribute("class")[-1:]
            mines = hundreds + tens + ones
            mines = int(mines)
            return(mines)
        except UnexpectedAlertPresentException:
            raise UnexpectedAlertError()

    def acceptAlert(self):
        try:
            alert = self._driver.switch_to.alert
            alert.accept()
        except UnexpectedAlertPresentException:
            raise UnexpectedAlertError()

    def closeWebpage(self):
        self._driver.close()
    def getBoardHeight(self):
        return(self.height)
    def getBoardWidth(self):
        return(self.width)
    def getBoardTotalMines(self):
        return(self.totalMines)

def main():
    pass
if __name__ == '__main__':
    main()


