from map.level.rect.graph.manager import RectGraphManager
from utils.disjoint_set import DisjointSet
from utils.random import is_random_proc, shuffle


class RectConnecter:
    """
    делает проходы(двери) между прямоугольниками.

    :return:
    """

    def __init__(self, graph_manager: RectGraphManager):
        self.arr = graph_manager.arr

        self.edges = []
        graph_manager.save_edges_between_rects(self.edges)

        self.rects_count = graph_manager.rects_count

    def start_random_connection(self):
        """
        Проходится по всем ребрам в случайном порядке
        (ребро - 2 клетки граничащих прямоугольников).

        Если от одного прямоугольника до другого добраться нельзя,
        соединяет их, удаляя стену, между клетками ребра.
        Если можно, то соединяет с некоторой вероятностью.
        """
        shuffle(self.edges)
        self.dis_set = DisjointSet(self.rects_count)
        for i in range(len(self.edges)):
            edge = self.edges[i]
            if not self.dis_set.check(edge.color[0], edge.color[1]):
                self.dis_set.union(edge.color[0], edge.color[1])
                edge.delete(self.arr)
                continue

            CHANCE_EXTRA_CONNECTION = 1
            if is_random_proc(CHANCE_EXTRA_CONNECTION):
                edge.delete(self.arr)
