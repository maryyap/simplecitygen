import util
from math import sin, cos, radians, copysign
from decodes.core import Segment, Point, Vec, Intersector


class RoadSegment(Segment): #extending decodes seg
    def __init__(self, spt, ept, is_highway = False):
        super(RoadSegment, self).__init__(spt, ept)
        self.is_highway = is_highway
        self.continue_growing = True

    @staticmethod
    def extend(seg, curve=False):
        if curve:
            sign = -1 * (seg.vec * Vec.ux()).z
            angle = copysign(seg.vec.angle(Vec.ux()), sign)
            if seg.is_highway:
                angle += radians(util.random_angle(3))
            else:
                angle += radians(util.random_angle(5))

            ept = Point(seg.ept.x + seg.length * cos(angle),
                        seg.ept.y + seg.length * sin(angle))
            return RoadSegment(seg.ept, ept, seg.is_highway)
        else:
            return RoadSegment(seg.ept, seg.vec, seg.is_highway)

    @staticmethod
    def branch(seg, offset = 0, force_highway=None):
        if not (force_highway == None):
            highway = force_highway
        else:
            highway = seg.is_highway

        sign = -1 * (seg.vec * Vec.ux()).z
        angle = copysign(seg.vec.angle(Vec.ux()), sign)
        angle += offset
        angle += radians(util.random_angle(15))

        if highway:
            length = 400
        else:
            length = 300

        ept = Point(seg.ept.x + length * cos(angle),
                    seg.ept.y + length * sin(angle))
        return RoadSegment(seg.ept, ept, highway)

    @property
    def bbox(self):
        #need to tell qtree the bounding box of my segment
        xmin = min(self.spt.x, self.ept.x)
        ymin = min(self.spt.y, self.ept.y)
        xmax = max(self.spt.x, self.ept.x)
        ymax = max(self.spt.y, self.ept.y)
        return (xmin, ymin, xmax, ymax)

    def intersects(self, other):
        # http://stackoverflow.com/a/565282/786339
        # p = self.spt
        # q = other.spt
        #ZXC
        # r = self.vec
        # s = other.vec
        #
        # t = (Vec(q - p) * s).z / (r * s).z
        # u = (Vec(q - p) * r).z / (r * s).z
        if (self.spt == other.spt or self.spt == other.ept
            or self.ept == other.spt or self.ept == other.ept):
            return False

        xsec = Intersector()
        if xsec.of(Segment(self.spt, self.ept), Segment(other.spt, other.ept)): #returns True/false
            return xsec.results[0] #if true, puts it into results.

        return False

    def can_connect_to_intersect(self, other):
        """Moves endpoint to other startpoint"""
        if Vec(self.ept, other.spt).length <= 50:
            return True
        else:
            return False

    def can_extend_to_intersect(self, other):
        """Projects (extends) from endpoint to other segment"""
        (near_pt, t, dist) = other.near(self.ept)
        if (t == 0.0 or t == 1.0):
            return False

        if dist <= 50:
            return near_pt

        return False
