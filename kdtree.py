import collections
import functools
import random


class Kdtree(collections.namedtuple('Kdtree', ['point', 'left', 'right'])):
    __slots__ = ()

    def nearest(self, point, axis=0, best=None):
        newdist = dist(point, self.point)
        if (not best) or newdist < best[1]:
            best = self.point, newdist

        next_axis = (axis + 1) % len(point)

        if point[axis] < self.point[axis]:
            first, second = self.left, self.right
        else:
            first, second = self.right, self.left

        if first:
            best = first.nearest(point, next_axis, best)

        if second and (self.point[axis] - point[axis])**2 < best[1]:
            best = second.nearest(point, next_axis, best)

        return best

    def nearest_point(self, point):
        return self.nearest(point)[0]

    def points(self):
        yield self.point
        if self.left:
            yield from self.left.points()
        if self.right:
            yield from self.right.points()


def dist(p1, p2):
    return sum((c1 - c2)**2 for (c1, c2) in zip(p1, p2))

def insert_point(kdtree, point, axis=0):
    if kdtree:
        next_axis = (axis + 1) % len(point)
        if point[axis] < kdtree.point[axis]:
            return Kdtree(point=kdtree.point,
                          left=insert_point(kdtree.left, point, next_axis),
                          right=kdtree.right)
        else:
            return Kdtree(point=kdtree.point,
                          left=kdtree.left,
                          right=insert_point(kdtree.right, point, next_axis))
    else:
        return Kdtree(point=point, left=None, right=None)

def remove_point(kdtree, point, axis=0):
    if kdtree:
        next_axis = (axis + 1) % len(point)
        if kdtree.point == point:
            stree = None
            for spoint in kdtree.points():
                if spoint != point:
                    stree = insert_point(stree, spoint, axis)
            return stree
        elif point[axis] < kdtree.point[axis]:
            return Kdtree(point=kdtree.point,
                          left=remove_point(kdtree.left, point, next_axis),
                          right=kdtree.right)
        else:
            return Kdtree(point=kdtree.point,
                          left=kdtree.left,
                          right=remove_point(kdtree.right, point, next_axis))
    else:
        return None

def test(point_count=1000, test_count=100):
    def random_point():
        return (random.uniform(0, 100), random.uniform(0, 100))

    points = [random_point() for _ in range(point_count)]
    kdtree = None
    for point in points:
        kdtree = insert_point(kdtree, point)

    def nearest_fix(qpoint):
        bpoint = min(points, key=functools.partial(dist, qpoint))
        bdist = dist(bpoint, qpoint)
        return (bpoint, bdist)

    def nearest_tree(qpoint):
        return kdtree.nearest(qpoint)

    for _ in range(test_count):
        qpoint = random_point()
        nf = nearest_fix(qpoint)
        nt = nearest_tree(qpoint)
        assert(nf[1] == nt[1])
        #
        # remove too
        #
        rp = random.choice(points)
        points.remove(rp)
        kdtree = remove_point(kdtree, rp)


test()
