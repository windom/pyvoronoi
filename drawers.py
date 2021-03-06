import time
import random
import math

from PIL import Image

import utils as u
import graphics as gr
import voronoi as vr
import circles as cs
import rasterizer as ras
import riemann as rm

##############################################################################
# Size inits
##############################################################################

def init_size(width, height, padding):
    global MAX_WIDTH, MAX_HEIGHT, PADDING
    MAX_WIDTH = width
    MAX_HEIGHT = height
    PADDING = padding
    init_ranges()


def init_photo(name):
    global MAX_WIDTH, MAX_HEIGHT
    image = Image.open("imgs/" + name)
    MAX_WIDTH = image.size[0] + 2*(PADDING - 1)
    MAX_HEIGHT = image.size[1] + 2*(PADDING - 1)
    init_ranges()
    return image.load()


def init_ranges():
    global XRANGE, YRANGE
    XRANGE = (PADDING, MAX_WIDTH - PADDING)
    YRANGE = (PADDING, MAX_HEIGHT - PADDING)


##############################################################################
# Point generators
##############################################################################

def spiral_points(radius_i, radius_i2, turns, center=None):
    if center is None:
        center = (MAX_WIDTH/2, MAX_HEIGHT/2)
    points = []
    angle = 0
    radius = 0
    for _ in range(turns):
        pt = gr.Point(center[0] + math.cos(angle) * radius,
                      center[1] + math.sin(angle) * radius)
        angle += math.pi / 9
        radius += radius_i
        radius_i += radius_i2
        points.append(pt)
    return points

def circle_points(radius_i, radius_i2, angle_fractions, turns, antisymm, center=None):
    if center is None:
        center = (MAX_WIDTH/2, MAX_HEIGHT/2)
    points = []
    iangle = 0
    iradius = radius_i
    for _ in range(turns):
        angle = iangle
        radius = iradius
        for _ in range(angle_fractions*2-antisymm):
            pt = gr.Point(center[0] + math.cos(angle) * radius,
                          center[1] + math.sin(angle) * radius)
            angle += math.pi / angle_fractions
            radius += 0.001
            points.append(pt)
        iradius = radius + radius_i
        radius_i += radius_i2
        iangle += math.pi / (angle_fractions*2)
    return points

def grid_points(size, ranges=None):
    if ranges is None:
        xrange, yrange = XRANGE, YRANGE
    else:
        xrange, yrange = ranges
    points = []
    dx = 0
    for y in range(yrange[0], yrange[1], size):
        dx = size/2-dx
        for x in range(xrange[0], xrange[1], size):
            points.append(gr.Point(x + dx, y))
    return points

def random_points(count, ranges=None):
    if ranges is None:
        xrange, yrange = XRANGE, YRANGE
    else:
        xrange, yrange = ranges
    def random_point(idx):
        return gr.Point(
            random.uniform(xrange[0], xrange[1]),
            random.uniform(yrange[0], yrange[1]),
            "p{}".format(idx))
    return [random_point(idx + 1) for idx in range(count)]

##############################################################################
# Polygon generators
##############################################################################

def uniform_rectangles(width, height, wpad, hpad):
    full_width = width + wpad
    full_height = height + hpad

    rectangles = []

    for x in range(XRANGE[0], XRANGE[1]-full_width+1, full_width):
        for y in range(YRANGE[0], YRANGE[1]-full_height+1, full_height):
            poly = gr.Polygon(gr.Point(x, y),
                              gr.Point(x + width, y),
                              gr.Point(x + height, y + height),
                              gr.Point(x, y + height))
            rectangles.append(poly)

    return rectangles

##############################################################################
# Drawing
##############################################################################

def process(opts):
    print("Begin processing")
    calculate(opts)
    postprocess(opts)
    draw(opts)
    print("Finished processing")

def calculate(opts):
    draw_mode = opts["draw_mode"]

    if draw_mode == "rectangles":
        opts["polygons"] = uniform_rectangles(opts["rect_width"],
                                              opts["rect_height"],
                                              opts["rect_wpad"],
                                              opts["rect_hpad"])
    elif draw_mode == "circles-pack":
        opts["polygons"] = cs.circle_pack(opts["circles_pack_distribution"],
                                          opts["circles_pack_iterations"],
                                          opts["circles_pack_separation"],
                                          opts["circles_pack_postfix"],
                                          (XRANGE, YRANGE))
    elif draw_mode == "circles-fill":
        opts["polygons"] = cs.circle_fill((XRANGE, YRANGE),
                                          opts["circles_fill_count"],
                                          opts["circles_fill_min_radius"],
                                          opts["circles_fill_max_radius"],
                                          opts["circles_fill_decay"],
                                          opts["circles_fill_postfix"])
    elif draw_mode == "riemann-fill":
        opts["polygons"] = rm.fill((XRANGE,YRANGE),
                                   opts["riemann_fill_exp"],
                                   opts["riemann_fill_rotation"],
                                   opts["riemann_fill_iterations"],
                                   opts["riemann_fill_shape_maker"])
    else:
        vor = vr.Voronoi(opts["points"])
        vor.process()
        vor.compact_polygons(XRANGE, YRANGE)

        for _ in range(opts["relaxation"]):
            vor = vor.floyd_relaxation()
            vor.process()
            vor.compact_polygons(XRANGE, YRANGE)

        opts["voronoi"] = vor


