import sys

from math import sqrt
from numpy import array, radians, sin, cos, around

from config import Config
from RepositoryCreator import RepositoryCreator
from addOns.Quadrant import Quadrant, QuadrantSuperposition

from xmlUtil.xmlwriter import XMLWriter
from xmlUtil.xmlreader import XMLReader
from xmlUtil.xmlstructure import XMLStructure


################## Global variables for configuration ##################

### Planet selection ###
# Criteria which determine which planets will be moved (planets must fulfill all criteria to be moved)
# Options: "all", "campaigns", "files", "quadrants", "custom"
useSelectionCriteria = ["campaigns"]

# Campaign names from which planets should be moved
campaigns = ["Sandbox_Large_Stargate_Universe_Tauri"]
# Xml files from which planets should be moved
files = ["Planets_Systemlord_Alliance.xml"]
# Area from which planets should be moved: Quadrant(x_range, y_range)
areas = [Quadrant([300,10000],[-10000,-500])]

# Create a custom selection criterion function for the "custom" criterion
def customSelectionFunc(planet, repository) -> bool:
    return True

# Or use empty useSelectionCriteria and fill in logic in the return value here:
def allowMigration(inCampaigns: bool, inFiles: bool, inQuadrant: bool, inCustom: bool) -> bool:
    return inCampaigns and inFiles or inQuadrant

# Planets to be ignored (e.g. galaxy core art model)
ignore = ["Galaxy_Core_Art_Model", "Pegasus_Prelude_Galaxy_Core_Art_Model"]


### Movement ###
# Set the movement type (choose from "offset", "stretch", "rotation")
selectedMoveType = "offset"
# Configure the movement types:
# Shift planets by a 2d vector
offset = (100,100)
# Stretch planets' distance to the pointOfReference by this factor
stretchFactor = 0.1
# Rotate planets counter-clockwise around the pointOfReference (in degrees)
rotationAngle = 40
# Point of reference (usually the origin)
pointOfReference = (-400,0)
# Round coordinates to this number of decimals (important for rotations)
coordDecimals = 2


################## Main ##################

def migratePlanets():
    config: Config = Config()
    XMLStructure.dataFolder = config.dataPath

    repositoryCreator: RepositoryCreator = RepositoryCreator()
    repository = repositoryCreator.constructRepository(XMLStructure.dataFolder)
    
    migratingPlanets = determineMigratingPlanets(repository)
    performPlanetsMovement(migratingPlanets)
    writeCoordinates(migratingPlanets)



def determineMigratingPlanets(repository):
    migratingPlanets = []
    migrationAllowed = buildSelectionCriteria(repository, campaigns, files, QuadrantSuperposition(areas), customSelectionFunc)
    
    for planet in repository.planets:
        if planet.name not in ignore and migrationAllowed(planet):
            migratingPlanets.append(planet)
    
    return migratingPlanets



################## Planet Movement ##################

def performPlanetsMovement(planets):
    performMove = getMovementAction()
    performMove(planets)

def getMovementAction():

    def movementShift(planets):
        shiftCoords(planets, offset)
    
    def movementStretch(planets):
        stretchPlanetPositions(planets, stretchFactor, pointOfReference)
    
    def movementRotation(planets):
        rotatePlanets(planets, rotationAngle, pointOfReference)
    
    moveTypeActions = {
        # Move planets by a 2d vector
        "offset" : movementShift,
        # Stretch the planet layout 
        "stretch" : movementStretch,
        # Rotate the planets around an origin
        "rotation" : movementRotation
        # Mirroring?
    }
    return moveTypeActions[selectedMoveType]


### Shifting and position conversion ###

def shiftCoords(planets, shift):
    for planet in planets:
        new_coords = positionAsArray(planet) + shift
        setPosition(planet, new_coords)

def positionAsArray(planet):
    return array([planet.x, planet.y])

def setPosition(planet, a):
    around(a, coordDecimals, a)
    planet.x, planet.y = a[0], a[1]

def performActionInShiftedCoords(planets, action, alt_origin = (0,0)):
    shift = -array(alt_origin)
    shiftCoords(planets, shift)
    action(planets)
    shiftCoords(planets, -shift)

### Stretching ###

def stretchPlanetPositions(planets, factor, origin = (0,0)):
    def action(planets):
        stretchPlanetsWrtOrigin(planets, factor)
    performActionInShiftedCoords(planets, action, origin)

def stretchPlanetsWrtOrigin(planets, factor):
    for planet in planets:
        position = positionAsArray(planet)
        setPosition(planet, factor*position)

### Rotation ###

def rotatePlanets(planets, degrees, rotation_center = (0,0)):
    def action(planets):
        rotatePlanetsAroundOrigin(planets, degrees)
    performActionInShiftedCoords(planets, action, rotation_center)

def rotatePlanetsAroundOrigin(planets, degrees):
    R = rotationMatrix(degrees)
    for planet in planets:
        position = positionAsArray(planet)
        setPosition(planet, R.dot(position))

def rotationMatrix(degrees):
    #if degrees < 0:
    #    degrees += 360
    angle = radians(degrees)
    s, c = sin(angle), cos(angle)
    return array([[c, -s], [s, c]])


################## Selection criteria ##################

def buildSelectionCriteria(repo, campaigns = [], files = [], area = QuadrantSuperposition(), selectionFunction = None):
    
    def selectAll(planet):
        return True
    
    def selectByCampaign(planet):
        for campaign in repo.campaigns:
            if campaign.name in campaigns and planet in campaign.planets:
                return True
        return False
    
    def selectByFile(planet):
        if planet.containingFile in files:
            return True
        return False
    
    def selectByQuadrant(planet):
        return area.contains(planet.x, planet.y)
    
    def selectByCustomCriterion(planet):
        if not selectionFunction:
            return True
        return selectionFunction(planet, repo)
    
    allowByCriterion = {
        # Should all planets be moved
        "all" : selectAll,
        # Planets from which campaign should be affected
        "campaigns" : selectByCampaign,
        # Planets from which files should be affected
        "files" : selectByFile,
        # Planets from which quadrant of the galaxy should be affected
        "quadrants" : selectByQuadrant,
        # Custom selection
        "custom" : selectByCustomCriterion
    }
    
    if len(useSelectionCriteria) > 0:
        def migrationAllowedByBasicCriteria(planet):
            for criterion in useSelectionCriteria:
                if not allowByCriterion[criterion](planet):
                    return False
            return True
        
        return migrationAllowedByBasicCriteria
    
    def migrationAllowedByAdvancedCriteria(planet):
        return allowMigration(selectByCampaign(planet), selectByFile(planet), selectByQuadrant(planet), selectByCustomCriterion(planet))
    
    return migrationAllowedByBasicCriteria


################## Save new coordinates ##################

def writeCoordinates(migratedPlanets):
    gameObjectFile = XMLStructure.dataFolder + "/XML/GameObjectFiles.XML"
    planetRoots = XMLReader().findPlanetFilesAndRoots(gameObjectFile)
    
    XMLWriter().planetCoordinatesWriter(XMLStructure.dataFolder + "/XML/", planetRoots, getPlanetCoordsByNameDict(migratedPlanets))

def getPlanetCoordsByNameDict(planets):
    coordsByName = {}
    for planet in planets:
        coordsByName[planet.name] = [planet.x, planet.y]
    return coordsByName
