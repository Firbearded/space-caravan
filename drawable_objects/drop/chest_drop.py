from typing import Dict
from drawable_objects.usable_object import UsableObject
from controller.controller import Controller
from geometry.point import Point
from weapons.weapons import WEAPON_VOCABULARY, weapon_to_dict


class WeaponDrop(UsableObject):
    def __init__(self, scene, controller: Controller,
                 pos: Point, angle: float = 0, zoom: float = 0.5, usage_radius: float = 75):
        super().__init__(scene, controller, WEAPON_VOCABULARY['Sword'].IMAGE_NAME,
                         pos, angle, zoom, usage_radius)
    # напиши нормальный get_image
    def activate(self):
        old_weapon = weapon_to_dict(self.scene.player.weapon)
        self.scene.player.set_weapon(self.__weapon_dict)
        self.enabled = False

        new_weapon = WeaponDrop(self.scene, self.controller,
                            self.pos, self.angle, self.zoom, self.usage_radius)
        new_weapon.set_weapon_dict(old_weapon)
        self.scene.game_objects.append(new_weapon)

    def set_weapon_dict(self, weapon_dict: Dict):
        self.__weapon_dict = weapon_dict
        self.image_name = WEAPON_VOCABULARY[self.__weapon_dict['weapon']].IMAGE_NAME

    def to_dict(self) -> Dict:
        result = super().to_dict()
        result.update(self.__weapon_dict)
        return result

    def from_dict(self, data_dict: Dict):
        super().from_dict(data_dict)

        weapon_dict = {'weapon': data_dict['weapon']}
        if 'magazine' in data_dict:
            weapon_dict.update({'magazine': data_dict['magazine']})

        self.set_weapon_dict(weapon_dict)


def create_drop(name: str, scene, controller: Controller, pos: Point) -> UsableObject:
    """
    создать новый дроп по названию name
    """
    if name in WEAPON_VOCABULARY:
        tmp_weapon = WEAPON_VOCABULARY[name](scene.player)
        res = WeaponDrop(scene, controller, pos)
        res.set_weapon_dict(weapon_to_dict(tmp_weapon))
        return res

    raise Exception('Drop does not exist')
