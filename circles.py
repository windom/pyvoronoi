import random
import math

import graphics as gr
import utils as u


def circle_pack(distributions, iterations, min_sep, postfix, pcenter):
    circles = []

    for count, min_radius, max_radius in distributions:
        for _ in range(count):
            circles.append((pcenter[0] + 50*random.random(),
                            pcenter[1] + 50*random.random(),
                            random.uniform(min_radius, max_radius)))

    progress = u.make_progressbar(iterations, timeit=True)

    for it_count in range(1, iterations+1):
        progress()

        #circles.sort(key=lambda cc: -((cc[0] - pcenter[0])**2 + (cc[1] - pcenter[1])**2))
        random.shuffle(circles)

        d_min_sep2 = min_sep**2

        for i in range(0, len(circles)-1):
            for j in range(i+1, len(circles)):
                abx = circles[j][0] - circles[i][0]
                aby = circles[j][1] - circles[i][1]
                r = circles[j][2] + circles[i][2]
                abd2 = abx**2 + aby**2
                if abd2 > d_min_sep2:
                    d2 = abd2-d_min_sep2
                else:
                    d2 = 0
                if d2 < r**2 - 0.01:
                    fact = 0.5*(r - math.sqrt(d2)) / math.sqrt(abd2)
                    abx *= fact
                    aby *= fact
                    circles[j] = (circles[j][0] + abx, circles[j][1] + aby, circles[j][2])
                    circles[i] = (circles[i][0] - abx, circles[i][1] - aby, circles[i][2])

        damping = 0.1 / it_count
        for i in range(0, len(circles)):
            cx = circles[i][0] - (circles[i][0] - pcenter[0])*damping
            cy = circles[i][1] - (circles[i][1] - pcenter[1])*damping
            circles[i] = (cx, cy, circles[i][2])

    print("Post-fixing circles")

    if postfix:
        for i in range(0, len(circles)):
            for j in range(0, len(circles)):
                if i==j:
                    break
                abx = circles[j][0] - circles[i][0]
                aby = circles[j][1] - circles[i][1]
                r = circles[j][2] + circles[i][2]
                abd2 = abx**2 + aby**2
                if abd2 > d_min_sep2:
                    d2 = abd2-d_min_sep2
                else:
                    d2 = 0
                if d2 < r**2 - 0.01:
                    dr = 0.5*(r - math.sqrt(d2))
                    circles[j] = (circles[j][0], circles[j][1], circles[j][2]-dr)
                    circles[i] = (circles[i][0], circles[i][1], circles[i][2]-dr)


    return [gr.Circle(gr.Point(cx, cy), r) for cx, cy, r in circles]
