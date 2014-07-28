import math
import itertools

import graphics as gr
import utils


class Delaunay:

    def __init__(self, points):
        self.points = points
        print("Will create triangulation for", len(points), "points")

        initial_tri = gr.Triangle(*self.container_points())
        self.triangles = [initial_tri]
        self.edge_map = {edge: [initial_tri] for edge in initial_tri.edges()}

        print("Inserting points")
        progressbar = utils.make_progressbar(len(self.points))
        for point in self.points:
            self.insert_point(point)
            progressbar()

        print("Testing triangles")
        self.test_triangles()

    def container_points(self):
        origo = self.points[0]
        maxDist = math.sqrt(max(map(lambda point: origo.dist2(point),
                                    self.points[1:])))
        sqrt3 = math.sqrt(3)
        return [origo.add(gr.Point(0, -2*maxDist), id="x1"),
                origo.add(gr.Point(-sqrt3*maxDist, maxDist), id="x2"),
                origo.add(gr.Point(+sqrt3*maxDist, maxDist), id="x3")]

    def insert_point(self, point):
        tri = self.find_triangle(point)

        new_tris = [gr.Triangle(tri.a, tri.b, point),
                    gr.Triangle(tri.b, tri.c, point),
                    gr.Triangle(tri.a, tri.c, point)]

        self.triangles += new_tris
        self.triangles.remove(tri)

        self.update_edge_map(gr.Edge(tri.a, tri.b), tri, new_tris[0])
        self.update_edge_map(gr.Edge(tri.b, tri.c), tri, new_tris[1])
        self.update_edge_map(gr.Edge(tri.a, tri.c), tri, new_tris[2])

        self.edge_map[gr.Edge(tri.a, point)] = [new_tris[0], new_tris[2]]
        self.edge_map[gr.Edge(tri.b, point)] = [new_tris[0], new_tris[1]]
        self.edge_map[gr.Edge(tri.c, point)] = [new_tris[1], new_tris[2]]

        inspect_queue = list(tri.edges())
        inspected_set = set()
        while inspect_queue:
            edge = inspect_queue.pop()
            inspected_set.add(edge)
            self.inspect_edge(edge, inspect_queue, inspected_set)

    def inspect_edge(self, edge, inspect_queue, inspected_set):
        tris = self.edge_map[edge]
        if len(tris) < 2:
            return

        apts = [tris[0].edge_antipoint(edge), tris[1].edge_antipoint(edge)]

        if (not tris[0].circum_contains(apts[1])) and \
                (not tris[1].circum_contains(apts[0])):
            return

        new_tris = [gr.Triangle(edge.p1, *apts), gr.Triangle(edge.p2, *apts)]

        self.triangles.remove(tris[0])
        self.triangles.remove(tris[1])
        self.triangles += new_tris

        self.update_edge_map(tris[0].point_antiedge(edge.p1),
                             tris[0], new_tris[1])
        self.update_edge_map(tris[0].point_antiedge(edge.p2),
                             tris[0], new_tris[0])
        self.update_edge_map(tris[1].point_antiedge(edge.p1),
                             tris[1], new_tris[1])
        self.update_edge_map(tris[1].point_antiedge(edge.p2),
                             tris[1], new_tris[0])

        del self.edge_map[edge]
        self.edge_map[gr.Edge(*apts)] = new_tris

        for edge in itertools.chain(tris[0].edges(), tris[1].edges()):
            if edge not in inspected_set:
                inspect_queue.append(edge)

    def find_triangle(self, point):
        return next(tri for tri in self.triangles if tri.contains(point))

    def update_edge_map(self, edge, old_tri, new_tri):
        tris = self.edge_map[edge]
        tris.remove(old_tri)
        tris.append(new_tri)

    def test_triangles(self):
        def test_edge(edge):
            tris = self.edge_map[edge]
            if len(tris) < 2:
                return
            apts = [tris[0].edge_antipoint(edge), tris[1].edge_antipoint(edge)]
            assert not tris[0].circum_contains(apts[1])
            assert not tris[1].circum_contains(apts[0])

        for tri in self.triangles:
            for edge in tri.edges():
                test_edge(edge)
