from drawable_objects.usable_object import UsableObject
from geometry.point import Point

from scenes.base import Scene
from controller.controller import Controller


class Chest(UsableObject):
    """
        Класс сундука, с которой игрок может взаимодействовать,
        при взаимодействии - не реализовано
        """
    IMAGE_ZOOM = 1.5
    IMAGE_NAME ='level_objects.boxes.box'

    def __init__(self, scene: Scene, controller: Controller, pos: Point, angle: float = 0):
        super().__init__(scene, controller, Chest.IMAGE_NAME,
                         pos, angle, Chest.IMAGE_ZOOM)

    def activate(self):
        self.image_name ='level_objects.boxes.box_open'
        self.popping_e.destroy()
