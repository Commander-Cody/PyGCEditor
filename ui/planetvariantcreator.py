from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QLineEdit

from gameObjects.planet import Planet
from gameObjects.gameObjectRepository import GameObjectRepository
from ui.qtautocomplete import AutoCompleter
from ui.dialogs import Dialog, DialogResult

class PlanetVariantCreator(Dialog):
    '''Class for a "create planet variant" dialog box'''
    def __init__(self, repository: GameObjectRepository):
        self.__dialog: QDialog = QDialog()
        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__formLayout: QFormLayout = QFormLayout()
        self.__buttonLayout: QHBoxLayout = QHBoxLayout()

        self.__autoComplete = None

        self.__inputBaseName: QLineEdit = QLineEdit(self.__dialog)
        self.__inputVariantName: QLineEdit = QLineEdit(self.__dialog)

        self.__okayButton: QPushButton = QPushButton("OK")
        self.__okayButton.clicked.connect(self.__okayClicked)

        self.__cancelButton: QPushButton = QPushButton("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelClicked)

        self.__formLayout.addRow("New planet variant name", self.__inputVariantName)
        self.__formLayout.addRow("Base Planet", self.__inputBaseName)

        self.__buttonLayout.addWidget(self.__okayButton)
        self.__buttonLayout.addWidget(self.__cancelButton)

        self.__layout.addLayout(self.__formLayout)
        self.__layout.addLayout(self.__buttonLayout)

        self.__dialog.setWindowTitle("New planet variant")
        self.__dialog.setLayout(self.__layout)

        self.__result = DialogResult.Cancel

        self.__repository = repository

        self.__variantName = ""
        self.__basePlanet = None


    def show(self, basePlanet = None) -> DialogResult:
        '''Display dialog non-modally'''
        if basePlanet is not None:
            self.__inputBaseName.setText(basePlanet.name)
        self.__setupAutoComplete()
        self.__dialog.exec()
        return self.__result

    def getCreatedPlanet(self) -> Planet:
        '''Returns the created planet object'''
        base = self.__repository.getPlanetByName(self.__basePlanet)
        planet: Planet = Planet(self.__variantName)

        planet.variantOf = base.name
        planet.x = base.x
        planet.y = base.y
        return planet

    def __setupAutoComplete(self) -> None:
        '''Sets up autocompleter with planet names'''
        autoCompleter = AutoCompleter(self.__repository.getPlanetNames())
        planetCompleter = autoCompleter.completer()
        self.__inputBaseName.setCompleter(planetCompleter)

    def __okayClicked(self) -> None:
        '''Okay button handler. Performs minor error checking and adds trade route to repository'''
        self.__variantName = self.__inputVariantName.text()
        self.__basePlanet = self.__inputBaseName.text()

        if not self.__inputDataIsValid():
            print("Error! Couldn't find base planet!")
            return

        if self.__repository.planetExists(self.__variantName):
            print("Error! Planet already exists!")
            return

        self.__result = DialogResult.Ok
        self.__dialog.close()

    def __inputDataIsValid(self) -> bool:
        '''Checks if the given data is filled in and the base planet exist in the repo'''
        return self.__variantName and self.__repository.planetExists(self.__basePlanet)

    def __cancelClicked(self) -> None:
        '''Cancel button handler. Closes dialog box'''
        self.__dialog.close()