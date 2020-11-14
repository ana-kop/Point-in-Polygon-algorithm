# Import modules for the Plotter class
from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt
# Import sys module for the RCA algorithm in the Polygon class
import sys

matplotlib.use('TkAgg')


# Define the Plotter class that will plot the polygon, the MBR and the points
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


# Definition of the Point class which has 3 attributes: point id, x-coordinate, y-coordinate
class Point:
    def __init__(self, name, x, y):
        # Attributes can be displayed using their respective methods
        self.name = name
        self.x = x
        self.y = y


# Definition of the Polygon class which has 1 attribute: list of points
class Polygon:
    def __init__(self, points):
        # Where 'points' is a list of point objects, in clockwise order
        self.points = points

    @property
    # The edges() method returns a list of tuples, where each tuple contains 2 endpoints of a polygon edge
    def edges(self):
        edge_list = []

        # For every point in the list of polygon points, take this point and the next point on the list, and
        # make a tuple containing the coordinates of both of these points
        for i, p in enumerate(self.points):
            p1 = p
            p2 = self.points[(i + 1) % len(self.points)]

            # Append the tuple with 2 points to the list edge_list
            edge_list.append((p1, p2))
        return edge_list

    def vertex_xs(self):
        xs = []
        for point in self.points:
            xs.append(point.x)
        return xs

    def vertex_ys(self):
        ys = []
        for point in self.points:
            ys.append(point.y)
        return ys

    # def mbr(self):
    #     # Find coordinates for MBR
    #     min_x = min(self.points_xs)
    #     max_x = max(self.points_xs)
    #     min_y = min(self.points_ys)
    #     max_y = max(self.points_ys)
    #
    #     # make a list of 4 points so that we can make a polygon
    #     mbr_points = [[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y], [min_x, min_y]]
    #     return mbr_points

    # The mbr_check_if_inside() method takes a point object and returns True if the point inside the MBR
    def mbr_check_if_inside(self, point):
        is_inside_mbr = False
        # check if the x-coordinate of the point is between the minimum and maximum x-coordinates of the polygon,
        # and the y-coordinate of the point is between the minimum and maximum y-coordinates of the polygon
        if (min_x <= point.x <= max_x) and (min_y <= point.y <= max_y):
            is_inside_mbr = True
        return is_inside_mbr

    # The contains() method takes a point-of-interest (POI), implements the RCA and
    # returns True if POI is inside the polygon
    def contains(self, point):
        # _huge acts as infinity if there is division by 0
        _huge = sys.float_info.max

        # _eps is used in cases where POI has the same y-coordinate as A or B
        _eps = 0.00001

        inside_polygon = False
        # Start on the outside of the polygon, and consider one polygon edge at a time
        for edge in self.edges:
            # name the 2 end points of the edge A and B
            a, b = edge[0], edge[1]
            # make sure A is lower than B
            if a.y > b.y:
                a, b = b, a

            # Make sure POI does not have the same y-coordinate as on of the edge points
            if point.y == a.y or point.y == b.y:
                # If POI has the same y-coordinate as A or B, increase the y-coordinate of POI by a small number
                point.y += _eps

            # If the x or y-coordinate of POI is greater or smaller than ???
            # then the horizontal ray does not intersect with the edge
            if point.y > b.y or point.y < a.y or point.x > max(a.x, b.x):
                continue

            # If the x-coordinate of POI is smaller than the x-coordinate of both A and B,
            # then the horizontal ray intersects with the edge
            if point.x < min(a.x, b.x):
                inside_polygon = not inside_polygon
                continue

            # Find slope of the edge
            try:
                m_edge = (b.y - a.y) / (b.x - a.x)

            # if the calculation produces a zero division error, then edge is vertical and its slope is infinity
            except ZeroDivisionError:
                m_edge = _huge

            # Find slope of the line segment between POI and A
            try:
                m_point = (point.y - a.y) / (point.x - a.x)

            # If the calculation produces a zero division error, then line between POI and A is vertical
            # and its slope is infinity
            except ZeroDivisionError:
                m_point = _huge

            # If the edge is downward-sloping and the x-coordinates of POI and A are equal, then
            # the horizontal ray does not intersect with the edge
            if m_edge < 0 and a.x == point.x:
                continue

            # The ray intersects with the edge if none of the conditions above have been fulfilled
            # and the slope of the line between POI and A is greater than or equal to slope of the edge
            if m_point >= m_edge:
                inside_polygon = not inside_polygon
                continue

        return inside_polygon

    # The boundary() method takes a point-of-interest (POI), and checks if the POI lies on the polygon boundary
    def boundary(self, point):
        _eps = 0.00001
        on_boundary = False
        for edge in self.edges:
            # name the 2 end points of the edge A and B
            a, b = edge[0], edge[1]
            # make sure A is lower than B
            if a.y > b.y:
                a, b = b, a

            # Calculate the distance between A and B, between A and POI, and between B and POI
            # using the formula 'distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 1/2
            distance_a_b = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** (1 / 2)
            distance_a_point = ((a.x - point.x) ** 2 + (a.y - point.y) ** 2) ** (1 / 2)
            distance_b_point = ((point.x - b.x) ** 2 + (point.y - b.y) ** 2) ** (1 / 2)

            # If the sum of the distance between A and POI, and between B and POI is equal to the
            # distance between A and B, then the POI must lie on the edge, and the method returns True
            if distance_a_point + distance_b_point == distance_a_b:
                on_boundary = True
        return on_boundary


