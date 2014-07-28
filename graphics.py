import math
import random

import utils as u


class MyCanvas:

    def __init__(self, canvas):
        self.canvas = canvas

    def draw_point(self, point):
        radius = 1
        self.draw_circle(point, radius, fill=True)
        # self.canvas.create_text(point.x + radius, point.y - radius,
        #                         anchor=tk.SW, text=point.id)

    def draw_line(self, source, dest):
        self.canvas.create_line(source.x, source.y,
                                dest.x, dest.y)

    def draw_edge(self, edge):
        self.draw_line(edge.p1, edge.p2)

    def draw_circle(self, center, radius, fill=False):
        self.canvas.create_oval(
            center.x - radius, center.y - radius,
            center.x + radius, center.y + radius,
            fill=("black" if fill else None))

    def draw_triangle(self, triangle):
        for edge in triangle.edges():
            self.draw_edge(edge)

    def draw_polygon(self, poly):
        last_point = poly.points[0]
        for point in poly.points[1:] + [last_point]:
            self.draw_line(last_point, point)
            last_point = point


class Point(u.SimpleEq):

    def __init__(self, x, y, id=None):
        if id is None:
            id = "?"
        self.x = x
        self.y = y
        self.id = id

    def add(self, point, factor=1, id=None):
        return Point(
            self.x + factor * point.x,
            self.y + factor * point.y,
            id)

    def dist2(self, point):
        dx = self.x - point.x
        dy = self.y - point.y
        return dx**2 + dy**2

    def __repr__(self):
        return "[{} ({:.0f},{:.0f})]".format(
            self.id,
            self.x,
            self.y)

    def __hash__(self):
        return(hash((self.x, self.y, self.id)))


class Edge(u.SimpleEq):

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def points(self):
        return [self.p1, self.p2]

    def __repr__(self):
        return "[eg {}{}]".format(self.p1, self.p2)

    def __eq__(self, other):
        if type(other) is type(self):
            return ((self.p1 == other.p1 and self.p2 == other.p2) or
                    (self.p1 == other.p2 and self.p2 == other.p1))
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.p1) ^ hash(self.p2)


class Triangle:

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        self.calc_center()
        self.calc_maps()

    def calc_center(self):
        bp = self.b.add(self.a, -1)
        cp = self.c.add(self.a, -1)

        denom = 2 * (bp.x*cp.y - bp.y*cp.x)

        bs = bp.x*bp.x + bp.y*bp.y
        cs = cp.x*cp.x + cp.y*cp.y

        xx = cp.y*bs - bp.y*cs
        yy = bp.x*cs - cp.x*bs

        self.center = self.a.add(Point(xx / denom, yy / denom))

        self.radius2 = (xx**2 + yy**2) / (denom**2)
        self.radius = math.sqrt(self.radius2)

    def calc_maps(self):
        edge_ab = Edge(self.a, self.b)
        edge_bc = Edge(self.b, self.c)
        edge_ca = Edge(self.c, self.a)

        self.edge_map = {edge_ab: self.c,
                         edge_bc: self.a,
                         edge_ca: self.b}

        self.point_map = {self.c: edge_ab,
                          self.a: edge_bc,
                          self.b: edge_ca}

    def contains(self, p):
        denom = (self.b.y - self.c.y)*(self.a.x - self.c.x) + \
                (self.c.x - self.b.x)*(self.a.y - self.c.y)
        s = ((self.b.y - self.c.y)*(p.x - self.c.x) +
             (self.c.x - self.b.x)*(p.y - self.c.y)) / denom
        t = ((self.c.y - self.a.y)*(p.x - self.c.x) +
             (self.a.x - self.c.x)*(p.y - self.c.y)) / denom
        r = 1 - s - t
        return all((0 <= s, s <= 1, 0 <= t,
                    t <= 1, 0 <= r, r <= 1))

    def circum_contains(self, p):
        return self.center.dist2(p) <= self.radius2

    def points(self):
        return [self.a, self.b, self.c]

    def edges(self):
        return self.edge_map.keys()

    def edge_antipoint(self, edge):
        return self.edge_map[edge]

    def point_antiedge(self, point):
        return self.point_map[point]

    def __repr__(self):
        return "[tr {}{}{}]".format(self.a, self.b, self.c)


class Polygon:

    def __init__(self, *points):
        self.points = list(points)

    def area(self):
        return sum([(p.x*pp.y - pp.x*p.y) for (p, pp) in
                    zip(self.points, self.points[1:] + self.points[0:1])]) / 2

    def centroid(self):
        area = self.area()
        cx = sum([(p.x + pp.x)*(p.x*pp.y - pp.x*p.y) for (p, pp) in
                  zip(self.points, self.points[1:] + self.points[0:1])])
        cy = sum([(p.y + pp.y)*(p.x*pp.y - pp.x*p.y) for (p, pp) in
                  zip(self.points, self.points[1:] + self.points[0:1])])
        return Point(cx / (6 * area), cy / (6 * area))

    def __repr__(self):
        return "[pl {}]".format(self.points)


def generate_points(count, xrange, yrange):
    print("Generating", count, "points")

    def random_point(idx):
        return Point(
            random.uniform(xrange[0], xrange[1]),
            random.uniform(yrange[0], yrange[1]),
            "p{}".format(idx))

    return [random_point(idx + 1) for idx in range(count)]
