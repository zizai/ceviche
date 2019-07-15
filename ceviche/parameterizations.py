import autograd.numpy as np
from autograd.extend import primitive, defvjp
import numpy

from ceviche.utils import circ2eps, grid_coords

class Param_Base(object):

    def __init__(self):
        pass

    @classmethod
    def get_eps(cls, params, *args):
        raise NotImplementedError("Need to implement a function for computing permittivity from parameters")

""" Topology / Continuous Optimization """

class Param_Topology(Param_Base):

    def __init__(self):
        super().__init__(self)

    @staticmethod
    def _density2eps(mat_density, eps_max):
        return 1 + (eps_max - 1) * mat_density

    @classmethod
    def get_eps(cls, params, eps_background, design_region, eps_max):

        mat_density = params
        eps_inner = cls._density2eps(mat_density, eps_max) * (design_region == 1)
        eps_outer = eps_background * (design_region == 0)

        return eps_inner + eps_outer

""" Shape Optimization """

class Param_Shape(Param_Base):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_eps(*args):
        raise NotImplementedError("Need to implement a function for computing permittivity from parameters")

    @staticmethod
    def sigmoid(x, strength=.1):
        # used to anti-alias the circle, higher strength means sharper boundary
        x1 = x * (x >= 0)
        x2 = x * (x < 0)
        return 1 / (1 + np.exp(-x1 * strength)) + \
            np.exp(x2 * strength) / (1 + np.exp(x2 * strength)) - 1/2

class Circle_Shapes(Param_Shape):

    def __init__(self, eps_background, dL):
        self.eps_background = eps_background
        self.dL = dL
        self.xs, self.ys = grid_coords(self.eps_background, self.dL)
        super().__init__()

    def circle(self, xs, ys, x, y, r):
        # defines an anti aliased circle    
        dist_from_edge = np.power((xs - x), 2) + np.power((ys - y), 2) - np.power(r, 2)
        return self.sigmoid(-dist_from_edge / np.power(self.dL, 2))

    def get_eps(self, xs, ys, rs, values):
        # returns the permittivity array for a bunch of holes at positions (xs, ys) with radii rs and epsilon values (val)
        eps_r = self.eps_background.copy()
        for x, y, r, value in zip(xs, ys, rs, values):
            circle = self.circle(self.xs, self.ys, x, y, r) 
            eps_r = circle*value + (1-circle)*eps_r
        return eps_r

""" Level Set Optimization """

class Param_LevelSet(Param_Base):

    def __init__(self):
        super().__init__(self)

    @classmethod
    def get_eps(cls, params, eps_background, design_region, eps_max):
        raise NotImplementedError("Need to implement a function for computing permittivity from parameters")


if __name__ == '__main__':

    # example of calling one

    shape = (10, 20)
    params = np.random.random(shape)
    eps_background = np.ones(shape)
    design_region = np.zeros(shape)
    design_region[5:,:] = 1
    eps_max = 5

    eps = Param_Topology.get_eps(params, eps_background, design_region, eps_max)
    