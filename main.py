import random

import utils
import ui
import graphics as gr
import drawers as drs

###########################################################################

def setup():
    opts = {}

    drs.init_size(670,670,11)
    #opts["photo"] = drs.init_photo("oldtree.jpg")

    #random.seed(100)
    opts["points"] = drs.random_points(100)

    #opts["points"] = drs.spiral_points(radius_i=0.8, radius_i2=0.02, turns=170)
    #opts["points"] = drs.spiral_points(radius_i=2, radius_i2=0, turns=170)

    #opts["points"] = drs.circle_points(radius_i=20, radius_i2=-1, angle_fractions=9, turns=30, antisymm=0)
    #opts["points"] = drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=15, antisymm=0)
    #opts["points"] = drs.circle_points(radius_i=20, radius_i2=-1, angle_fractions=18, turns=15, antisymm=3)

    #opts["points"] = drs.grid_points(size=50)

    opts["relaxation"] = 0

    #opts["draw_mode"] = 'voronoi'
    opts["draw_mode"] = 'tri-center'
    #opts["draw_mode"] = 'tri-delaunay'
    #opts["draw_mode"] = 'rectangles'

    opts["rect_width"] = 10
    opts["rect_height"] = 10
    opts["rect_wpad"] = 0
    opts["rect_hpad"] = 0

    #opts["draw_points"] = True
    opts["draw_points"] = False

    opts["area_bounds"] = None
    #opts["area_bounds"] = (100,1700)

    opts["outline_color"] = None

    #opts["outline_color"] = utils.rgb_to_hex(0,0,0)
    #opts["get_color"] = lambda _: (255,255,255)

    opts["get_color"] = gr.weighted_color((20,20,138), (140,140,198))
    opts["outline_color"] = utils.rgb_to_hex(20,20,138)

    #opts["get_color"] = gr.weighted_color((236,57,50), (148,18,18))
    #opts["outline_color"] = utils.rgb_to_hex(148,18,18)

    #opts["get_color"] = gr.weighted_color((38,63,93), (184,210,221))
    #opts["outline_color"] = utils.rgb_to_hex(38,63,93)

    #opts["photo_gradient"] = True
    opts["photo_gradient"] = False

    #opts["do_svg"] = True
    opts["do_svg"] = False

    return opts

###########################################################################

def main():
    opts = setup()
    drs.process(opts)
    app = ui.DrawingUi(drs.MAX_WIDTH, drs.MAX_HEIGHT)
    drs.flush(opts, app.canvas)
    app.run()

if __name__ == '__main__':
    main()