def postprocess(opts):
    draw_mode = opts["draw_mode"]
    vor = opts.get("voronoi", None)

    if draw_mode == 'voronoi':
        polys = vor.polygons.values()
    elif draw_mode == 'tri-center':
        polys = vor.polygons.values()
        newpolys = []
        for poly in polys:
            newpolys.extend([gr.Polygon(p1,p2,poly.centroid) for (p1,p2) in poly.point_edges()])
        polys = [poly for poly in newpolys if all(map(lambda p: XRANGE[0] <= p.x <= XRANGE[1] and YRANGE[0] <= p.y <= YRANGE[1], poly.points))]
    elif draw_mode in ('rectangles', 'circles-pack', 'circles-fill', 'riemann-fill'):
        polys = opts["polygons"]
    else:
        polys = [gr.Polygon(tri.a, tri.b, tri.c) for tri in vor.triangles \
                    if all(map(lambda p: XRANGE[0] <= p.x <= XRANGE[1] and YRANGE[0] <= p.y <= YRANGE[1], [tri.a, tri.b, tri.c]))]

    areas = list(map(lambda poly: abs(poly.area), polys))
    if opts["area_bounds"]:
        areas = [area for area in areas if opts["area_bounds"][0] <= area <= opts["area_bounds"][1]]

    maxarea = max(areas)
    minarea = min(areas)
    avgarea = sum(areas) / len(areas)

    print("Areas: min={}, max={}, avg={}".format(minarea, maxarea, avgarea))

    opts["polygons"] = polys
    opts["minarea"] = minarea
    opts["maxarea"] = maxarea

def draw(opts):
    print("Drawing")

    canvas = opts["canvas"] = gr.MyCanvas()

    polys = opts["polygons"]
    do_svg = opts["do_svg"]

    if do_svg:
        svg_name = "svg/" + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + ".svg"
        print("Save SVG to:", svg_name)
        svg_canvas = gr.SvgCanvas(svg_name)

    outline_color = opts["outline_color"]
    outline_color_delta = opts["outline_color_delta"]

    def draw_stuff(stuff, fill):
        outline = outline_color
        if not (outline_color_delta is None or fill is None):
            outline = gr.offset_color(fill, outline_color_delta)

        if not fill is None:
            fill = u.rgb_to_hex(*fill)

        if not outline is None:
            outline = u.rgb_to_hex(*outline)

        if isinstance(stuff, gr.Polygon):
            canvas.draw_polygon(stuff, fill, outline)
            if do_svg:
                svg_canvas.draw_polygon(stuff, fill=fill, stroke=outline)
        elif isinstance(stuff, gr.Circle):
            canvas.draw_circle(stuff, fill, outline)
            if do_svg:
                svg_canvas.draw_circle(stuff, fill=fill, stroke=outline)

    if "photo" in opts:
        photo = opts["photo"]

        def rasterize_stuff(stuff):
            if isinstance(stuff, gr.Polygon):
                pts = [(pt.x-PADDING, pt.y-PADDING) for pt in poly.points]
                return ras.rasterize_poly(pts)
            elif isinstance(stuff, gr.Circle):
                return ras.rasterize_circle((poly.center.x, poly.center.y),
                                            int(poly.radius))

        photo_x = MAX_WIDTH - 2*(PADDING - 1) - 1
        photo_y = MAX_HEIGHT - 2*(PADDING - 1) - 1

        for poly in polys:
            rs = gs = bs = cnt = 0
            for x,y in rasterize_stuff(poly):
                if 0 <= x <= photo_x and 0 <= y <= photo_y:
                    r, g, b, *_ = photo[x,y]
                    rs += r
                    gs += g
                    bs += b
                    cnt += 1
            if cnt > 0:
                rs, gs, bs = int(rs/cnt), int(gs/cnt), int (bs/cnt)
                draw_stuff(poly, (rs,gs,bs))
    else:
        area_bounds = opts["area_bounds"]
        minarea = opts["minarea"]
        maxarea = opts["maxarea"]
        get_color = opts["get_color"]

        for poly in polys:
            area = abs(poly.area)
            if (not area_bounds) or (area_bounds[0] <= area <= area_bounds[1]):
                weight = (area - minarea) / (maxarea - minarea)
                draw_stuff(poly, get_color(weight))
            else:
                draw_stuff(poly, (255,255,255))

    if opts["draw_points"]:
        vor = opts["voronoi"]
        for point in vor.points:
            canvas.draw_point(point)
            if do_svg:
                svg_canvas.draw_point(point)

    if do_svg:
        svg_canvas.save()

def flush(opts, native_canvas):
    canvas = opts["canvas"]
    canvas.canvas = native_canvas
    canvas.flush_calls()
