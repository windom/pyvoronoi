import math

def safediv(x,y):
    if y == 0:
        return float('inf')
    else:
        return x/y

def rasterize(points):
    edges = list(zip(points, points[1:] + points[0:1]))

    alist = [safediv(pt1[1]-pt2[1], pt1[0]-pt2[0]) for pt1, pt2 in edges]
    blist = [safediv(pt1[0]*pt2[1] - pt2[0]*pt1[1], pt1[0]-pt2[0]) for pt1, pt2 in edges]

    if not any(filter(lambda a: a!=0, alist)):
        return

    #
    # Remove horizontal edges + their a's and b's too
    #
    (edges, alist, blist) = zip(*((e,a,b) for e, a, b in zip(edges, alist, blist) if a != 0))

    def scanline(y):
        xs = []
        for (pt1, pt2), a, b in zip(edges, alist, blist):
            if pt1[1] <= y < pt2[1] or pt2[1] <= y < pt1[1]:
                if math.isinf(a):
                    x = pt1[0]
                else:
                    x = (y - b)/a
                xs.append(int(x))
        if xs:
            for x in range(min(xs), max(xs)+1):
                yield (x,y)

    miny = int(min(map(lambda pt: pt[1], points)))
    maxy = int(max(map(lambda pt: pt[1], points)))

    for y in range(miny, maxy+1):
        yield from scanline(y)
