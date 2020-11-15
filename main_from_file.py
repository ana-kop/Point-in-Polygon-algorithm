# Import modules for the Plotter class
from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt
# Import sys module for the RCA algorithm in the Polygon class
import sys

matplotlib.use('TkAgg')


class Plotter:
    """Definition of the Plotter class, used to plot the polygon, the MBR and the points."""
    def __init__(self):
        plt.figure()

    def add_polygon(self, xs, ys):
        plt.fill(xs, ys, 'lightgray', label='Polygon', lw=2, zorder=0)

    # This method plots the MBR
    def add_mbr(self, xs, ys):
        plt.plot(xs, ys, 'deepskyblue', label='MBR', linestyle='--', lw=1.4)

    def add_point(self, x, y, kind=None):
        if kind == "outside":
            plt.plot(x, y, "ro", label='Outside')
        elif kind == "boundary":
            plt.plot(x, y, "bo", label='Boundary')
        elif kind == "inside":
            plt.plot(x, y, "go", label='Inside')
        else:
            plt.plot(x, y, "ko", label='Unclassified')

    def add_ray(self, x, y, max_x):
        """The add_ray() method plots a horizontal ray from the specified point."""
        x2 = 1.5 * max_x
        plt.arrow(x, y, x2, 0, head_width=0.1, head_length=0.08, label='Ray', linewidth=0.4, linestyle=(0, (1, 10)),
                  color='black', length_includes_head=True)

    def show(self):
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        plt.show()


class Point:
    """Definition of the Point class.
    Point class object has 3 required attributes: point id, x-coordinate, y-coordinate.
    """
    def __init__(self, name, x, y):
        # Attributes can be displayed using their respective methods
        self.name = name
        self.x = x
        self.y = y


class Polygon:
    """Definition of the Polygon class. Polygon class has 1 required attribute: list of points, in clockwise order."""
    def __init__(self, points):
        self.points = points

    @property
    def edges(self):
        """The edges() method returns a list of tuples, where each tuple contains 2 endpoints of a polygon edge"""
        edge_list = []

        # For every point on the list of polygon points, take this point and the next point on the list, and
        # make a tuple containing the coordinates of both of these points
        for i, p in enumerate(self.points):
            p1 = p
            p2 = self.points[(i + 1) % len(self.points)]
            # Append the tuple with 2 points to the list edge_list
            edge_list.append((p1, p2))
        return edge_list

    def x_vertices(self):
        """The vertex_xs() method returns a list of x-coordinates of the polygon points"""
        xs = []
        for point in self.points:
            xs.append(point.x)
        return xs

    def y_vertices(self):
        """The vertex_ys() method returns a list of x-coordinates of the polygon points"""
        ys = []
        for point in self.points:
            ys.append(point.y)
        return ys

    def mbr_contains(self, point, min_x, max_x, min_y, max_y):
        """The mbr_contains() method takes a point object and the MBR vertices, and returns True
        if the point is inside the MBR.
        """
        is_inside_mbr = False
        # check if the x-coordinate of the point is between the minimum and maximum x-coordinates of the polygon,
        # and the y-coordinate of the point is between the minimum and maximum y-coordinates of the polygon
        if (min_x <= point.x <= max_x) and (min_y <= point.y <= max_y):
            is_inside_mbr = True
        return is_inside_mbr

    def contains(self, point):
        #The polygon_contains() method takes a point-of-interest (POI), implements the RCA and returns True if
        #POI is inside the polygon


        # _huge acts as infinity if there is division by 0
        _huge = sys.float_info.max

        # _eps is used in cases where POI has the same y-coordinate as A or B
        _eps = 0.00001

        is_inside_polygon = False
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
               is_inside_polygon = not is_inside_polygon
               continue

            # Find slope of the edge
            try:
               slope_edge = (b.y - a.y) / (b.x - a.x)

            # if the calculation produces a zero division error, then edge is vertical and its slope is infinity
            except ZeroDivisionError:
               slope_edge = _huge

            # Find slope of the line segment between POI and A
            try:
               slope_point = (point.y - a.y) / (point.x - a.x)

            # If the calculation produces a zero division error, then line between POI and A is vertical
            # and its slope is infinity
            except ZeroDivisionError:
               slope_point = _huge

            # If the edge is downward-sloping and the x-coordinates of POI and A are equal, then
            # the horizontal ray does not intersect with the edge
            if slope_edge < 0 and a.x == point.x:
               continue

            # The ray intersects with the edge if none of the conditions above have been fulfilled
            # and the slope of the line between POI and A is greater than or equal to slope of the edge
            if slope_point >= slope_edge:
               is_inside_polygon = not is_inside_polygon
               continue

        return is_inside_polygon

    def boundary(self, point):
        """The boundary() method takes a point-of-interest (POI), and checks if the POI lies on the polygon boundary."""

        on_boundary = False
        for edge in self.edges:
            # name the 2 end points of the edge A and B
            a, b = edge[0], edge[1]
            # make sure A is lower than B
            # if a.y > b.y:
            #     a, b = b, a

            # Calculate the distance between A and B, between A and POI, and between B and POI
            # using the formula 'distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 1/2
            distance_a_b = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** (1 / 2)
            distance_a_point = ((a.x - point.x) ** 2 + (a.y - point.y) ** 2) ** (1 / 2)
            distance_b_point = ((point.x - b.x) ** 2 + (point.y - b.y) ** 2) ** (1 / 2)
            sum_point_dist = distance_a_point + distance_b_point

            # Both numbers are rounded to 12 decimal places before comparison, since Python sometimes rounds
            # square roots to different number of decimal places
            distance_a_b = round(distance_a_b, 12)
            sum_point_dist = round(sum_point_dist, 12)

            # If the sum of the distance between A and POI, and between B and POI is equal to the
            # distance between A and B, then the POI must lie on the edge, and the method returns True
            if sum_point_dist == distance_a_b:
                on_boundary = True
        return on_boundary


