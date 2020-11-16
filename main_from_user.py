# Import modules for the Plotter class
from collections import OrderedDict
import matplotlib
import matplotlib.pyplot as plt
# Import sys module for the RCA algorithm in the Polygon class
import sys

matplotlib.use("TkAgg")


class Plotter:
    """Definition of the Plotter class, used to plot the polygon, the MBR and the points."""
    def __init__(self):
        plt.figure()

    def add_polygon(self, xs, ys):
        plt.fill(xs, ys, "lightgray", label="Polygon", lw=2, zorder=0)

    # This method plots the MBR
    def add_mbr(self, xs, ys):
        plt.plot(xs, ys, "deepskyblue", label="MBR", linestyle="--", lw=1.4)

    def add_point(self, x, y, kind=None):
        if kind == "outside":
            plt.plot(x, y, "ro", label="Outside")
        elif kind == "boundary":
            plt.plot(x, y, "bo", label="Boundary")
        elif kind == "inside":
            plt.plot(x, y, "go", label="Inside")
        else:
            plt.plot(x, y, "ko", label="Unclassified")

    def add_ray(self, x, y, max_x):
        """The add_ray() method plots a horizontal ray from the specified point."""
        xs = [x, max_x + 1]
        ys = [y, y]
        plt.plot(xs, ys, label="Ray", linewidth=0.4,  color="black")

    def show(self):
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        plt.show()


class Point:
    """Definition of the Point class.
    Point class object has 2 required attributes: x-coordinate, y-coordinate.
    """
    def __init__(self, x, y):
        # Attributes can be displayed using their respective methods
        self.x = x
        self.y = y


class Polygon:
    """Definition of the Polygon class.
    Polygon object class has 1 required attribute: list of points, in clockwise order.
    """
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
        """The vertex_xs() method returns a list of x-coordinates of the polygon vertices"""
        xs = []
        for point in self.points:
            xs.append(point.x)
        return xs

    def y_vertices(self):
        """The vertex_ys() method returns a list of x-coordinates of the polygon vertices"""
        ys = []
        for point in self.points:
            ys.append(point.y)
        return ys

    def mbr_contains(self, point, min_x, max_x, min_y, max_y):
        """The mbr_contains() method takes an instance of a point object and the MBR vertices, and returns True
        if the point is inside the MBR.
        """

        is_inside_mbr = False
        # check if the x-coordinate of the point is between the minimum and maximum x-coordinates of the polygon,
        # and the y-coordinate of the point is between the minimum and maximum y-coordinates of the polygon
        if (min_x <= point.x <= max_x) and (min_y <= point.y <= max_y):
            is_inside_mbr = True
        return is_inside_mbr

    def contains(self, point):
        """The polygon_contains() method takes a point-of-interest (POI), implements the RCA and returns True if
        the POI is inside the polygon
        """

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

            # Make sure POI does not have the same y-coordinate as one of the edge points
            if point.y == a.y or point.y == b.y:
                # If POI has the same y-coordinate as A or B, increase the y-coordinate of POI by a small number
                point.y += _eps

            # If the x or y-coordinate of POI is greater or smaller than ???
            # then the horizontal ray does not intersect with the edge
            if point.y > b.y or point.y < a.y or point.x >= max(a.x, b.x):
                continue

            # If the x-coordinate of POI is smaller than the x-coordinate of both A and B,
            # then the horizontal ray intersects with the edge
            if point.x < min(a.x, b.x):
                is_inside_polygon = not is_inside_polygon
                continue

            # Find slope of the edge
            try:
                slope_edge = (b.y - a.y) / (b.x - a.x)

            # if the calculation produces a zero division error, then edge is vertical and its slope is set to infinity
            except ZeroDivisionError:
                slope_edge = _huge

            # Find slope of the line segment between POI and A
            try:
                slope_point = (point.y - a.y) / (point.x - a.x)

            # If the calculation produces a zero division error, then line between POI and A is vertical
            # and its slope is set to infinity
            except ZeroDivisionError:
                slope_point = _huge

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

            # Calculate the distance between A and B, between A and POI, and between B and POI
            # using the formula "distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 1/2
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
    """ The read_points_from_file() function takes a csv file and inputs the points from the file
    into a specified list as Point class instances.
    """
    with open(file_path, "r") as f:
        for line in (f.readlines()[1:]):
            items = line.split(",")
            x = float(items[1])
            y = float(items[2])
            list_for_points.append(Point(x, y))
    return list_for_points


def main(polygon_points_file):

    def check_point(the_polygon, point):
        """ The check_point() function takes a polygon and a point, and checks the location of the point, using the
        Polygon class methods defined above. The function returns the result as a string.
        """
        check_result = "outside"
        if the_polygon.mbr_contains(point, min_x, max_x, min_y, max_y) is False:
            check_result = "outside"
        elif the_polygon.mbr_contains(point, min_x, max_x, min_y, max_y) is True:
            if the_polygon.boundary(point) is True:
                check_result = "boundary"
            elif the_polygon.boundary(point) is False:
                if the_polygon.contains(point) is True:
                    check_result = "inside"
        return check_result

    print("--Read " + str(polygon_points_file))
    # Read a list of polygon coordinates from "polygon.csv" file into polygon_points list
    polygon_points_list = []
    read_points_from_file(polygon_points_file, polygon_points_list)

    # Make an instance of a Polygon from the points obtained in the previous step
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

    print("--Insert point information")
    user_decision = input("Would you like to check location of a point? Please enter yes or no: ")

    while user_decision == "yes":
        # Get the point from user by asking for x- and y-coordinates
        try:
            x = float(input("Please enter the X-coordinate of your point: "))
        # If user entered not a number and there is ValueError
        except ValueError:
            x = float(input("Please input a NUMBER. Please enter the X-coordinate of your point: "))

        try:
            y = float(input("Please enter the Y-coordinate of your point: "))
        # If user entered not a number and there is ValueError
        except ValueError:
            y = float(input("Please input a NUMBER. Please enter the Y-coordinate of your point: "))

        # Make a point Instance
        input_point = Point(x, y)

        print("--Categorize point")
        # Check the location of the point and record it in result
        result = check_point(polygon, input_point)
        print("Your point is on the " + result + " of the polygon.")

        # Plot the results of classification alongside the original polygon
        print("--Plot polygon and points")
        print("IMPORTANT: Please close the plot window to continue")
        plotter = Plotter()
        plotter.add_polygon(polygon.x_vertices(), polygon.y_vertices())
        plotter.add_mbr(mbr_x, mbr_y)
        plotter.add_point(x, y, result)
        plotter.add_ray(x, y, max_x)
        plotter.show()

        user_decision = input("Would you like to check location of another point? Please enter yes or no: ")

        # error handling in input
        if user_decision != "yes" and user_decision != "no":
            user_decision = input("Your answer is not recognised. Would you like to check location of a point? "
                                  "Please enter yes or no:  ")


# If whole file is executed:
if __name__ == "__main__":
    polygon_file = "polygon.csv"
    input_file = "input.csv"
    main(polygon_file)
