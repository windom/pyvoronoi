import random
import tkinter as tk

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
    random.seed(233)

    points = gr.generate_points(100,
                                (PADDING, MAX_WIDTH - PADDING),
                                (PADDING, MAX_HEIGHT - PADDING))

    vor = vr.Voronoi(points).floyd_relaxation()

    return vor


def draw(canvas, data):
    vor = data

    for point in vor.points:
        canvas.draw_point(point)

    for edge in vor.edges:
        canvas.draw_edge(edge)


def main():
    data = calculate()
    root = createRoot(MAX_WIDTH, MAX_HEIGHT)
    app = DrawingApp(master=root)
    draw(app.canvas, data)
    root.mainloop()


if __name__ == '__main__':
    main()
