import graphics as gr
import delaunay as dl


class Voronoi(dl.Delaunay):

    def __init__(self, points):
        super().__init__(points)

        print("Creating edges")
        self.edges = []
        for tris in self.edge_map.values():
            if len(tris) == 2:
                self.edges.append(gr.Edge(tris[0].center, tris[1].center))

        print("Creating polygons")
        self.polygons = {point: self.get_polygon(point) for point in self.points}

    def trimmed_polygons(self, xrange, yrange):
        res = []
        for poly in self.polygons.values():
            if all(map(lambda pt: pt.x >= xrange[0] and pt.x <= xrange[1] and pt.y >= yrange[0] and pt.y <= yrange[1], poly.points)):
                res.append(poly)
        return res

    def floyd_relaxation(self):
        floyd_points = [poly.centroid() for poly in self.polygons.values()]
        return Voronoi(floyd_points)

    def get_polygon(self, point):
        old_edge = edge = next(filter(lambda edge: point in edge.points(), self.edge_map.keys()))
        tri = self.edge_map[edge][0]

        all_tris = []

        while True:
            tri = next(filter(lambda new_tri: new_tri != tri,
                              self.edge_map[edge]))
            all_tris.append(tri)
            edge = next(filter(lambda new_edge: (new_edge != edge) and (point in new_edge.points()), tri.edges()))
            if edge == old_edge:
                break

        return gr.Polygon(*(map(lambda tri: tri.center, all_tris)))
