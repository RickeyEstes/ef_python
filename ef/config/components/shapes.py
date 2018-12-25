import numpy as np
import rowan
from numpy.linalg import norm

from ef.config.component import ConfigComponent
from ef.util.serializable_h5 import SerializableH5

__all__ = ['Shape', 'Box', 'Cylinder', 'Tube', 'Sphere', 'Cone']


class Shape(ConfigComponent, SerializableH5):
    def visualize(self, visualizer, **kwargs):
        raise NotImplementedError()

    def is_point_inside(self, point):
        raise NotImplementedError()

    def generate_uniform_random_point(self, generator):
        return self.generate_uniform_random_points(generator, 1)[0]

    def generate_uniform_random_points(self, generator, n):
        raise NotImplementedError()


def rotation_from_z(vector):
    """
    Find a quaternion that rotates z-axis into a given vector.
    :param vector: Any non-zero 3-component vector
    :return: Array of length 4 with the rotation quaternion
    """
    cos2 = (vector / norm(vector))[2]
    cos = np.sqrt((1 + cos2) / 2)
    sin = np.sqrt((1 - cos2) / 2)
    axis = np.cross((0, 0, 1), vector)
    vector_component = (axis / norm(axis)) * sin
    return np.concatenate(([cos], vector_component))


class Box(Shape):
    def __init__(self, origin=(0, 0, 0), size=(1, 1, 1)):
        self.origin = np.array(origin, np.float)
        self.size = np.array(size, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_box(self.size, self.origin, **kwargs)

    def is_point_inside(self, point):
        return np.all(point >= self.origin) and np.all(point <= self.origin + self.size)

    def generate_uniform_random_points(self, generator, n):
        return generator.uniform(self.origin, self.origin + self.size, (n, 3))


class Cylinder(Shape):
    def __init__(self, start=(0, 0, 0), end=(1, 0, 0), radius=1):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.r = float(radius)
        self._rotation = rotation_from_z(self.end - self.start)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cylinder(self.start, self.end, self.r, **kwargs)

    def is_point_inside(self, point):
        pointvec = point - self.start
        axisvec = self.end - self.start
        axis = norm(axisvec)
        unit_axisvec = axisvec / axis
        projection = np.dot(pointvec, unit_axisvec)
        perp_to_axis = pointvec - unit_axisvec * projection
        return 0 <= projection <= axis and norm(perp_to_axis) <= self.r

    def generate_uniform_random_points(self, generator, n):
        r = np.sqrt(generator.uniform(0.0, 1.0, n)) * self.r
        phi = generator.uniform(0.0, 2.0 * np.pi, n)
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        z = generator.uniform(0.0, norm(self.end - self.start), n)
        points = np.stack((x, y, z), -1)
        return rowan.rotate(self._rotation, points) + self.start


class Tube(Shape):
    def __init__(self, start=(0, 0, 0), end=(1, 0, 0), inner_radius=1, outer_radius=2):
        self.start = np.array(start, np.float)
        self.end = np.array(end, np.float)
        self.r = float(inner_radius)
        self.R = float(outer_radius)
        self._rotation = rotation_from_z(self.end - self.start)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_tube(self.start, self.end, self.r, self.R, **kwargs)

    def is_point_inside(self, point):
        pointvec = point - self.start
        axisvec = self.end - self.start
        axis = norm(axisvec)
        unit_axisvec = axisvec / axis
        projection = np.dot(pointvec, unit_axisvec)
        perp_to_axis = pointvec - unit_axisvec * projection
        return 0 <= projection <= axis and self.r <= norm(perp_to_axis) <= self.R

    def generate_uniform_random_points(self, generator, n):
        r = np.sqrt(generator.uniform(self.r / self.R, 1.0, n)) * self.R
        phi = generator.uniform(0.0, 2.0 * np.pi, n)
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        z = generator.uniform(0.0, norm(self.end - self.start), n)
        points = np.stack((x, y, z), -1)
        return rowan.rotate(self._rotation, points) + self.start


class Sphere(Shape):
    def __init__(self, origin=(0, 0, 0), radius=1):
        self.origin = np.array(origin)
        self.r = float(radius)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_sphere(self.origin, self.r, **kwargs)

    def is_point_inside(self, point):
        return norm(point - self.origin, axis=-1) <= self.r

    def generate_uniform_random_points(self, generator, n):
        while True:
            p = generator.uniform(0, 1, (n * 2, 3)) * self.r + self.origin
            p = p.compress(self.is_point_inside(p), 0)
            if len(p) > n:
                return p[:n]


class Cone(Shape):
    def __init__(self, start=(0, 0, 0, 1),
                 start_radii=(1, 2), end_radii=(3, 4)):
        self.start = np.array(start, np.float)
        self.start_radii = np.array(start_radii, np.float)
        self.end_radii = np.array(end_radii, np.float)

    def visualize(self, visualizer, **kwargs):
        visualizer.draw_cone(self.start, self.end,
                             self.start_radii, self.end_radii, **kwargs)

# TODO: def is_point_inside(self, point)
