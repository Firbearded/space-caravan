from constants import Color
from drawable_objects.player import Player
from scenes.base import Scene
from geometry.point import Point

from map.level.grid import LevelGrid

class MainScene(Scene):

    def create_objects(self):
        self.player = Player(self, self.game.controller, Point(0, 0), 0)
        self.grid = LevelGrid(self, self.game.controller, Point(0, 0), 25, 25)
        self.game_objects = [self.grid]

    def additional_logic(self):
        self.relative_center = self.player.next_step_pos - self.game.center
        self.player.process_logic()

    def additional_draw(self):
        self.player.process_draw()
