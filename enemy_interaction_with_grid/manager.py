from typing import List

from drawable_objects.enemy import Enemy
from enemy_interaction_with_grid.hearing.manager import EnemyHearingManager
from enemy_interaction_with_grid.vision.manager import EnemyVisionManager
from geometry.point import Point
from map.level.rect.splitter import GridRectangle


class GridInteractionWithEnemyManager:
    """
    Enemy обладает слухом и зрением.

    слух отвечает за поиск кратчайшего пути.
    зрение отвечает на запросы, видит ли enemy player'а
    """

    def __init__(self, rectangles: List[GridRectangle],
                 arr_after_split: List[List[int]],
                 grid):
        self.__hearing_manager = EnemyHearingManager(grid)
        self.__vision_manager = EnemyVisionManager(
            rectangles, arr_after_split, grid)

    def is_enemy_see_player(self, enemy: Enemy, radius: float) -> bool:
        """
        Видит ли enemy player'а

        :param enemy: враг
        :param radius: радиус, в котором player должен находиться
        :return: bool
        """
        return self.__vision_manager.is_enemy_see_player(enemy, radius)

    def save_enemy_pos(self, pos: Point):
        """
        отмечает, что на этой позиции есть enemy
        """
        self.__hearing_manager.save_enemy_pos(pos)

    def get_pos_to_move(self, enemy: Enemy) -> Point:
        """
        Получить следующую точку для движения.
        """
        return self.__hearing_manager.get_pos_to_move(enemy)

    def is_hearing_player(self, enemy: Enemy) -> bool:
        """
        Может ли услышать Enemy Player'а
        """
        return self.__hearing_manager.is_hearing_player(enemy)

    def is_enemy_can_stay(self, i: int, j: int) -> bool:
        """
        Может ли enemy стоять в клетке с индексами i, j
        """
        return self.__hearing_manager.can_stay(i, j)

    def process_logic(self):
        """
        логика менеджера
        """
        self.__hearing_manager.process_logic()
