import pygame

from typing import List, Dict

from drawable_objects.base import Humanoid
from geometry.point import Point
from geometry.vector import sign, length, normalized, polar_angle, get_min_vector
from geometry.rectangle import Rectangle
from geometry.distances import vector_dist_point_rect
from constants.directions import DIRECTIONS
from constants.mouse_buttons import MouseButtonID
from scenes.base import Scene
from controller.controller import Controller
from utils.sound import SoundManager

from weapons.weapons import WEAPON_VOCABULARY, weapon_to_dict
from drawable_objects.drop.chest_drop import WeaponDrop


class Player(Humanoid):
    """
    Игрок на уровне (далек от завершения).

    :param scene: сцена, на которой находится игрок
    :param controller: контроллер
    :param pos: начальная позиция игрока
    :param angle: начальный угол поворота игрока

    :IMAGE_NAME: путь до изображения персонажа
    :IMAGE_ZOOM: размер изображения
    :CONTROLS: клавиши управления движением
    :NUMBERIC_WEAPON_SLOTS_CONTROLS: клавиши управления слотами оружия
    :WEAPON_RELOAD_KEY: клавиша перезарядки
    :SPEED: скорость игрока
    """

    ADD_TO_GAME_PLANE = True
    IMAGE_NAME = 'moving_objects.player.range'
    IMAGE_ZOOM = 1.15
    HURT_SOUND = 'humanoid.hurt'
    DEATH_SOUND = 'humanoid.death'
    SLOT_SOUND = 'weapon.slot'
    CONTROLS = [
        pygame.K_d,
        pygame.K_w,
        pygame.K_a,
        pygame.K_s,
    ]
    NUMBERIC_WEAPON_SLOTS_CONTROLS = [
        pygame.K_1,
        pygame.K_2,
    ]
    TAB_WEAPON_SLOTS_CONTROLS = pygame.K_TAB
    WEAPON_RELOAD_KEY = pygame.K_r
    SPEED = 10
    MAXHP = 300

    DATA_FILENAME = 'player'

    def __init__(self, scene: Scene, controller: Controller, pos: Point, angle: float = 0):
        super().__init__(scene, controller, Player.IMAGE_NAME, pos, angle, Player.IMAGE_ZOOM)
        # head - 140x126
        #self.rotation_offset = [
        #    140 * Player.IMAGE_ZOOM,
        #    126 * Player.IMAGE_ZOOM
        #]
        self.ammo = {
            'Pistol': 200,
            'Shotgun': 60,
            'Rifle': 100,
        }
        self.weapon_slots = [
            WEAPON_VOCABULARY['Fist'](self),
            WEAPON_VOCABULARY['Fist'](self),
        ]
        self.weapon_slots_ind = 0
        self.change_weapon_request = -1
        self.change_weapon_cooldown = 0
        self.weapon = self.weapon_slots[self.weapon_slots_ind]
        self.is_clone = False
        self.is_dead = False

    def set_weapon(self, weapon_dict: Dict):
        """
        Присвоить на место оружия на текущем слоте weapon
        """
        weapon = WEAPON_VOCABULARY[weapon_dict['weapon']](self)
        if weapon.type == 'Ranged':
            weapon.magazine = weapon_dict['magazine']

        self.weapon_slots[self.weapon_slots_ind] = weapon
        self.weapon = self.weapon_slots[self.weapon_slots_ind]

    def from_dict(self, data_dict: Dict):
        super().from_dict(data_dict)

        self.ammo = data_dict['ammo']
        self.weapon_slots_ind = data_dict['weapon_slots_ind']

        self.weapon_slots = []
        for weapon_dict in data_dict['weapons']:
            weapon = WEAPON_VOCABULARY[weapon_dict['weapon']](self)
            if weapon.type == 'Ranged':
                weapon.magazine = weapon_dict['magazine']
            self.weapon_slots.append(weapon)

        self.weapon = self.weapon_slots[self.weapon_slots_ind]

        self.is_clone = data_dict['is_clone']
        self.is_dead = data_dict['is_dead']

    def to_dict(self) -> Dict:
        result = super().to_dict()

        weapons = []
        for item in self.weapon_slots:
            weapon_dict = weapon_to_dict(item)
            weapons.append(weapon_dict)

        result.update({'weapons': weapons})

        result.update({'weapon_slots_ind': self.weapon_slots_ind})
        result.update({'ammo': self.ammo})

        result.update({'is_clone': self.is_clone})
        result.update({'is_dead': self.is_dead})

        return result

    def load(self):
        """
        Загрузка игрока из файла. Игрок хранится отдельно от сцен, потому что должен уметь подгружаться на
        любую игровую сцену.
        """
        self.from_dict(
            self.scene.game.file_manager.read_data(self.DATA_FILENAME))

    def save(self):
        """
        Сохранение игрока в файл.
        """
        self.scene.game.file_manager.write_data(
            self.DATA_FILENAME, self.to_dict())

    def process_logic(self):
        self._movement_controls()
        self.scene.update_relative_center()
        self._turn_to_mouse()
        self._weapon_controls()
        self.weapon.process_logic()
        self.sprite_manager()

    @property
    def is_fired_this_tick(self):
        """
        выстрелил ли Player в этот тик process_logic
        """
        return self.weapon.is_fired_this_tick

    def _turn_to_mouse(self):
        """
        Высичление позиции в относительных координатах и поворот к мыши (которая по умолчанию
        в относительных координатах).
        """
        relative_center = self.scene.relative_center
        relative_pos = self.pos - relative_center
        vector_to_mouse = self.controller.get_mouse_pos() - relative_pos
        self.angle = polar_angle(vector_to_mouse)

    def _movement_controls(self):
        """
        Передвижение игрока по команде пользователя.
        """
        velocity = Point()
        for i in range(4):
            if self.controller.is_key_pressed(Player.CONTROLS[i]):
                velocity += DIRECTIONS[i]
        velocity *= self.SPEED
        new_player_pos = self._pos_after_pull_from_walls(self.pos + velocity)
        self.move(new_player_pos)

    def _weapon_controls(self):
        """
        Управление оружием игрока по команде пользователя
        """
        is_attacking = self.weapon.is_automatic and self.controller.is_mouse_pressed(MouseButtonID.LEFT)
        button = self.controller.get_click_button()
        if (button == MouseButtonID.LEFT or is_attacking) and self.weapon.cooldown == 0:
            self.weapon.main_attack()
        if button == MouseButtonID.RIGHT:
            self.weapon.alternative_attack()
        if self.controller.is_key_pressed(Player.WEAPON_RELOAD_KEY):
            self.weapon.reload_request = True
        if self.change_weapon_cooldown != 0:
            self.change_weapon_cooldown -= 1
        else:
            if self.change_weapon_request == -1:
                if not self.controller.is_key_pressed(Player.NUMBERIC_WEAPON_SLOTS_CONTROLS[self.weapon_slots_ind]):
                    for ind in range(len(self.NUMBERIC_WEAPON_SLOTS_CONTROLS)):
                        if self.controller.is_key_pressed(Player.NUMBERIC_WEAPON_SLOTS_CONTROLS[ind]):
                            SoundManager.play_sound(Player.SLOT_SOUND)
                            self.change_weapon_request = ind
                if self.controller.is_key_pressed(Player.TAB_WEAPON_SLOTS_CONTROLS):
                    SoundManager.play_sound(Player.SLOT_SOUND)
                    self.change_weapon_request = 1 + self.weapon_slots_ind == 1
        if self.change_weapon_request != -1 and self.weapon.combo == 0:
            self.change_weapon(self.change_weapon_request)
            self.change_weapon_cooldown = 20
            self.change_weapon_request = -1

    def change_weapon(self, ind):
        if self.weapon.type == 'Ranged':
            self.weapon.is_reloading = 0
            self.weapon.reload_request = False
        self.weapon.cooldown = 0
        self.weapon_slots[self.weapon_slots_ind] = self.weapon
        self.weapon_slots_ind = ind
        self.weapon = self.weapon_slots[ind]
        self.weapon.cooldown = 15

    def sprite_manager(self):
        if self.weapon.__class__.__name__ == 'Pistol' or self.weapon.__class__.__name__ == 'BurstFiringPistol':
            self.image_name = 'moving_objects.player.pistol'
        elif self.weapon.__class__.__name__ == 'Fist':
            if self.image_name != 'moving_objects.player.punch':
                self.image_name = 'moving_objects.player.barehanded'
        elif self.weapon.__class__.__name__ == 'Knife':
            if self.image_name != 'moving_objects.player.knife1' and self.image_name != 'moving_objects.player.knife2':
                self.image_name = 'moving_objects.player.knife'
        else:
            self.image_name = 'moving_objects.player.range'

    def _pos_after_pull_from_walls(self, player_pos: Point) -> Point:
        """
        Вытаскивание игрока из стен (каждый раз при попытке передвижения по команде
        пользователя позиция игрока корректируется: его вытаскивает из стен уровня).
        """
        result_pos = Point(player_pos.x, player_pos.y)
        walls_rects = self.scene.grid.get_collision_rects_nearby(player_pos)
        while True:
            vectors_from_bumps = self._get_vectors_from_bumps(
                result_pos, walls_rects)
            if len(vectors_from_bumps) == 0:
                break
            min_vector = get_min_vector(vectors_from_bumps)
            push_vector = self._get_push_vector(min_vector)
            result_pos += push_vector
        return result_pos

    def _get_push_vector(self, vector_from_bump: Point) -> Point:
        """
        По вектору от соударения со стеной получить вектор выталкивания, на который
        надо сместить игрока, чтобы он из этой стены вышел.
        """
        length_delta = self.HITBOX_RADIUS - length(vector_from_bump)
        direction_vector = normalized(vector_from_bump)
        return direction_vector * length_delta

    def _get_vectors_from_bumps(self, player_pos: Point, walls_rects: List[Rectangle]) -> List[Point]:
        """
        Формирует список векторов от соударений игрока с прямоугольниками стен до центра игрока
        (точкой соударения считается ближайшая к центру игрока точка прямоугольника).
        """
        vectors_from_bumps = []
        for rect in walls_rects:
            vector_from_rect = vector_dist_point_rect(player_pos, rect)
            if sign(self.HITBOX_RADIUS - length(vector_from_rect)) == 1:
                vectors_from_bumps.append(vector_from_rect)
        return vectors_from_bumps

    def die(self, angle_of_attack=0):
        """
        Смерть. При гибели клона включается сцена гибели клона. При гибели игрока космос отмечается проигранным
        для последующего удаления и включается сцена конца игры.

        :param angle_of_attack: угол, под которым Enemy ударили(для анимаций)
        """
        SoundManager.play_sound(Player.DEATH_SOUND)
        if self.is_clone:
            self.is_dead = True

            for item in self.weapon_slots:
                weapon_dict = weapon_to_dict(item)
                if weapon_dict['weapon'] == 'Fist': #кулак не нужно дропать
                    continue
                drop = WeaponDrop(self.scene, self.controller, self.pos)
                drop.set_weapon_dict(weapon_dict)
                self.scene.game_objects.append(drop)

            self.scene.game.set_scene_with_index(self.scene.game.CLONE_KILLED_SCENE_INDEX)
        else:
            self.scene.game.set_current_space_lost()
            self.scene.game.set_scene_with_index(self.scene.game.GAMEOVER_SCENE_INDEX)
