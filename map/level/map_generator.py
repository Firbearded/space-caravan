from typing import List

from map.level.rect.connecter import RectConnecter
from map.level.rect.graph.manager import RectGraphManager
from map.level.rect.splitter import RectSplitter
from map.level.rect.unioner import RectUnioner


class LevelGenerator:
    """
    Принимает arr. Далее заполняет его числами.
    Если ноль, то стена. Иначе пол.
    Разные числа означают границы разных фигур.

    Результат генерации - заполнение исходного прямоугольника фигурами
    с углами 270 и 90 градусов.
    """

    def __init__(self, arr: List[List[int]],
                 min_area: int = 100, min_w: int = 8, min_h: int = 8):
        self.arr = arr

        self.rect_splitter = RectSplitter(self.arr, min_area, min_w, min_h)

    def generate(self):
        """
        Прямоугольник разбивается на много прямоугольников.

        Далее некоторые из них объединяются (для получения фигур помимо прямоугольников).

        После проводятся ребра (двери) между полученными фигурами.

        Граф связный, но не обязательно является деревом.
        """
        self.__split()

        self.__union()

        self.__connect()

    def __split(self):
        """
        Разбить сетку на прямоугольники
        """
        self.rect_splitter.start_random_split()

        # Необходимо сохранить список для дальнейших нужд:
        self.arr_after_split = self.rect_splitter.get_arr_after_split()

        self.graph_manager = RectGraphManager(
            self.rect_splitter.arr, self.rect_splitter.rects_colors_count)

    def __union(self):
        """
        Объединить некоторые прямоугольники
        """
        self.rect_unioner = RectUnioner(self.graph_manager)
        self.rect_unioner.start_random_union()
        self.rect_unioner.delete_edges()

    def __connect(self):
        """
        Добавить проходы
        """
        self.rect_connecter = RectConnecter(self.graph_manager)
        self.rect_connecter.start_random_connection()
