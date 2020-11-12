from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt
import sys
matplotlib.use('TkAgg')


class Plotter:

    def __init__(self):
        plt.figure()

    def add_polygon(self, xs, ys):
        plt.plot(xs, ys, 'black', label='Polygon',  lw=0.7)

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

    def green_point(self, x, y):
        plt.plot(x, y, "go")

    def red_point(self, x, y):
        plt.plot(x, y, "ro")

    def blue_point(self, x, y):
        plt.plot(x, y, "bo")

    def show(self):
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        plt.show()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Polygon:
    def __init__(self, points):
#points: a list of Points in clockwise order.
        self.points = points

    @property
    def edges(self):
#Returns a list of tuples that each contain 2 points of an edge
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

            distance_a_b = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2)**(1/2)
            distance_a_point = ((a.x - point.x) ** 2 + (a.y - point.y) ** 2)**(1/2)
            distance_b_point = ((point.x - b.x) ** 2 + (point.y - b.y) ** 2)**(1/2)

            if distance_a_point + distance_b_point == distance_a_b:
                location = 'boundary'
        return location

    def check_point(self, point):
        result = 'outside'
#        if self.mbr_check_if_inside(point) is False:
        if self.boundary(point) == 'boundary':
            result = 'boundary'
        elif self.contains(point) is True:
            result = 'inside'
        else:
            pass
        return result

# Read a list of x, y coordinates from a comma-separated values (CSV) file
polygon_points = []
with open('polygon.csv', 'r') as f:
    for line in (f.readlines()[1:]):
        items = line.split(',')
        x = float(items[1])
        y = float(items[2])
        polygon_points.append(Point(x, y))
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

user_decision = input('Would you like to check location of a point? Please enter yes or no: ')

while user_decision == 'yes':
    # get the point from user
    x = float(input('Please enter the X-coordinate of your point: '))
    # if type error
    y = float(input('Please enter the Y-coordinate of your point: '))
    # if type error
    input_point = Point(x, y)

    # find whether point is inside MBR
    result = p.check_point(input_point)
    print('Your point is on the ' + result + ' of the polygon.')

    # plot
    plotter = Plotter()
    plotter.add_polygon(xs, ys)
    plotter.add_point(x, y, result)
    plotter.show()

    user_decision = input('Would you like to check location of another point? Please enter yes or no: ')

# error handling in input
if user_decision != 'yes' and user_decision != 'no':
    user_decision = input('Your answer is not recognised. Would you like to check location of a point? Please enter '
                          'yes or no:  ')
