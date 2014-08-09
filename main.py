import random
import tkinter as tk

import utils
import graphics as gr
import voronoi as vr

MAX_WIDTH = 700
MAX_HEIGHT = 600
PADDING = 20


class DrawingApp(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.pack(fill=tk.BOTH, expand=1)

        canvas = tk.Canvas(self)
        canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas = gr.MyCanvas(canvas)

        # w = tk.Text(self, height=5)
        # w.pack(fill=tk.X)

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


def calculate():
    #random.seed(233)

    points = 100
    relaxation = 0
    xrange = (PADDING, MAX_WIDTH - PADDING)
    yrange = (PADDING, MAX_HEIGHT - PADDING)

    vor = vr.Voronoi(gr.generate_points(points, xrange, yrange))
    vor.compact_polygons(xrange, yrange)

    for _ in range(relaxation):
        vor = vor.floyd_relaxation()
        vor.compact_polygons(xrange, yrange)

    return vor


def draw(canvas, data):
    vor = data

    #polys = vor.polygons.values()

    xrange = (PADDING, MAX_WIDTH - PADDING)
    yrange = (PADDING, MAX_HEIGHT - PADDING)
    polys = [gr.Polygon(tri.a, tri.b, tri.c) for tri in vor.triangles \
                if all(map(lambda p: xrange[0] <= p.x <= xrange[1] and yrange[0] <= p.y <= yrange[1], [tri.a, tri.b, tri.c]))]

    maxarea = max(map(lambda poly: abs(poly.area), polys))
    minarea = min(map(lambda poly: abs(poly.area), polys))

    outline_color = None

    get_color = gr.weighted_color((20,20,138), (140,140,198))
    outline_color = utils.rgb_to_hex(20,20,138)

    # get_color = gr.weighted_color((236,57,50), (148,18,18))
    # outline_color = utils.rgb_to_hex(148,18,18)

    #get_color = gr.weighted_color((38,63,93), (184,210,221))
    #outline_color = utils.rgb_to_hex(38,63,93)

    for poly in polys:
        weight = (abs(poly.area) - minarea) / (maxarea - minarea)
        canvas.draw_polygon(poly, fill=utils.rgb_to_hex(*get_color(weight)), outline=outline_color)

    # for point in vor.points:
    #     canvas.draw_point(point)

def main():
    data = calculate()
    root = createRoot(MAX_WIDTH, MAX_HEIGHT)
    app = DrawingApp(master=root)
    draw(app.canvas, data)
    root.mainloop()


if __name__ == '__main__':
    main()
