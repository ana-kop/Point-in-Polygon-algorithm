from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt
import sys

matplotlib.use('TkAgg')


class Plotter:

    def __init__(self):
        plt.figure()

    def add_polygon(self, xs, ys):
        plt.plot(xs, ys, 'black', label='Polygon', lw=0.7)

    def add_mbr(self, xs, ys):
        plt.plot(xs, ys, 'darkgray', label='MBR', linestyle='--')

    def add_point(self, x, y, kind=None):
        if kind == "outside":
            plt.plot(x, y, "ro", label='Outside')
        elif kind == "boundary":
            plt.plot(x, y, "bo", label='Boundary')
        elif kind == "inside":
            plt.plot(x, y, "go", label='Inside')
        else:
            plt.plot(x, y, "ko", label='Unclassified')

    def show(self):
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        plt.show()


class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


class Polygon:
    def __init__(self, points):
        # points: a list of Points in clockwise order.
        self.points = points

    @property
    def edges(self):
        # Returns a list of tuples that each contain 2 points of an edge
        edge_list = []
        for i, p in enumerate(self.points):
            p1 = p
            p2 = self.points[(i + 1) % len(self.points)]
            edge_list.append((p1, p2))

        return edge_list

    def mbr_check_if_inside(self, point):
        res = False
        if (min_x <= point.x <= max_x) and (min_y <= point.y <= max_y):
            res = True
        return res

    def contains(self, point):
        # _huge is used to act as infinity if we divide by 0
        _huge = sys.float_info.max
        # _eps is used to make sure points are not on the same line as vertexes
        _eps = 0.00001

        # We start on the outside of the polygon
        inside = False
        for edge in self.edges:
            # Make sure A is the lower point of the edge
            a, b = edge[0], edge[1]
            if a.y > b.y:
                a, b = b, a

            # Make sure point is not at same height as vertex
            if point.y == a.y or point.y == b.y:
                point.y += _eps

            if point.y > b.y or point.y < a.y or point.x > max(a.x, b.x):
                # The horizontal ray does not intersect with the edge
                continue

            if point.x < min(a.x, b.x):  # The ray intersects with the edge
                inside = not inside
                continue

            try:
                m_edge = (b.y - a.y) / (b.x - a.x)
            except ZeroDivisionError:
                m_edge = _huge

            try:
                m_point = (point.y - a.y) / (point.x - a.x)
            except ZeroDivisionError:
                m_point = _huge

            if m_edge < 0 and a.x == point.x:
                continue

            if m_point >= m_edge:
                # The ray intersects with the edge
                inside = not inside
                continue

        return inside

    # define a boundary function
    def boundary(self, point):
        _eps = 0.00001
        location = 'outside'
        for edge in self.edges:
            # Make sure A is the lower point of the edge
            a, b = edge[0], edge[1]
            if a.y > b.y:
                a, b = b, a

            distance_a_b = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** (1 / 2)
            distance_a_point = ((a.x - point.x) ** 2 + (a.y - point.y) ** 2) ** (1 / 2)
            distance_b_point = ((point.x - b.x) ** 2 + (point.y - b.y) ** 2) ** (1 / 2)

            if distance_a_point + distance_b_point == distance_a_b:
                location = 'boundary'
        return location


def read_points_from_file(path, mode, list_for_points):
    with open(path, mode) as f:
        for line in (f.readlines()[1:]):
            items = line.split(',')
            name = str(items[0])
            x = float(items[1])
            y = float(items[2])
            list_for_points.append(Point(name, x, y))
    return list_for_points


# Read a list of x, y coordinates from a comma-separated values (CSV) file
polygon_points = []
read_points_from_file('polygon.csv', 'r', polygon_points)
p = Polygon(polygon_points)

xs = []
ys = []
for point in polygon_points:
    xs.append(point.x)
for point in polygon_points:
    ys.append(point.y)

# Find coordinates for MBR
min_x = min(xs)
max_x = max(xs)
min_y = min(ys)
max_y = max(ys)

# make a list of 4 points so that we can make a polygon
mbr_points = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y], [min_x, min_y]]
mbr_x = [min_x, min_x, max_x, max_x, min_x]
mbr_y = [min_y, max_y, max_y, min_y, min_y]

# make a list of coordinates for testing from csv
input_points = []
read_points_from_file('input.csv', 'r', input_points)

points_dictionary = {}
for point in input_points:
    points_dictionary.update({point.name: [point.x, point.y, 'unclassified']})

# find which points are outside MBR
inside_mbr = []
for point in input_points:
    if p.mbr_check_if_inside(point) is True:
        inside_mbr.append(point)
    else:
        points_dictionary[point.name][2] = 'outside'
print(points_dictionary)

# classify points
to_be_classified = []
for point in inside_mbr:
    if p.boundary(point) == 'boundary':
        points_dictionary[point.name][2] = 'boundary'
    else:
        to_be_classified.append(point)

for point in to_be_classified:
    if p.contains(point) is True:
        points_dictionary[point.name][2] = 'inside'
    else:
        points_dictionary[point.name][2] = 'outside'

# write into file
output_file = open('output.csv', 'w+')
output_file.write('id,category')
for key, values in points_dictionary.items():
    output_file.write('\n')
    output_file.write(key + ',' + values[2])  # is it okay for id to be string in the output?
output_file.close()

# plot
plotter = Plotter()
plotter.add_polygon(xs, ys)
plotter.add_mbr(mbr_x, mbr_y)
for key, values in points_dictionary.items():
    plotter.add_point(values[0], values[1], values[2])
plotter.show()
