import numpy as np


class Vector(np.ndarray):
    def __new__(cls, x, y):
        dtype = float
        return super(Vector, cls).__new__(cls, shape=2, buffer=np.array([x, y], dtype=dtype))

    def __mul__(self, value):
        if type(value) in (float, int):
            return super().__mul__(value)
        elif type(value) == Vector:
            return np.dot(self, value)

    @property
    def length(self):
        return np.sqrt(np.sum(np.power(self, 2)))


class Matrix(np.ndarray):
    def __new__(cls, m):
        dtype = float
        return super(Matrix, cls).__new__(cls, shape=(2, 2), buffer=np.array(m, dtype=dtype))


def out_of_boundary(point, boundary):
    """
    Verify is the point out of boundart
    Parameter:
        point: Vector
        boundary: Matrix
    """


def clip(v, a, b):
    if a < v < b:
        return v
    if v <= a:
        return a
    if v >= b:
        return b
