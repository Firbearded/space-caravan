from geometry.point import Point
from geometry.vector import cross_product, dot_product, sign


class Segment:
    def __init__(self, p1: Point = Point(), p2: Point = Point()):
        self.p1 = Point(p1.x, p1.y)
        self.p2 = Point(p2.x, p2.y)


def point_on_segment(p: Point, seg: Segment) -> bool:
    if sign(cross_product(p - seg.p1, seg.p2 - seg.p1)) != 0:
        return False
    return sign(dot_product(p - seg.p1, seg.p2 - seg.p1)) >= 0 and sign(dot_product(p - seg.p2, seg.p1 - seg.p2)) >= 0