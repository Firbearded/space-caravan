from collections import deque

from constants.directions import side_di, side_dj
from geometry.point import Point
from geometry.intersections import intersect_seg_rect
from geometry.segment import Segment
from map.level.grid_interaction_with_enemy.grid_path_finder import IsMarkedManager


class GridIntersectionManager:
    def __init__(self, grid):
        self.grid = grid
        self.used_manager = IsMarkedManager(grid.arr)

    def intersect_seg_walls(self, seg: Segment) -> Point:
        self.used_manager.next_iteration()
        i0, j0 = self.grid.index_manager.get_index_by_pos(seg.p1)

        s = deque()
        self.used_manager.mark(i0, j0)
        s.append((i0, j0))

        while (len(s)):
            i, j = s.popleft()
            for k in range(len(side_di)):
                new_i = i + side_di[k]
                new_j = j + side_dj[k]
                if self.used_manager.is_marked(new_i, new_j):
                    continue

                rect = self.grid.get_collision_rect(new_i, new_j)
                interset_point = intersect_seg_rect(seg, rect)
                if interset_point is None:
                    continue

                if not self.grid.is_passable(new_i, new_j):
                    return interset_point

                self.used_manager.mark(new_i, new_j)
                s.append((new_i, new_j))

        return None

