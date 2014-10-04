import math
import svgwrite

import utils as u


class MyCanvas(u.Deferrable):

    def __init__(self, canvas=None):
        super().__init__()
        self.canvas = canvas

    @u.deferred
    def draw_point(self, point):
        radius = 1
        self.draw_circle(point, radius, fill=True)
        # self.canvas.create_text(point.x + radius, point.y - radius,
        #                         anchor=tk.SW, text=point.id)

    @u.deferred
    def draw_line(self, source, dest):
        self.canvas.create_line(source.x, source.y,
                                dest.x, dest.y)

    @u.deferred
    def draw_edge(self, edge):
        self.draw_line(edge.p1, edge.p2)

    @u.deferred
    def draw_circle(self, center, radius, fill=False):
        self.canvas.create_oval(
            center.x - radius, center.y - radius,
            center.x + radius, center.y + radius,
            fill=("black" if fill else None))

    @u.deferred
    def draw_triangle(self, triangle):
        for edge in triangle.edges():
            self.draw_edge(edge)

    @u.deferred
    def draw_polygon(self, poly, fill=None, outline=None):
        self.canvas.create_polygon(list(map(lambda point: (point.x, point.y), poly.points)),
                                   fill=fill, outline=outline)


class SvgCanvas:

    def __init__(self, name):
        self.dwg = svgwrite.Drawing(name, profile='tiny')
        self.gradient_ids = 0

    def draw_polygon(self, poly, **opts):
        def make_command(type, point):
            return "{} {} {}".format(type, point.x, point.y)
        scommands = [make_command('M', poly.points[0])] + \
                    [make_command('L', point) for point in poly.points[1:]] + \
                    ['z']
        self.dwg.add(self.dwg.path(scommands, **opts))

    def draw_point(self, point, **opts):
        self.dwg.add(self.dwg.circle(center=(point.x, point.y), r=1, **opts))

    def create_gradient(self, color1, color2):
        self.gradient_ids += 1
        gradient_name = "grad" + str(self.gradient_ids)

        gradient = self.dwg.radialGradient((0.5,0.5), 0.5, id=gradient_name)
        gradient.add_stop_color(0, color1)
        gradient.add_stop_color(0.5, color2)
        gradient.add_stop_color(1, color1)
        self.dwg.add(gradient)

        return "url(#{})".format(gradient_name)

    def save(self):
        self.dwg.save()

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

    def dist(self, point):
        return math.sqrt(self.dist2(point))

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
        self.calc_area()
        self.calc_centroid()

    def calc_area(self):
        self.area = sum([(p.x*pp.y - pp.x*p.y) for (p, pp) in
                        zip(self.points, self.points[1:] + self.points[0:1])]) / 2

    def calc_centroid(self):
        #
        # TODO: degenerate polygons should be handled properly
        #
        if self.area == 0:
            self.centroid = self.points[0]
            return
        cx = sum([(p.x + pp.x)*(p.x*pp.y - pp.x*p.y) for (p, pp) in
                  zip(self.points, self.points[1:] + self.points[0:1])])
        cy = sum([(p.y + pp.y)*(p.x*pp.y - pp.x*p.y) for (p, pp) in
                  zip(self.points, self.points[1:] + self.points[0:1])])
        self.centroid = Point(cx / (6 * self.area), cy / (6 * self.area))

    def __repr__(self):
        return "[pl {}]".format(self.points)


def weighted_color(from_rgb, to_rgb):
    def get_color(weight):
        return (int(from_rgb[0] + weight*(to_rgb[0] - from_rgb[0])),
                int(from_rgb[1] + weight*(to_rgb[1] - from_rgb[1])),
                int(from_rgb[2] + weight*(to_rgb[2] - from_rgb[2])))
    return get_color

def offset_color(rgb, offset):
    def offset_component(color_comp):
        return max(min(color_comp, 255), 0)
    r, g, b = rgb
    return (offset_component(r + offset),
            offset_component(g + offset),
            offset_component(b + offset))
