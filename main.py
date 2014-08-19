import time
import random
import tkinter as tk
import math

import svgwrite

import utils
import graphics as gr
import voronoi as vr

###########################################################################

def setup_points():
    relaxation = 0

    #random.seed(100)
    #points = gr.generate_points(50, XRANGE, YRANGE)

    #points = spiral_points(radius_i=0.8, radius_i2=0.02, turns=170)
    #points = spiral_points(radius_i=2, radius_i2=0, turns=170)

    #points = circle_points(radius_i=20, radius_i2=-1, angle_fractions=9, turns=30, antisymm=0)
    points = circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=15, antisymm=0)
    #points = circle_points(radius_i=20, radius_i2=-1, angle_fractions=18, turns=15, antisymm=3)

    #points = grid_points(size=50)

    return (relaxation, points)

def setup_drawing():
    draw_mode = 'voronoi';
    #draw_mode = 'tri-center';
    #draw_mode = 'tri-delaunay';

    #draw_points = True
    draw_points = False

    #area_bounds = None
    area_bounds = (100,1700)

    outline_color = None

    #outline_color = utils.rgb_to_hex(0,0,0)
    #get_color = lambda _: (255,255,255)

    get_color = gr.weighted_color((20,20,138), (140,140,198))
    outline_color = utils.rgb_to_hex(20,20,138)

    #get_color = gr.weighted_color((236,57,50), (148,18,18))
    #outline_color = utils.rgb_to_hex(148,18,18)

    #get_color = gr.weighted_color((38,63,93), (184,210,221))
    #outline_color = utils.rgb_to_hex(38,63,93)

    #do_svg = True
    do_svg = False

    return (draw_mode, draw_points, area_bounds, outline_color, get_color, do_svg)

###########################################################################

MAX_WIDTH = 670
MAX_HEIGHT = 670
PADDING = 10

XRANGE = (PADDING, MAX_WIDTH - PADDING)
YRANGE = (PADDING, MAX_HEIGHT - PADDING)

class DrawingApp(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.pack(fill=tk.BOTH, expand=1)

        canvas = tk.Canvas(self)
        canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas = gr.MyCanvas(canvas)

def createRoot(width, height, title='Drawing'):
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)

    root.geometry("{}x{}+{}+{}".format(width, height, x, y))
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.title(title)
    root.iconbitmap('rabbit.ico')

    return root

def spiral_points(radius_i, radius_i2, turns):
    points = []
    angle = 0
    radius = 0
    for _ in range(turns):
        pt = gr.Point(MAX_WIDTH/2 + math.cos(angle) * radius,
                      MAX_HEIGHT/2 + math.sin(angle) * radius)
        angle += math.pi / 9
        radius += radius_i
        radius_i += radius_i2
        points.append(pt)
    return points

def circle_points(radius_i, radius_i2, angle_fractions, turns, antisymm):
    points = []
    iangle = 0
    iradius = radius_i
    for _ in range(turns):
        angle = iangle
        radius = iradius
        for _ in range(angle_fractions*2-antisymm):
            pt = gr.Point(MAX_WIDTH/2 + math.cos(angle) * radius,
                          MAX_HEIGHT/2 + math.sin(angle) * radius)
            angle += math.pi / angle_fractions
            radius += 0.001
            points.append(pt)
        iradius = radius + radius_i
        radius_i += radius_i2
        iangle += math.pi / (angle_fractions*2)
    return points

def grid_points(size):
    points = []
    dx = 0
    for y in range(YRANGE[0], YRANGE[1], size):
        dx = size/2-dx
        for x in range(XRANGE[0], XRANGE[1], size):
            points.append(gr.Point(x + dx, y))
    return points

def calculate():
    (relaxation, points) = setup_points()

    vor = vr.Voronoi(points)
    vor.process()
    vor.compact_polygons(XRANGE, YRANGE)

    for _ in range(relaxation):
        vor = vor.floyd_relaxation()
        vor.compact_polygons(XRANGE, YRANGE)

    return vor

def draw(canvas, data):
    vor = data

    (draw_mode, draw_points, area_bounds, outline_color, get_color, do_svg) = setup_drawing()

    if do_svg:
        svgCanvas = gr.SvgCanvas("svg/" + time.strftime("%Y_%m_%d_%H_%M_%S.svg", time.localtime()) + ".svg")

    if draw_mode == 'voronoi':
        polys = vor.polygons.values()
    elif draw_mode == 'tri-center':
        polys = vor.polygons.values()
        newpolys = []
        for poly in polys:
            newpolys.extend([gr.Polygon(p1,p2,poly.centroid) for (p1,p2) in zip(poly.points, poly.points[1:] + poly.points[0:1])])
        polys = [poly for poly in newpolys if all(map(lambda p: XRANGE[0] <= p.x <= XRANGE[1] and YRANGE[0] <= p.y <= YRANGE[1], poly.points))]
    else:
        polys = [gr.Polygon(tri.a, tri.b, tri.c) for tri in vor.triangles \
                    if all(map(lambda p: XRANGE[0] <= p.x <= XRANGE[1] and YRANGE[0] <= p.y <= YRANGE[1], [tri.a, tri.b, tri.c]))]

    areas = list(map(lambda poly: abs(poly.area), polys))
    if area_bounds:
        areas = [area for area in areas if area_bounds[0] <= area <= area_bounds[1]]

    maxarea = max(areas)
    minarea = min(areas)
    avgarea = sum(areas) / len(areas)

    print("Areas: min={}, max={}, avg={}".format(minarea, maxarea, avgarea))

    for poly in polys:
        area = abs(poly.area)
        if (not area_bounds) or (area_bounds[0] <= area <= area_bounds[1]):
            weight = (area - minarea) / (maxarea - minarea)
            canvas.draw_polygon(poly, fill=utils.rgb_to_hex(*get_color(weight)), outline=outline_color)
            if do_svg:
                svgCanvas.draw_polygon(poly, fill=utils.rgb_to_hex(*get_color(weight)), stroke=outline_color)
        else:
            canvas.draw_polygon(poly, fill="#ffffff", outline=outline_color)
            if do_svg:
                svgCanvas.draw_polygon(poly, fill="#ffffff", stroke=outline_color)

    if draw_points:
        for point in vor.points:
            canvas.draw_point(point)
            if do_svg:
                svgCanvas.draw_point(point)

    if do_svg:
        svgCanvas.save()

def main():
    data = calculate()
    root = createRoot(MAX_WIDTH, MAX_HEIGHT)
    app = DrawingApp(master=root)
    draw(app.canvas, data)
    root.mainloop()


if __name__ == '__main__':
    main()
