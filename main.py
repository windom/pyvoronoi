import random as rng
import tkinter as tk

import utils as u
import graphics as gr
import voronoi as vr


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


def main():

    u.log_enabled = False
    rng.seed(233)

    root = createRoot(vr.MAX_WIDTH, vr.MAX_HEIGHT)
    app = DrawingApp(master=root)

    gen = vr.Generator(1000)

    ps = gen.floyd_points()
    gen = vr.Generator(100, ps)
    gen.draw(app.canvas)

    root.mainloop()

if __name__ == '__main__':
    main()
