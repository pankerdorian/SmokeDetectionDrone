import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from random import seed
from random import randrange
from math import exp, sqrt, pow
from csv import reader


class Field:
    def __init__(self, drone_coordinates, h=0):
        self.h = h
        self.base = drone_coordinates
        self.a = (0, 0)
        self.b = (0, 0)
        self.c = (0, 0)
        self.d = (0, 0)
        self.delta = np.deg2rad(20)
        self.alpha1 = np.deg2rad(-31.9)
        self.alpha2 = np.deg2rad(8.9)
        self.tilt_angle = np.deg2rad(-17)
        self.beta = np.deg2rad(57)
        self.rotate_angle = np.deg2rad(3)
        self.x1 = self.h / np.tan(-(self.tilt_angle + self.alpha1))
        self.x12 = self.h / np.tan(-(self.tilt_angle + self.alpha2))
        self.N = 720
        self.M = 1280
        self.cal_trapezoid_points()

    def cal_trapezoid_points(self):
        self.a = (self.x1, self.x1 * np.tan(self.beta/2))
        self.b = (self.x12, self.x12 * np.tan(self.beta/2))
        self.c = (self.x1, -self.x1 * np.tan(self.beta/2))
        self.d = (self.x12, -self.x12 * np.tan(self.beta/2))

    def get_fire_cartesian(self, nf, mf):
        # if nf <0 or (nf > 720) or mf <0 or mf > 1280:
        #     raise Exception("Fire point not in range nf : 0-720, mf : 0-1280")
        xf = self.base[0] + self.x1 + (self.x12 - self.x1) * nf / self.N
        w = 2 * self.a[1] + 2 * (self.b[1] - self.a[1]
                                 ) * (self.N - nf) / self.N
        yf = -(mf - self.M/2)/self.M * w / 2 + self.base[1]
        return xf, yf

# field = Field(h=9)
# print(f"a = {field.a}")
# print(f"b = {field.b}")
# print(f"c = {field.c}")
# print(f"d = {field.d}")
# print(f"p = {field.get_fire_cartesian(400, 400)}")


def gps_distance(gps1, gps2):
    # sqrt((x1 - x2)^2 + (y1 - y2)^2)
    return sqrt(pow(gps1[0] - gps2[0], 2) + pow(gps1[1] - gps2[1], 2))
