from typing import Dict
from drawable_objects.enemy import Enemy
from enemy_interaction_with_grid.manager import GridInteractionWithEnemyManager
from geometry.point import Point
from map.collision_grid.collision_grid import CollisionGrid
from map.level.map_generator import LevelGenerator
from map.level.objects_generator import LevelObjectsGenerator
from map.level.rect.splitter import GridRectangle
from utils.game_data_manager import to_2dimensional_list_of_dicts, from_2dimensional_list_of_dicts
from utils.list import copy_2dimensional_list
from constants.grid import CELL_SIZE
from scenes.base import Scene
from controller.controller import Controller
from map.level.settings import level_settings


class LevelGrid(CollisionGrid):
    """
    Сетка уровня (данжа).
    """

    def to_dict(self):
        arr = []
        for i in range(len(self.arr)):
            arr.append([])
            for item in self.arr[i]:
                arr[i].append(self.__get_filename_index(item.image_name))

        arr_after_split = self.__arr_after_split
        room_rectangles = [item.to_dict() for item in self.__room_rectangles]
        return {
            'biom': self.biom,
            'pos': self.pos.to_dict(),
            'arr': arr,
            'arr_after_split': arr_after_split,
            'room_rectangles': room_rectangles,
            'classname': self.__class__.__name__
        }

    def from_dict(self, data_dict: Dict):
        """
        Воспроизведение объекта из словаря.
        """
        self.biom = data_dict['biom']

        new_pos = Point()
        new_pos.from_dict(data_dict['pos'])
        self.move(new_pos)

        self.arr = data_dict['arr']
        self._arr_initialize(CELL_SIZE, CELL_SIZE)
        self.transform_ints_to_objects()

        self.__arr_after_split = data_dict['arr_after_split']

        self.__room_rectangles = []
        for item in data_dict['room_rectangles']:
            res = GridRectangle((0, 0), (0, 0))
            res.from_dict(item)
            self.__room_rectangles.append(res)

        self._other_initialize()
        self._create_interaction_with_enemy_manager()

    def _get_filename(self, filename_index: int) -> str:
        filenames = level_settings[self.biom].level_filenames
        return filenames[filename_index]

    def __get_filename_index(self, filename_str: str) -> int:
        filenames = level_settings[self.biom].level_filenames
        return filenames.index(filename_str)

    def _create_interaction_with_enemy_manager(self):
        """
        Необходимо вызывать до enemy_generation.

        InteractionWithEnemyManager использует информацию из LevelGenerator
        (Он создает прямоугольники коллизий на основе комнат)
        """
        self.enemy_interaction_manager = GridInteractionWithEnemyManager(
            self.__room_rectangles, self.__arr_after_split, self)

    def enemy_generation(self):
        """
        Генерация врагов с помощью EnemyGenerator
        """
        self._create_interaction_with_enemy_manager()

        enemy_generator = LevelObjectsGenerator(self, self.__room_rectangles,
                        level_settings[self.biom].enemy_weapons,
                        level_settings[self.biom].chest_weapon_drop,
                        level_settings[self.biom].CHEST_OTHER_DROP,
                        level_settings[self.biom].CHEST_WEAPON_DROP_CHANCE,
                        level_settings[self.biom].enemy_img,
                        level_settings[self.biom].chest_imgs)
        enemy_generator.generate()

        """
        self.__arr_after_split, self.__room_rectangles нельзя удалять, т.к. их нужно хранить для
        удобного сохранения данных
        """

    def map_construction(self, min_area: int = 100, min_w: int = 8, min_h: int = 8):
        """
        Генерация уровня с помощью LevelGenerator
        """
        generator = LevelGenerator(self.arr, min_area, min_w, min_h)
        generator.generate()

        self.__room_rectangles = generator.rect_splitter.rectangles
        self.__arr_after_split = generator.arr_after_split

    def process_logic(self):
        """
        логика связана с взаимодействием grid'а и Enemy
        """
        self.enemy_interaction_manager.process_logic()

    def is_enemy_see_player(self, enemy: Enemy, radius: float) -> bool:
        """
        Видит ли enemy player'а

        :param enemy: враг
        :param radius: радиус, в котором player должен находиться
        :return: bool
        """
        return self.enemy_interaction_manager.is_enemy_see_player(enemy, radius)

    def save_enemy_pos(self, pos: Point):
        """
        Отмечает, что на этой позиции есть enemy. Нужно для path finding'а.
        """
        self.enemy_interaction_manager.save_enemy_pos(pos)

    def is_enemy_can_stay(self, i: int, j: int) -> bool:
        """
        Может ли в этой клетке стоять Enemy
        """
        return self.enemy_interaction_manager.is_enemy_can_stay(i, j)

    def get_pos_to_move(self, enemy: Enemy) -> Point:
        """
        получить точку для движения к игроку или None, если пройти нельзя (игрок слишком далеко или другие противники
        закрывают путь).
        """
        return self.enemy_interaction_manager.get_pos_to_move(enemy)

    def is_hearing_player(self, enemy: Enemy) -> bool:
        """
        Может ли услышать Enemy Player'а
        """
        return self.enemy_interaction_manager.is_hearing_player(enemy)


class DemoLevel(LevelGrid):
    def initialize(self):
        ARR_W = 75
        ARR_H = 50
        self._fill_arr(CELL_SIZE, CELL_SIZE, ARR_W, ARR_H)