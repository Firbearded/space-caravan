import sys
import pygame
import gc

from typing import Tuple

from controller.controller import Controller
from geometry.rectangle import Rectangle
from scenes.base import Scene
from scenes.game.base import GameScene
from scenes.game.level import LevelScene
from scenes.menu.about import AboutMenuScene
from scenes.menu.main import MainMenuScene
from scenes.menu.settings import SettingsMenuScene
from scenes.menu.space_choice import SpaceChoiceMenuScene
from scenes.menu.redirecting.gameover import GameoverScene
from scenes.menu.redirecting.clone_killed import CloneKilledScene
from scenes.menu.redirecting.victory import VictoryScene
from utils.image import ImageManager
from utils.game_data_manager import GameDataManager
from utils.sound import SoundManager


class Game:
    """
    Класс игры в смысле приложения. Содержит главный рабочий цикл; организует отрисовку графического окна;
    как поля имеет контроллер ввода и менеджеры картинок, звука, файлов игры; руководит работой сцен.
    """

    MAIN_MENU_SCENE_INDEX = 0
    SETTINGS_MENU_SCENE_INDEX = 1
    ABOUT_MENU_SCENE_INDEX = 2
    SPACE_CHOICE_MENU_SCENE_INDEX = 3
    GAMEOVER_SCENE_INDEX = 4
    CLONE_KILLED_SCENE_INDEX = 5
    VICTORY_SCENE_INDEX = 6
    TITLE = 'Space Caravan'

    def __init__(self, width: int = 1000, height: int = 700):
        pygame.mixer.init(22100, -16, 2, 64)  # removes sound delay
        pygame.init()
        pygame.display.set_caption(Game.TITLE)
        self.size = (width, height)
        self.__running = True
        ImageManager.load_all()
        pygame.display.set_icon(ImageManager.get_image('other.icon'))
        SoundManager.load_all()
        SoundManager.configure_volume()
        self.__file_manager = GameDataManager()

        self.__controller = Controller(self)
        self.__scenes_classes = [
            MainMenuScene,
            SettingsMenuScene,
            AboutMenuScene,
            SpaceChoiceMenuScene,
            GameoverScene,
            CloneKilledScene,
            VictoryScene,
        ]
        self.__current_scene = None
        self.set_scene_with_index(0)
        self.__scenes_to_delete = list()
        self.__lost_spaces = list()

    @property
    def size(self) -> Tuple[int, int]:
        return self.__size

    @size.setter
    def size(self, value: Tuple[int, int]):
        """
        Присвоением окну размера инициализируются все характеристики экрана.
        """
        self.__size = value
        self.__width = self.__size[0]
        self.__height = self.__size[1]
        self.__screen_rectangle = Rectangle(0, 0, self.__width, self.__height)
        self.__create_window()

    def __create_window(self):
        self.__screen = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

    @property
    def screen(self) -> pygame.Surface:
        return self.__screen

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def screen_rectangle(self) -> Rectangle:
        return self.__screen_rectangle

    @property
    def controller(self) -> Controller:
        return self.__controller

    @property
    def file_manager(self) -> GameDataManager:
        return self.__file_manager

    def set_scene(self, scene: Scene):
        """
        Установка заданной сцены текущей. Старая сцена может быть None; если она не None, она сохраняется. Если
        старая сцена игровая, она отправляется на удаление. Далее новой сцене подгружается игрок и объект с общими
        данными игры, если необходимо. После вызывается конструирование новой сцены и обновляется __current_scene.

        :param scene: ссылка на новую сцену
        """
        if self.__current_scene:
            self.__current_scene.save()
        if isinstance(self.__current_scene, GameScene):
            self.__scenes_to_delete.append(self.__current_scene)
        if isinstance(scene, GameScene):
            scene.load_common_data()
        if isinstance(scene, LevelScene):
            scene.load_player()
        scene.construct()
        self.__current_scene = scene

    def set_scene_with_index(self, scene_index: int):
        """
        Установка сцены из имеющегося списка в качестве текущей. Индексы в списке - константные поля класса игры.
        """
        scene = self.__scenes_classes[scene_index](self)
        self.set_scene(scene)

    def set_current_space_lost(self):
        """
        Установка текущего космоса проигранным для дальшейшего удаления.
        """
        self.__lost_spaces.append(self.file_manager.space_name)

    def end(self):
        self.__running = False

    def __delete_garbage_scenes(self):
        """
        Как такового удаления не происходит, вызывается подчистка сборщиком мусора python'а.
        """
        if len(self.__scenes_to_delete):
            self.__scenes_to_delete.clear()
            gc.collect()

    def __delete_lost_spaces(self):
        """
        Удаление проигранных космосов.
        """
        for space_name in self.__lost_spaces:
            self.file_manager.space_name = space_name
            self.file_manager.delete_space_storage()
        self.__lost_spaces.clear()

    def main_loop(self):
        """
        Главный рабочий цикл.
        """
        while self.__running:
            self.__controller.iteration()
            self.__current_scene.iteration()
            self.__delete_lost_spaces()
            self.__delete_garbage_scenes()
        sys.exit(0)
