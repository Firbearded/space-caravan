from typing import List
import pygame
from drawable_objects.base import Humanoid
from geometry.point import Point
from geometry.vector import sign, length, normalized, polar_angle, get_min_vector
from geometry.rectangle import Rectangle
from geometry.distances import vector_dist_point_rect
from constants.directions import DIRECTIONS
from constants.mouse_buttons import MouseButtonID
from scenes.base import Scene
from controller.controller import Controller

from weapons.weapons import BurstFiringPistol, Shotgun, Pistol, AutomaticRifle

from utils.game_plane import GamePlane

class Player(Humanoid):
    """
    Игрок на уровне (далек от завершения).

    :param scene: сцена, на которой находится игрок
    :param controller: контроллер
    :param pos: начальная позиция игрока
    :param angle: начальный угол поворота игрока
    """

    ADD_TO_GAME_PLANE = True
    IMAGE_NAME = 'moving_objects.player'
    IMAGE_ZOOM = 0.25
    CONTROLS = [
        pygame.K_d,
        pygame.K_w,
        pygame.K_a,
        pygame.K_s,
    ]
    ARSENAL_CONTROLS = [
        pygame.K_1,
        pygame.K_2,
        pygame.K_3,
    ]
    WEAPON_RELOAD_KEY = pygame.K_r
    SPEED = 10

    def __init__(self, scene: Scene, controller: Controller, pos: Point, angle: float = 0):
        super().__init__(scene, controller, Player.IMAGE_NAME, pos, angle, Player.IMAGE_ZOOM)
        # head - 140x126
        self.rotation_offset = [
            140 * Player.IMAGE_ZOOM,
            126 * Player.IMAGE_ZOOM
        ]

        self.ammo = {
            'Pistol': 200,
            'Shotgun': 60,
            'Rifle': 100,
        }
        self.arsenal = [
            Shotgun(self),
            BurstFiringPistol(self),
            AutomaticRifle(self),
        ]
        self.arsenal_ind = 0
        self.weapon = self.arsenal[self.arsenal_ind]
        self.scene.game_objects.append(self.weapon)

    def process_logic(self):
        self._turn_to_mouse()
        self._movement_controls()
        self._weapon_controls()
        self.weapon.pos = self.pos
        self.weapon.angle = self.angle

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
        if self in self.controller.input_objects:
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
        if not self.controller.is_key_pressed(Player.ARSENAL_CONTROLS[self.arsenal_ind]):
            for ind in range(len(self.ARSENAL_CONTROLS)):
                if self.controller.is_key_pressed(Player.ARSENAL_CONTROLS[ind]):
                    self.change_arsenal_weapon(ind)

    def change_arsenal_weapon(self, ind):
        if self.weapon.type == 'Ranged':
            self.weapon.is_reloading = 0
            self.weapon.reload_request = False
        self.weapon.cooldown = 0
        self.arsenal[self.arsenal_ind] = self.weapon
        self.weapon.destroy()
        self.arsenal_ind = ind
        self.weapon = self.arsenal[ind]
        self.weapon.enabled = True
        self.scene.game_objects.append(self.weapon)
        self.weapon.cooldown = 20

    def _pos_after_pull_from_walls(self, player_pos: Point) -> Point:
        """
        Вытаскивание игрока из стен (каждый раз при попытке передвижения по команде
        пользователя позиция игрока корректируется: его вытаскивает из стен уровня).
        """
        result_pos = Point(player_pos.x, player_pos.y)
        walls_rects = self.scene.grid.get_collision_rects_nearby(player_pos)
        while True:
            vectors_from_bumps = self._get_vectors_from_bumps(result_pos, walls_rects)
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