# The read_points_from_file() method takes a csv file and inputs the points from the file as
# Point objects into a specified list
def read_points_from_file(path, list_for_points):
    with open(path, 'r') as f:
        for line in (f.readlines()[1:]):
            items = line.split(',')
            name = str(items[0])
            x = float(items[1])
            y = float(items[2])
            list_for_points.append(Point(name, x, y))
    return list_for_points


# Read a list of polygon coordinates from 'polygon.csv' file into polygon_points list
polygon_points = []
read_points_from_file('polygon.csv', polygon_points)

# Make a polygon object from the points obtained in the previous step
polygon = Polygon(polygon_points)

# Find coordinates for MBR
xs = polygon.vertex_xs()
ys = polygon.vertex_ys()
min_x = min(xs)
max_x = max(xs)
min_y = min(ys)
max_y = max(ys)

# Make lists of x- and y-coordinates of the MBR for plotting it
mbr_x = [min_x, min_x, max_x, max_x, min_x]
mbr_y = [min_y, max_y, max_y, min_y, min_y]

# Read a list of points for testing from 'input.csv' file into input_points list
input_points = []
read_points_from_file('input.csv', input_points)

# Make a dictionary of points for testing, where point name/id is key, and point coordinates and location are values
points_dictionary = {}
for point in input_points:
    points_dictionary.update({point.name: [point.x, point.y, 'unclassified']})

# Find which input points are inside MBR and append them to a list of points for further testing
inside_mbr = []
for point in input_points:
    if polygon.mbr_check_if_inside(point) is True:
        inside_mbr.append(point)
    else:
        points_dictionary[point.name][2] = 'outside'

# Find which points are on the polygon boundary and append the other points to a list of points for further testing
to_be_classified = []
for point in inside_mbr:
    if polygon.boundary(point) is True:
        points_dictionary[point.name][2] = 'boundary'
    else:
        to_be_classified.append(point)

# Classify points that are inside the MBR and not on the boundary
for point in to_be_classified:
    if polygon.contains(point) is True:
        points_dictionary[point.name][2] = 'inside'
    else:
        points_dictionary[point.name][2] = 'outside'

# For each input point, write point name with the result of its classification into a file 'output.csv'
output_file = open('output.csv', 'w+')
output_file.write('id,category')

# For each input point in the dictionary, write point name/id with the result of its classification into the output file
for key, values in points_dictionary.items():
    output_file.write('\n')
    output_file.write(key + ',' + values[2])
output_file.close()

# Plot the results of classification alongside the original polygon
plotter = Plotter()
plotter.add_polygon(polygon.vertex_xs(), polygon.vertex_ys())
plotter.add_mbr(mbr_x, mbr_y)
for key, values in points_dictionary.items():
    plotter.add_point(values[0], values[1], values[2])
plotter.show()
