import sys

from math import sqrt

from config import Config
from ui.mainwindow_presenter import MainWindow, MainWindowPresenter
from RepositoryCreator import RepositoryCreator


# Global variables for configuration
autoConnectionDistance = 100
ignore = ["Galaxy_Core_Art_Model"]
basic_indent = "  "
def indent(n):
    return n*basic_indent


# Main
def main():
    config: Config = Config()
    path = config.dataPath

    repositoryCreator: RepositoryCreator = RepositoryCreator()
    repository = repositoryCreator.constructRepository(path)

    outputFile = open("PlanetDatabase.lua", "w")
    writePlanetDatabaseTable(repository.planets, repository.tradeRoutes, outputFile)
    outputFile.close()



################## Actual Functionality ##################

def writePlanetDatabaseTable(allPlanets, allTradeRoutes, outputFile):
    content = []
    for planet in allPlanets:
        if not planet.name in ignore:
            content.append(createPlanetData(planet, allPlanets, allTradeRoutes))
    content = mergeWithCommas(content)

    output = createLuaTable("PlanetDataBase", content)

    outputFile.write(output.toSingleStr())

def mergeWithCommas(textLineObjects):
    res = TextLines()
    for k in range(len(textLineObjects)-1):
        textLineObjects[k].lines[-1] = textLineObjects[k].lines[-1] + ","
        res.add(textLineObjects[k])
    return res.add(textLineObjects[-1])

def createPlanetData(planet, allPlanets, allTradeRoutes):

    planetConnectionListContent = TextLines.asStrings(getConnections(planet, allPlanets, allTradeRoutes)).addCommas()#.addIndent()

    planetConnectionList = createLuaTable("\"ConnectedTo\"", planetConnectionListContent)

    planetData = createLuaTable("\"" + planet.name + "\"", planetConnectionList)

    return planetData

# Parameters: String, TextLines
def createLuaTable(name, content):
    return TextLines([name + " = {"]).add(content.addIndent()).append("}")


def getConnections(planet, planets, tradeRoutes):
    # Traderoutes
    connections = []
    for tr in tradeRoutes:
        if tr.start == planet and tr.end not in connections:
            connections.append(tr.end.name)
        elif tr.end == planet and tr.start not in connections:
            connections.append(tr.start.name)

    # Auto connections
    for p1 in planets:
        if p1 != planet and not p1.name in ignore:
            if not p1 in connections and distance(p1,planet) < autoConnectionDistance:
                connections.append(p1.name)

    return connections

# Parameters: Planet, Planet
def distance(p1,p2):
    return sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)


# Basically a list of strings, each of which represents a line of text
class TextLines:
    def __init__(self, raw_list = []):
        self.lines = []
        for element in raw_list:
            self.lines.append(element)

    # An alternative constructor
    # Adds \" ... \" to all elements (so that the contained strings are again valid strings themselves)
    def asStrings(raw_list):
        lines = []
        for element in raw_list:
            lines.append("\"" + element + "\"")
        return TextLines(lines)

    # Add two TextLines objects to a single one
    def add(self, lines2):
        self.lines.extend(lines2.lines)
        return self

    # Append a string as an extra line to the end
    def append(self, entry):
        self.lines.append(entry)
        return self

    # Adds commas to all lines except the last
    def addCommas(self):
        for k in range(len(self.lines) - 1):
            self.lines[k] = self.lines[k] + ","
        return self

    # Adds an optional number of indents to every line
    def addIndent(self, n = 1):
        for k in range(len(self.lines)):
            self.lines[k] = indent(n) + self.lines[k]
        return self

    # Concatenates all lines to a single string with \n as seperation
    def toSingleStr(self):
        text = ""
        for line in self.lines:
            text = text + line + "\n"
        return text


# Run
main()