"""
Основа для создания сцен меню
"""

from drawable_objects.menu.widget_group import WidgetGroup
from scenes.conservable import ConservableScene


class MenuScene(ConservableScene):
    """
    Базовый класс для сцены меню

    :param game: игра, создающая сцену
    """
    DATA_FILENAME = None

    def __init__(self, game):
        super().__init__(game, self.DATA_FILENAME)
        self.menu = WidgetGroup(self, self.game.controller, [0.5, 0.3], 6)
        self.interface_objects.append(self.menu)
