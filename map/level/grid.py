from typing import List, Tuple

from controller.controller import Controller
from drawable_objects.base import GameSprite
from drawable_objects.enemy import Enemy
from geometry.point import Point
from geometry.rectangle import Rectangle, create_rectangle_with_left_top
from geometry.segment import Segment
from map.grid import Grid
from map.level.generator import LevelGenerator
from map.level.grid_interaction_with_enemy.grid_interaction_with_enemy_manager import GridInteractionWithEnemyManager
from map.level.grid_static_draw_manager import GridStaticDrawManager
from scenes.base import Scene
from map.level.intersection import GridIntersectionManager

class LevelGrid(Grid):
    """
    Сетка уровня (данжа).
    Представляет собой двумерный список объектов,
    либо стена, либо пол.
    Все они статические (не меняются со временем).

    Генерируется с помощью LevelGenerator, далее преобразует
    инты в объекты.
    """
    def __init__(self, scene: Scene, controller: Controller, pos: Point,
                 cell_width: int, cell_height: int,
                 width: int = 100, height: int = 100,
                 min_area: int = 100, min_w: int = 8, min_h: int = 8):
        super().__init__(scene, controller, pos, 0, cell_width, cell_height, width, height)

        generator = LevelGenerator(self.arr, min_area, min_w, min_h)
        generator.generate()

        self.transform_ints_to_objects()
        self.static_draw_manager = GridStaticDrawManager(self)
        self.grid_intersection_manager = GridIntersectionManager(self)
        self.path_manager = GridInteractionWithEnemyManager(self)

    def process_draw(self):
        self.static_draw_manager.process_draw()

    def process_logic(self):
        self.path_manager.process_logic()

    def transform_ints_to_objects(self):
        """
        Необходимо применять после генерации.
        """
        for i in range(len(self.arr)):
            for j in range(len(self.arr[i])):
                pos_x = self.pos.x + j * self.cell_width + self.cell_width / 2
                pos_y = self.pos.y + i * self.cell_height + self.cell_height / 2
                filenames = ['wall', 'floor']
                filename_index = int(bool(self.arr[i][j]))

                self.arr[i][j] = GameSprite(self.scene, self.controller,
                           filenames[filename_index], Point(pos_x, pos_y))

    def is_passable(self, i: int, j: int) -> bool:
        return self.arr[i][j].image_name != 'wall'

    def get_collision_rect(self, i: int, j: int) -> Rectangle:
        h = self.cell_height
        w = self.cell_width
        y = i * h
        x = j * w
        return create_rectangle_with_left_top(Point(x, y) + self.pos, w, h)

    def get_collision_rects_nearby(self, pos: Point) -> List[Rectangle]:
        """
        Возвращает все прямоугольники коллизий статических объектов (стен)
        в квадрате длиной (1 + INDEX_OFFSET * 2) с центром в клетке,
        соответствующей координате pos.
        :param pos:
        :return:
        """
        center_i, center_j = self.index_manager.get_index_by_pos(pos)
        INDEX_OFFSET = 2

        min_i = max(0, center_i - INDEX_OFFSET)
        min_j = max(0, center_j - INDEX_OFFSET)
        max_i = min(len(self.arr), center_i + INDEX_OFFSET + 1)
        max_j = min(len(self.arr[0]), center_j + INDEX_OFFSET + 1)

        res = []
        for i in range(min_i, max_i):
            for j in range(min_j, max_j):
                if not self.is_passable(i, j):
                    res.append(self.get_collision_rect(i, j))
        return res

    def set_enemy_in_arr(self, enemy: Enemy):
        self.path_manager.set_enemy_in_arr(enemy)

    def get_pos_to_move(self, enemy: Enemy) -> Point:
        return self.path_manager.grid_path_finder.get_pos_to_move(enemy)

    def is_segment_intersect_walls(self, seg: Segment) -> bool:
        return self.grid_intersection_manager.is_segment_intersect_walls(seg)
