from commands.Command import Command
from gameObjects.planet import Planet
from ui.planetvariantcreator import PlanetVariantCreator
from ui.dialogs import Dialog, DialogResult
from ui.DialogFactory import DialogFactory
from ui.mainwindow_presenter import MainWindowPresenter

class ShowPlanetVariantCreatorDialogCommand(Command):
    '''Class to handle displaying the trade route creator dialog box'''
    def __init__(self, mainWindowPresenter: MainWindowPresenter, dialogFactory: DialogFactory):
        self.__dialogFactory = dialogFactory
        self.__presenter = mainWindowPresenter

    def execute(self, planet = None) -> None:
        '''Runs the dialog and passes results to the presenter and repository'''
        dialog = self.__dialogFactory.makePlanetVariantCreationDialog()
        result: DialogResult = dialog.show(planet)

        if result is DialogResult.Ok:
            planet: Planet = dialog.getCreatedPlanet()
            self.__presenter.onNewPlanetVariant(planet)