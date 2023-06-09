from map.collision_grid.collision_grid import CollisionGrid
from geometry.point import Point
from scenes.base import Scene
from controller.controller import Controller


class SpaceshipGrid(CollisionGrid):
    """
    Сетка космического корабля.
    """

    def __init__(self, scene: Scene, controller: Controller, pos: Point,
                 width: int = 100, height: int = 100,
                 top_left_corner_bias: int = 24):
        self.room_width = width
        self.room_height = height
        # Смещение от угла для однообразного управления
        self.top_left_corner_bias = top_left_corner_bias
        super().__init__(scene, controller, pos)
        self.initialize()

    def _get_filename(self, filename_index: int) -> str:
        FILENAMES = ['level.spaceship.empty', 'level.spaceship.floor']
        return FILENAMES[filename_index]

    def map_construction(self):
        width = self.top_left_corner_bias + self.room_width
        height = self.top_left_corner_bias + self.room_height
        for i in range(self.top_left_corner_bias, height):
            for j in range(self.top_left_corner_bias, width):
                self.arr[i][j] = 1
