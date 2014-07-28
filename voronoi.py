import random
import math
import time

import utils as u
import graphics as gr

MAX_WIDTH = 700
MAX_HEIGHT = 600
PADDING = 20


class Generator:

    def __init__(self, pointCount, points=None):

        if points:
            self.points = points
        else:
            self.points = self.generate_points(pointCount)

        self.augment_points()

        initial_tri = gr.Triangle(*self.points[:3])
        self.triangles = [ initial_tri ]
        self.edge_map = dict()
        for initial_edge in initial_tri.edges():
            self.edge_map[initial_edge] = [ initial_tri ]

        self.checks = 0

        start = time.time()
        for point in self.points[3:]:
            self.insert_point(point)

        print("Insertion took", time.time() - start)

        print("Total checks", self.checks)
        print("Avg checks", self.checks / pointCount)

        print("Testing...")
        self.test_tris()

        # def check_tri(tri):
        #     pts = tri.points()
        #     return not any((self.points[0] in pts,
        #                    self.points[1] in pts,
        #                    self.points[2] in pts))
        # self.triangles = list(filter(check_tri, self.triangles))

        print("Generating vedges...")
        self.vedges = []
        for duo in self.edge_map.values():
            if len(duo) == 2:
                self.vedges.append(gr.Edge(duo[0].center, duo[1].center))
        # self.vedges = []
        # def common_elements(list1, list2):
        #     return [element for element in list1 if element in list2]
        # for tri1 in self.triangles:
        #     for tri2 in self.triangles:
        #         if common_elements(tri1.edges(), tri2.edges()):
        #             self.vedges.append(gr.Edge(tri1.center, tri2.center))

        # self.insert_point(self.points[3])
        # self.insert_point(self.points[5])
        # self.insert_point(self.points[4])
        # self.insert_point(self.points[6])
        # self.insert_point(self.points[7])

    def floyd_points(self):
        pts = []
        for p in self.points[3:]:
            pol = self.get_poly(p)
            pts.append(pol.centroid())
        return pts

    def get_poly(self, p):
        oedge = edge = next(filter(lambda e: p in e.points(),self.edge_map.keys()))
        tri = self.edge_map[edge][0]

        all_tris = []

        while True:
            tris = self.edge_map[edge]
            new_tri = tris[0]
            if new_tri == tri:
                new_tri = tris[1]
            all_tris.append(new_tri)
            edge = next(filter(lambda e: (e != edge) and (p in e.points()), new_tri.edges()))
            tri = new_tri
            if edge == oedge:
                break

        return gr.Poly(*(map(lambda tri: tri.center,all_tris)))

    def test_tris(self):
        for tri in self.triangles:
            for edge in tri.edges():
                if not self.test_edge(edge):
                    print("BAAAAAAAAAAAAAAAJ")

    def test_edge(self, edge):
        tris = self.find_triangles(edge)
        if len(tris) < 2:
            return True
        def opoint(tri, epoints=edge.points()):
            return next(p for p in tri.points() if not p in epoints)
        pts = [ opoint(tris[1]), opoint(tris[0]) ]
        def checker(trip):
            tri = trip[0]
            pt = trip[1]
            return not tri.circum_contains(pt)
        return all(map(checker, zip(tris, pts)))

    def generate_points(self, pointCount):
        # coords = [(250, 300), (300, 200), (390, 320), (310,300),(330,260)]
        # return [gr.Point(coords[i][0], coords[i][1], "p{}".format(i+1))
        #         for i in range(len(coords))]
        def random_point(idx):
            return gr.Point(
                random.uniform(PADDING, MAX_WIDTH - PADDING),
                random.uniform(PADDING, MAX_HEIGHT - PADDING),
                "p{}".format(idx))
        return [ random_point(idx + 1) for idx in range(pointCount)]

    def augment_points(self):
        origo = self.points[0]
        maxDist = math.sqrt(max(map(lambda point: origo.dist2(point),
                                    self.points[1:])))
        sqrt3 = math.sqrt(3)
        self.points = [
            origo.add(gr.Point(0, -2*maxDist), id="x1"),
            origo.add(gr.Point(-sqrt3*maxDist, maxDist), id="x2"),
            origo.add(gr.Point(+sqrt3*maxDist, maxDist), id="x3")
            ] + self.points

    def insert_point(self, p):
        tri = self.find_triangle(p)

        print("Inserting {} into {}".format(p, tri))

        tri1 = gr.Triangle(tri.a, tri.b, p)
        tri2 = gr.Triangle(tri.b, tri.c, p)
        tri3 = gr.Triangle(tri.a, tri.c, p)

        self.triangles += [ tri1, tri2, tri3 ]
        self.triangles.remove(tri)

        self.update_edgemap(gr.Edge(tri.a, tri.b), tri, tri1)
        self.update_edgemap(gr.Edge(tri.b, tri.c), tri, tri2)
        self.update_edgemap(gr.Edge(tri.a, tri.c), tri, tri3)

        self.edge_map[gr.Edge(tri.a, p)] = [tri1, tri3]
        self.edge_map[gr.Edge(tri.b, p)] = [tri1, tri2]
        self.edge_map[gr.Edge(tri.c, p)] = [tri2, tri3]

        insp_queue = tri.edges()
        old_queue = set()
        while insp_queue:
            edge = insp_queue.pop()
            old_queue.add(edge)
            self.inspect_edge(edge, insp_queue, old_queue)

        u.log("Triangle count {}", len(self.triangles))

    def update_edgemap(self, edge, old_tri, new_tri):
        li = self.edge_map[edge]
        li.remove(old_tri)
        li.append(new_tri)

    def inspect_edge(self, edge, insp_queue, old_queue):
        self.checks += 1

        u.log("  Inspecting {} ({} more to go)", edge, len(insp_queue))

        tris = self.find_triangles(edge)
        if len(tris) < 2:
            u.log("    No pair found")
            return

        def opoint(tri, epoints=edge.points()):
            return next(p for p in tri.points() if not p in epoints)
        pts = [ opoint(tris[1]), opoint(tris[0]) ]

        def checker(trip):
            tri = trip[0]
            pt = trip[1]
            ok = tri.circum_contains(pt)
            u.log("    Checking if {} contains {} --> {}", tri, pt, ok)
            return ok
        flip_needed = any(map(checker, zip(tris, pts)))
        u.log("    Flip needed: {}", flip_needed)
        if not flip_needed:
            return

        new_tris = [ gr.Triangle(edge.p1, *pts), gr.Triangle(edge.p2, *pts)  ]

        self.triangles.remove(tris[0])
        self.triangles.remove(tris[1])
        self.triangles += new_tris

        es1 = list(set(tris[0].edges()) - { edge })
        if not es1[0] in new_tris[0].edges():
            es1 = list(reversed(es1))
        self.update_edgemap(es1[0], tris[0], new_tris[0])
        self.update_edgemap(es1[1], tris[0], new_tris[1])

        es2 = list(set(tris[1].edges()) - { edge })
        if not es2[0] in new_tris[0].edges():
            es2 = list(reversed(es2))
        self.update_edgemap(es2[0], tris[1], new_tris[0])
        self.update_edgemap(es2[1], tris[1], new_tris[1])

        del self.edge_map[edge]
        self.edge_map[gr.Edge(*pts)] = new_tris

        insp_edges = tris[0].edges() + tris[1].edges()

        for insp_edge in insp_edges:
            if not insp_edge in old_queue:
                insp_queue.append(insp_edge)


    def find_triangle(self, p):
        return next(tri for tri in self.triangles if tri.contains(p))

    def find_triangles(self, edge):
        #return list(filter(lambda tri: edge in tri.edges(), self.triangles))
        return self.edge_map[edge]

    def draw(self, canvas):
        for point in self.points:
            canvas.draw_point(point)

        # for triangle in self.triangles:
        #     canvas.draw_triangle(triangle)

        for edge in self.vedges:
            canvas.draw_line(edge.p1, edge.p2)