def read_points_from_file(file_path, list_for_points):
    # """ The read_points_from_file() method takes a csv file and inputs the points from the file
    # into a specified list as Point class objects """
    with open(file_path, 'r') as f:
        for line in (f.readlines()[1:]):
            items = line.split(',')
            name = str(items[0])
            x = float(items[1])
            y = float(items[2])
            list_for_points.append(Point(name, x, y))
    return list_for_points


def main(polygon_points_file, input_points_file, display_points=True, display_points_rays=True):
    print("Read " + str(polygon_points_file))
    # Read a list of polygon coordinates from 'polygon.csv' file into polygon_points list
    polygon_points_list = []
    read_points_from_file(polygon_points_file, polygon_points_list)

    # Make a polygon object from the points obtained in the previous step
    polygon = Polygon(polygon_points_list)

    # Find coordinates for MBR
    polygon_xs = polygon.x_vertices()
    polygon_ys = polygon.y_vertices()
    min_x = min(polygon_xs)
    max_x = max(polygon_xs)
    min_y = min(polygon_ys)
    max_y = max(polygon_ys)

    # Make lists of x- and y-coordinates of the MBR to plot it
    mbr_x = [min_x, min_x, max_x, max_x, min_x]
    mbr_y = [min_y, max_y, max_y, min_y, min_y]

    # Read a list of points for testing from 'input.csv' file into input_points list
    print("Read " + str(input_points_file))
    input_points_list = []
    read_points_from_file(input_points_file, input_points_list)

    # Make a dictionary of points for testing, where point name/id is key, and point coordinates and location are values
    points_dictionary = {}
    for point in input_points_list:
       points_dictionary.update({point.name: [point.x, point.y, 'unclassified']})

    print("Categorize points")
    # Find which input points are inside MBR and append them to a list of points for further testing
    points_inside_mbr = []
    for point in input_points_list:
       if polygon.mbr_contains(point, min_x, max_x, min_y, max_y) is True:
           points_inside_mbr.append(point)
       else:
           points_dictionary[point.name][2] = 'outside'

    # Find which points are on the polygon boundary and append the other points to a list of points for further testing
    to_be_classified = []
    for point in points_inside_mbr:
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
    print("Write output.csv")
    output_file = open('output.csv', 'w+')
    output_file.write('id,category')

    # For each input point in the dictionary, write point name/id with the result of its classification into output file
    for key, values in points_dictionary.items():
       output_file.write('\n')
       output_file.write(key + ',' + values[2])
    output_file.close()

    # Plot the results of classification alongside the original polygon
    if display_points is True:
        print("Plot polygon and points")
        plotter = Plotter()
        plotter.add_polygon(polygon.x_vertices(), polygon.y_vertices())
        plotter.add_mbr(mbr_x, mbr_y)
        for key, values in points_dictionary.items():
           plotter.add_point(values[0], values[1], values[2])
        if display_points_rays is True:
           for key, values in points_dictionary.items():
               plotter.add_ray(values[0], values[1], max_x)
        plotter.show()
    return None


# If whole file is ran
if __name__ == "__main__":
    polygon_file = 'polygon.csv'
    input_file = 'input.csv'
    main(polygon_file, input_file)
