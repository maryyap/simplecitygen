from perlin import Perlin

class Population():
    def __init__(self, seed = 0):
        self.perlin = Perlin(seed)

    def at(self, x, y):
        v1 = (self.perlin.simplex2(x/10000.0, y/10000.0) + 1) / 2
        v2 = (self.perlin.simplex2((x/20000.0) + 500, (y/20000.0) + 500) + 1) / 2
        v3 = (self.perlin.simplex2((x/20000.0) + 1000, (y/20000.0) + 1000) + 1) / 2
        return (((v1 * v2) + v3) / 2) ** 2

    def along_road(self, seg):
        return (self.at(seg.spt.x, seg.spt.y) +
                self.at(seg.ept.x, seg.ept.y)) / 2
