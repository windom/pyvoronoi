import random

import utils
import ui
import graphics as gr
import drawers as drs
import riemann as rm

###########################################################################

def setup(opts):
    drs.init_size(660,660,11)
    #opts["photo"] = drs.init_photo("oldtree.jpg")

    random.seed(100)
    opts["points"] = drs.random_points(100)

    #opts["points"] = drs.spiral_points(radius_i=0.8, radius_i2=0.02, turns=170)
    #opts["points"] = drs.spiral_points(radius_i=2, radius_i2=0, turns=170)

    #opts["points"] = drs.circle_points(radius_i=20, radius_i2=-1, angle_fractions=9, turns=30, antisymm=0)
    #opts["points"] = drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=15, antisymm=0)
    #opts["points"] = drs.circle_points(radius_i=20, radius_i2=-1, angle_fractions=18, turns=15, antisymm=3)

    #opts["points"] = drs.grid_points(size=50)

    # opts["points"] = []
    # opts["points"].extend(drs.random_points(100,((0, 660),(0,220))))
    # opts["points"].extend(drs.random_points(100,((0, 660),(440,660))))
    # opts["points"].extend(drs.random_points(100,((0, 220),(220,440))))
    # opts["points"].extend(drs.random_points(100,((440, 660),(220,440))))
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=170))

    # opts["points"] = []
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=110, center=(165,165)))
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=110, center=(165+330,165)))
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=110, center=(165,165+330)))
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=110, center=(165+330,165+330)))

    # opts["points"] = []
    # opts["points"].extend(drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=11, antisymm=0, center=(165,165)))
    # opts["points"].extend(drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=11, antisymm=0, center=(165+330,165)))
    # opts["points"].extend(drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=11, antisymm=0, center=(165,165+330)))
    # opts["points"].extend(drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=11, antisymm=0, center=(165+330,165+330)))
    # opts["points"].extend(drs.circle_points(radius_i=20, radius_i2=0, angle_fractions=9, turns=6, antisymm=0, center=(330,330)))

    # opts["points"] = []
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=110, center=(110,110)))
    # opts["points"].extend(drs.spiral_points(radius_i=2, radius_i2=0, turns=180, center=(440,440)))
    # opts["points"].extend(drs.random_points(100, ((230, 660),(0,210))))
    # opts["points"].extend(drs.random_points(100, ((0, 210),(230,660))))

    opts["relaxation"] = 0

    opts["draw_mode"] = 'voronoi'
    #opts["draw_mode"] = 'tri-center'
    #opts["draw_mode"] = 'tri-delaunay'
    #opts["draw_mode"] = 'rectangles'
    #opts["draw_mode"] = 'circles-pack'
    #opts["draw_mode"] = 'circles-fill'
    #opts["draw_mode"] = 'riemann-fill'

    opts["circles_pack_distribution"] = [(6, 15, 30), (18, 1, 15)]
    #opts["circles_pack_distribution"] = [(200, 10, 30)]
    opts["circles_pack_iterations"] = 100
    opts["circles_pack_separation"] = 0
    opts["circles_pack_postfix"] = True

    opts["circles_fill_count"] = 2500
    opts["circles_fill_min_radius"] = 2
    opts["circles_fill_max_radius"] = 100
    opts["circles_fill_decay"] = 'log'
    opts["circles_fill_postfix"] = True

    opts["riemann_fill_exp"] = 1.1
    opts["riemann_fill_rotation"] = 1
    opts["riemann_fill_iterations"] = 5000
    #opts["riemann_fill_shape_maker"] = rm.circle_maker()
    #opts["riemann_fill_shape_maker"] = rm.poly_maker((0,0), (1,0), (1,1), (0, 1))
    #opts["riemann_fill_shape_maker"] = rm.poly_maker((0,0), (1.618, 0), (1.618, 1), (0, 1))
    #opts["riemann_fill_shape_maker"] = rm.poly_maker((1,0), (2,0), (2,1), (3,1), (3,2), (2,2), (2,3), (1,3), (1,2), (0,2), (0,1), (1,1))
    #opts["riemann_fill_shape_maker"] = rm.poly_maker((0,0), (0.5,0.866), (-0.5,0.866))
    #opts["riemann_fill_shape_maker"] = rm.poly_maker((0,0), (1-0.25,0), (1-0.25,1+0.25), (2,1+0.25), (2,2), (0,2))

    opts["rect_width"] = 10
    opts["rect_height"] = 10
    opts["rect_wpad"] = 0
    opts["rect_hpad"] = 0

    #opts["draw_points"] = True
    opts["draw_points"] = False

    opts["area_bounds"] = None
    #opts["area_bounds"] = (100,1700)

    opts["outline_color"] = None

    opts["get_color"] = lambda _: (255,255,255)
    opts["outline_color"] = (0,0,0)

    opts["get_color"] = gr.weighted_color((20,20,138), (140,140,198))
    opts["outline_color"] = (20,20,138)

    #opts["get_color"] = gr.weighted_color((236,57,50), (148,18,18))
    #opts["outline_color"] = (148,18,18)

    #opts["get_color"] = gr.weighted_color((38,63,93), (184,210,221))
    #opts["outline_color"] = (38,63,93)

    opts["outline_color_delta"] = None
    #opts["outline_color_delta"] = 20

    #opts["do_svg"] = True
    opts["do_svg"] = False

###########################################################################

def main():
    opts = {}
    setup(opts)
    drs.process(opts)
    app = ui.DrawingUi(drs.MAX_WIDTH, drs.MAX_HEIGHT)
    drs.flush(opts, app.canvas)
    app.run()

if __name__ == '__main__':
    main()
