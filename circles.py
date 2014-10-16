import random
import math

import graphics as gr
import rasterizer as ras
import utils as u


def circle_fill(ranges, circle_count, minrad, maxrad, decay, postfix):
    width = ranges[0][1] - 2*ranges[0][0] + 1
    height = ranges[1][1] - 2*ranges[1][0] + 1
    used = [[False for y in range(height)] for x in range(width)]
    used_count = 0
    total_count = width * height

    maxrad = original_maxrad = maxrad

    fi = maxrad/total_count

    def maxrad_no_decay():
        pass

    def maxrad_uniform_decay():
        nonlocal maxrad, fi
        maxrad = max(5, int(fi*(total_count - used_count)))

    def maxrad_log_decay():
        nonlocal maxrad, fi
        fi =  math.log((1 + (total_count - used_count) / total_count), 2)
        maxrad = min(max(5, int(fi*(total_count - used_count))), original_maxrad)

    maxrad_decay = {
        "none": maxrad_no_decay,
        "uniform": maxrad_uniform_decay,
        "log": maxrad_log_decay
    }[decay]

    maxrad_decay()

    def check_circle(center, radius):
        for x, y in ras.rasterize_circle(center, radius):
            if used[x][y]:
                new_radius = math.ceil(math.sqrt((x-center[0])**2 + (y-center[1])**2))
                if new_radius < radius:
                    return new_radius
                else:
                    return radius - 1
        return None

    circles = []

    print("Will generate", circle_count, "random circles")
    progress = u.make_progressbar(circle_count, timeit=True)

    while len(circles) < circle_count:
        x, y = random.randint(0, width), random.randint(0, height)

        cropdrad = -1
        maxrad_cropped = min(x, y, width-x, height-y, maxrad)

        for radius in range(0, maxrad_cropped):
            if used[x-radius][y] or used[x+radius][y] or used[x][y-radius] or used[x][y+radius]:
                break
            cropdrad = radius

        if cropdrad < minrad:
            continue

        radius = cropdrad
        while radius >= minrad:
            new_radius = check_circle((x,y), radius)
            if new_radius is None:
                for cx, cy in ras.rasterize_circle((x,y), radius):
                    used[cx][cy] = True
                    used_count += 1
                circles.append(gr.Circle(gr.Point(x + ranges[0][0], y + ranges[1][0]), radius))
                maxrad_decay()
                progress()
                break
            else:
                radius = new_radius

    print("Area coverage {:.2f}%".format((used_count / total_count) * 100))

    if postfix:
        print("Postfixing")
        progress = u.make_progressbar(len(circles), timeit=True)

        for i in range(0, len(circles)):
            progress()
            for j in range(0, len(circles)):
                if i==j:
                    break
                abx = circles[j].center.x - circles[i].center.x
                aby = circles[j].center.y - circles[i].center.y
                r = circles[j].radius + circles[i].radius
                d2 = abd2 = abx**2 + aby**2
                if d2 < r**2 - 0.01:
                    fact = 0.5*(r - math.sqrt(d2)) / math.sqrt(abd2)
                    abx *= fact
                    aby *= fact
                    circles[j].center.x += abx
                    circles[j].center.y += aby
                    circles[i].center.x -= abx
                    circles[i].center.y -= aby

    return circles


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
