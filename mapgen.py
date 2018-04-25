import decodes as dc

from math import radians
from random import random, randint
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
    #return True
    # Reject segements outside of bounds (keeps it closer to the population)
    if (max(my_segment.spt.x, my_segment.spt.y,
            my_segment.ept.x, my_segment.ept.y) > 20000 or
        min(my_segment.spt.x, my_segment.spt.y,
                my_segment.ept.x, my_segment.ept.y) < -20000):
        return False

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
            # if my_segment.vec.angle_deg(candidate.vec) < 30:
            #     return False
            my_segment.ept = intersect_pt
            my_segment.continue_growing = False
            return True

    for candidate in candidates:
        # If segment intersects, we should shorten to the intersection
        intersect_pt = candidate.intersects(my_segment)
        if intersect_pt:
            # if my_segment.vec.angle_deg(candidate.vec) < 30:
            #     return False
            my_segment.ept = intersect_pt
            my_segment.continue_growing = False
            return True

    return True

    #I had previously defined the 4 params in the bounding box of some RoadSeg

def generate_possible_highway_segments(prev_segment, population):
    """

    """
    segments = []

    straight_seg = RoadSegment.extend(prev_segment)
    angle_seg = RoadSegment.extend(prev_segment, curve=True)

    # Highway Extension
    if (population.along_road(angle_seg) > population.along_road(straight_seg)):
        seg = angle_seg
    else:
        seg = straight_seg

    segments.append(seg)

    # Highway Branching
    if population.along_road(seg) > 0.1:
        if random() < 0.02: #2% prob
            # branch right
            segments.append(RoadSegment.branch(prev_segment, offset = radians(-90)))
        if random() < 0.02: #2% prob
            # branch left
            segments.append(RoadSegment.branch(prev_segment, offset = radians(90)))

    return segments

def generate_regular_branches(prev_segment, priority):
    segments = []
    if random() < 0.2:
        # branch right
        segments.append(RoadSegment.branch(prev_segment, offset = radians(-90), force_highway = False))

    if random() < 0.2:
        # branch left
        segments.append(RoadSegment.branch(prev_segment, offset = radians(90), force_highway = False))

    new_priority = priority+5 if prev_segment.is_highway else priority
    return [(new_priority, s) for s in segments]

def generate_possible_segments(prev_segment, priority, population, priorityQ):
    if (prev_segment.continue_growing == False):
        return False

    possible_segments = []

    # Extend or branch highway (highway_segs are always more highways)
    if prev_segment.is_highway:
        highway_segs = generate_possible_highway_segments(prev_segment, population)
        possible_segments.extend([(priority, s) for s in highway_segs])

    # If we are in a populated area, grow roads
    extend_seg = RoadSegment.extend(prev_segment, curve=True)
    if population.along_road(extend_seg) > 0.1:
        if not prev_segment.is_highway:
            # Always extend a regular road
            possible_segments.append((priority, extend_seg))

    # If we are in a really populated area, create road branches
    if population.along_road(extend_seg) > 0.2:
        regular_branches = generate_regular_branches(prev_segment, priority)
        possible_segments.extend(regular_branches)

    for segt in possible_segments:
        priorityQ.put(segt)

def generate(num):
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

    while (len(segments) < num):
        #wrote this because it gets stuck and priorityQ gets empty.
        #this starts the whole process over again.
        if priorityQ.empty():
            start_pt = Point(randint(-15000, 15000), randint(-15000, 15000))
            root_segment = RoadSegment(start_pt, start_vec, is_highway = True)
            opposite_root = RoadSegment(start_pt, -start_vec, is_highway = True)
            priorityQ.put((0, root_segment))
            priorityQ.put((0, opposite_root))

        (priority, next_segment) = priorityQ.get()

        accepted = check_and_fix_segment(next_segment, segments, qTree)
        if (accepted):
            add_segment_to_map(next_segment, segments, qTree)
            generate_possible_segments(next_segment, priority + 1, population, priorityQ)

    return (segments, population)

def rhino():
    (segments, population) = generate(3000)
    rlayer = dc.make_out(dc.Outies.Rhino, name="roads")
    player = dc.make_out(dc.Outies.Rhino, name="population")

    def heatmap():
        p_points = []
        for x in range(-20000, 20000, 1000):
            for y in range(-20000, 20000, 1000):
                p = Point(x, y)
                p.set_color(Color.HSB(population.at(x, y), 1, 1))
                player.put(p)
                player.draw(p)

    heatmap()

    for segment in segments:
        if segment.is_highway:
            segment.set_color(Color.HSB(1,1,1))
        rlayer.put(segment)
        rlayer.draw(segment)

rhino()
