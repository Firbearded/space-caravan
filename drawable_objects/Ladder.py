from drawable_objects.UsableObject import UsableObject
from geometry.point import Point

from scenes.base import Scene
from controller.controller import Controller


class Ladder(UsableObject):
    IMAGE_ZOOM = 0.8

    def __init__(self, scene: Scene, controller: Controller, pos: Point, angle: float = 0):
        super().__init__(scene, controller, 'level_objects.ladder',
                         pos, angle, Ladder.IMAGE_ZOOM)

    def activate(self):
        self.scene.game.set_scene(self.scene.game.SPACESHIP_SCENE_INDEX)
