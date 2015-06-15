import math
import random

import graphics as gr
import utils as u


def fill(ranges, exp, rotation, iters, shape_maker):
    riem = sum(i ** (-exp) for i in range(1, 1000000))
    total_area = (ranges[0][1] - ranges[0][0]) * (ranges[1][1] - ranges[1][0])
    initial_area = total_area / riem
    initial_size = math.sqrt(initial_area / shape_maker(gr.Point(0, 0), 1).area)

    progress = u.make_progressbar(iters, timeit=True)

    rad_rotation = rotation * math.pi / 180

    shapes = []
    for i in range(1, iters+1):
        size = initial_size * (i ** (-exp / 2))
        while True:
            center = gr.Point(random.uniform(*ranges[0]),
                              random.uniform(*ranges[1]))
            shape = shape_maker(center, size)
            if rotation > 0:
                units = random.randint(0, (360-1)//rotation)
                if units:
                    shape = shape.rotate(rad_rotation*units)
            if all(not shape.intersects(sh) for sh in shapes):
                shapes.append(shape)
                progress()
                break

    return shapes


class Polygon(gr.Polygon):
    @u.lazy_property
    def bounding_box(self):
        min_x = min(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_x = max(p.x for p in self.points)
        max_y = max(p.y for p in self.points)
        return min_x, min_y, max_x, max_y

    def bound_intersects(self, other):
        x2, y2, a2, b2 = self.bounding_box
        x1, y1, a1, b1 = other.bounding_box
        return a2>=x1 and a1>=x2 and b2>=y1 and b1>=y2

    def intersects(self, other):
        if not self.bound_intersects(other):
            return False
        return any (other.contains(p) for p in self.points) or \
               any (self.contains(p) for p in other.points) or \
               any (line_intersects(e1, e2) for e1 in self.point_edges() for e2 in other.point_edges())


class Circle(gr.Circle):
    def rotate(self, angle):
        return self

#
# Shape factories
#

circle_maker = lambda: Circle


def poly_maker(*points):
    poly = Polygon(*(gr.Point(*xy) for xy in points))
    def shape_maker(center, size):
        scaled_poly = poly.scale(size)
        return scaled_poly.translate(center.add(scaled_poly.centroid, factor=-1))
    return shape_maker

#
# Utils
#

#
# see: http://stackoverflow.com/a/9997374
#
def ccw(a, b, c):
    return (c.y - a.y)*(b.x - a.x) > (b.y - a.y)*(c.x - a.x)

def line_intersects(l1, l2):
    a, b = l1
    c, d = l2
    return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)
