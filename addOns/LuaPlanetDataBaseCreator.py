import sys

from math import sqrt

from config import Config
from RepositoryCreator import RepositoryCreator



################## Global variables for configuration ##################

# This defines the data sets in the Lua table and what campaign set the data comes from
# CampaignXMLName : LuaTableName
campaigns = {
"Sandbox_Gateways_Underworld" : "Gateways",
"Sandbox_Equal_Footing_Underworld" : "Equal_Footing"
}
# MaximumFleetMovementDistance
autoConnectionDistance = 100
# Planets to be ignored (only meant for pseudo planets like the galaxy core art model)
ignore = ["Galaxy_Core_Art_Model"]
# Indentations
basic_indent = "  "
def indent(n):
    return n*basic_indent



################## Main ##################

def writePlanetDatabaseLuaTable():
    config: Config = Config()
    path = config.dataPath

    repositoryCreator: RepositoryCreator = RepositoryCreator()
    repository = repositoryCreator.constructRepository(path)

    outputFile = open("PlanetDatabase.lua", "w")

    outputFile.write(createPlanetDatabaseTable(repository).toSingleStr())

    outputFile.close()



################## Create the table ##################

def createPlanetDatabaseTable(repository):
    campaignTables = []
    for campaign in repository.campaigns:
        #print(campaign.name)
        try:
            campaignAlias = campaigns[campaign.name]
        except KeyError:
            continue
        campaignTables.append(createCampaignSpecificTable(campaignAlias, campaign.planets, campaign.tradeRoutes))

    return createLuaTable("PlanetDataBase", mergeWithCommas(campaignTables))

def createCampaignSpecificTable(campaignName, allPlanets, allTradeRoutes):
    content = []
    for planet in allPlanets:
        if not planet.name in ignore:
            content.append(createPlanetData(planet, allPlanets, allTradeRoutes))
    content = mergeWithCommas(content)

    return createLuaTable(campaignName, content)

def mergeWithCommas(textLineObjects):
    res = TextLines()
    if len(textLineObjects) < 1:
        return res

    # Loop through all objects but the last
    for k in range(len(textLineObjects)-1):
        # Add a comma to the last line of each object
        textLineObjects[k].lines[-1] = textLineObjects[k].lines[-1] + ","
        res.add(textLineObjects[k])

    # Last one gets added without a comma
    return res.add(textLineObjects[-1])

def createPlanetData(planet, allPlanets, allTradeRoutes):

    planetConnectionListContent = TextLines.asStrings(getConnections(planet, allPlanets, allTradeRoutes)).addCommas()#.addIndent()

    planetConnectionList = createLuaTable("ConnectedTo", planetConnectionListContent)

    return createLuaTable(planet.name, planetConnectionList)

# Parameters: String, TextLines
# Returns a lua table of the form:
'''
name = {
    content
}
'''
# as a TextLines object
def createLuaTable(name, content):
    return TextLines([name + " = {"]).add(content.addIndent()).append("}")


################## Find connections ##################

def getConnections(planet, planets, tradeRoutes):
    # Traderoutes
    connections = []
    for tr in tradeRoutes:
        if tr.start == planet and tr.end.name not in connections:
            connections.append(tr.end.name)
        elif tr.end == planet and tr.start.name not in connections:
            connections.append(tr.start.name)

    # Auto connections
    for p1 in planets:
        if p1 != planet and not p1.name in ignore:
            if not p1.name in connections and distance(p1,planet) < autoConnectionDistance:
                connections.append(p1.name)

    return connections

# Parameters: Planet, Planet
def distance(p1,p2):
    return sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)


################## Class which consists of a list of strings (lines of text) ##################
#to keep lines of text seperate and modifiable until we want to merge them into a single string

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
