from controller.controller import Controller
from drawable_objects.drop.base import Drop
from geometry.point import Point
from random import randint

from utils.sound import SoundManager


class AmmoDrop(Drop):
    IMAGE_NAME = 'drop.ammo'
    ACTIVATION_SOUND = 'usable.pickup'

    def __init__(self, scene, controller: Controller,
                 pos: Point, angle: float = 0, zoom: float = 1.15, usage_radius: float = 42):
        super().__init__(scene, controller, pos, angle, zoom, usage_radius)

    def process_logic(self):
        self._update_player_nearby()
        if self.player_nearby:
            self.activate()
            self.destroy()

    def activate(self):
        SoundManager.play_sound(AmmoDrop.ACTIVATION_SOUND)
        MINIMUM_AMMO = 1
        MAXIMUM_AMMO = 5
        ammo_cnt = randint(MINIMUM_AMMO, MAXIMUM_AMMO)
        for key in self.scene.player.ammo:
            self.scene.player.ammo[key] += ammo_cnt
