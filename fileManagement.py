class fileManagement():
    def __init__(self, fileName):
        self.fileName = fileName
        self.contentsOfFile = ""
        self.someList = []
        self.lineNumber = 0

    def readList(self):
        self.responses = self.contentsOfFile.split("\n")
        for self.response in self.responses:
            if(self.response != ""):
                self.someList.append(self.response.strip())
        return(self.someList)

    def readFile(self):
        try:
            file = open(self.fileName, "r")
            self.contentsOfFile = file.read()
            file.close()
        except FileNotFoundError:
            print("No file exists!")
        return(self.contentsOfFile)
    def writeToFile(self, contents):
        file = open(self.fileName, "w")
        file.write(contents)
        file.close()

    def appendToFile(self, contents):
        file = open(self.fileName, "a")
        file.write(contents)
        file.close()

    def getFileLine(self, lineNumber):
        print(self.someList)
        return(self.someList[lineNumber])

    def incrementLineNumber(self):
        self.lineNumber += 1
        if(self.lineNumber >= len(self.someList)):
            self.lineNumber = 0
        return(self.lineNumber)
    def setLineNumber(self, lineNumber):
        self.lineNumber = lineNumber
    def getFileName(self):
        return(self.fileName)
    def getContentsOfFile(self):
        return(self.contentsOfFile)
    def getList(self):
        return(self.someList)
