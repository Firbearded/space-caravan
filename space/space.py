from controller.controller import Controller
from scenes.spacemap import SpacemapScene
from space.planets_generator import PlanetsGenerator
from geometry.rectangle import Rectangle


class Space:
    PLANETS_NUMBER = 12

    def __init__(self, game, controller: Controller, name='world'):
        self.__game = game
        self.__controller = controller
        self.__name = name
        self.__spacemap_scene = SpacemapScene(self.__game)

        space_rectangle = Rectangle(0, 0, game.width, game.height)
        planets_generator = PlanetsGenerator(space_rectangle, Space.PLANETS_NUMBER, controller,
                                             self.__spacemap_scene)
        self.__planets = planets_generator.generate()
        self.__spacemap_scene.interface_objects = self.__planets

        self.__game.file_manager.reset()
        self.__game.file_manager.create_space_storage(self.__name)

    def get_spacemap_scene(self):
        return self.__spacemap_scene
