from geometry.segment import Segment
from drawable_objects.enemy import Enemy
from geometry.vector import length

class EnemyVisionManager:
    def __init__(self, grid):
        self.grid = grid
        self.enemies = []

    def add_enemy(self, enemy: Enemy):
        enemy.is_see_player = False

        player_pos = self.grid.scene.player.pos
        dt = player_pos - enemy.pos
        if length(dt) <= Enemy.VISION_RADIUS:
            self.enemies.append(enemy)

    def process_logic(self):
        player_pos = self.grid.scene.player.pos
        for i in range(len(self.enemies)):
            seg = Segment(self.enemies[i].pos, player_pos)
            if self.grid.is_segment_intersect_walls(seg):
                continue
            self.enemies[i].is_see_player = True
        self.enemies = []