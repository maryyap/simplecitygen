import decodes as dc

from math import radians
from random import random
from Queue import PriorityQueue

from pyqtree import Index
from decodes.core import Segment, Vec, Point, Color
from road_segment import RoadSegment
from population import Population


def add_segment_to_map(my_segment, segments, qTree):
    print("Added segment: ", my_segment)
    segments.append(my_segment)
    qTree.insert(my_segment, my_segment.bbox)

def check_and_fix_segment(my_segment, segments, qTree):
    candidates = qTree.intersect(my_segment.bbox)

    for candidate in candidates:
        # If segment is close to intersection, connect to intersection
        if candidate.can_connect_to_intersect(my_segment):
            my_segment.ept = candidate.spt
            my_segment.continue_growing = False
            return True

    for candidate in candidates:
        # If segment can extend to create intersection, create intersection
        intersect_pt = candidate.can_extend_to_intersect(my_segment)
        if intersect_pt:
            if my_segment.vec.angle_deg(candidate.vec) < 30:
                return False
            my_segment.ept = intersect_pt
            my_segment.continue_growing = False
            return True

    for candidate in candidates:
        # If segment intersects, we should shorten to the intersection
        intersect_pt = candidate.intersects(my_segment)
        if intersect_pt:
            if my_segment.vec.angle_deg(candidate.vec) < 30:
                return False
            my_segment.ept = intersect_pt
            my_segment.continue_growing = False
            return True

    return True

    #I had previously defined the 4 params in the bounding box of some RoadSeg

def generate_possible_highway_segments(prev_segment, population):
    """

    """
    segments = []

    straight_seg = RoadSegment.extend_straight(prev_segment)
    angle_seg = RoadSegment.extend_angle(prev_segment)

    if (population.along_road(angle_seg) > population.along_road(straight_seg)):
        seg = angle_seg
    else:
        seg = straight_seg

    segments.append(seg)

    if population.along_road(seg) > 0.1:
        if random() < 0.05:
            # branch right
            segments.append(
                RoadSegment.extend_angle(
                    prev_segment,
                    offset = radians(-90),
                    branch = True))
        if random() < 0.05:
            # branch left
            segments.append(
                RoadSegment.extend_angle(
                    prev_segment,
                    offset = radians(90),
                    branch = True))

    return segments

def generate_branch_segments(prev_segment):
    segments = []
    if random() < 0.4:
        # branch right
        segments.append(
            RoadSegment.extend_angle(
                prev_segment,
                offset = radians(-90),
                branch = True,
                force_highway = False))

    if random() < 0.4:
        # branch left
        segments.append(
            RoadSegment.extend_angle(
                prev_segment,
                offset = radians(90),
                branch = True,
                force_highway = False))

    return segments

def generate_possible_segments(prev_segment, priority, population, priorityQ):
    if (prev_segment.continue_growing == False):
        return False

    new_branches = []

    straight_seg = RoadSegment.extend_straight(prev_segment)
    straight_pop = population.along_road(straight_seg)

    if prev_segment.is_highway:
        highway_segs = generate_possible_highway_segments(prev_segment, population)
        new_branches.extend([(priority, s) for s in highway_segs])
    elif straight_pop > 0.1:
        new_branches.append((priority, straight_seg))

    if straight_pop > 0.1:
        branch_segs = generate_branch_segments(prev_segment)
        new_priority = priority + 5 if prev_segment.is_highway else priority
        new_branches.extend([(new_priority, s) for s in branch_segs])

    for branch_tuple in new_branches:
        priorityQ.put(branch_tuple)

def generate():
    population = Population(random())
    priorityQ = PriorityQueue()

    start_pt = Point(0, 0)
    start_vec = Vec(400, 0)
    root_segment = RoadSegment(start_pt, start_vec, is_highway = True)
    opposite_root = RoadSegment(start_pt, -start_vec, is_highway = True)

    # PQ entries are tuple (t, RoadSegment)
    priorityQ.put((0, root_segment))
    priorityQ.put((0, opposite_root))

    # segments and qTree have the same road segments
    segments = []
    qTree = Index(bbox=(-20000, -20000, 20000, 20000))

    while (not priorityQ.empty() and len(segments) < 2000):
        (priority, next_segment) = priorityQ.get()

        # local_constraints
        try:
            accepted = check_and_fix_segment(next_segment, segments, qTree)
            if (accepted):
                add_segment_to_map(next_segment, segments, qTree)
                generate_possible_segments(next_segment, priority + 1, population, priorityQ)
        except:
            continue

    return (segments, population)

def rhino():
    (segments, population) = generate()
    out = dc.make_out(dc.Outies.Rhino)

    def heatmap():
        p_points = []
        for x in range(-20000, 20000, 500):
            for y in range(-20000, 20000, 500):
                p = Point(x, y)
                p.set_color(Color.HSB(population.at(x, y), 1, 1))
                out.put(p)
                out.draw(p)

    for segment in segments:
        if segment.is_highway:
            segment.set_color(Color.HSB(1,1,1))
        out.put(segment)
        out.draw(segment)

rhino()
