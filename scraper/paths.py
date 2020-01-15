"""
Path Classes

    Expose consistent movement and path sampling, jumping, analysis for 
    various classes.
"""

import numpy as np 


class Path():
    def __init__(self, step_size, start_coord):
        self.step_size = step_size
        self.path_len = self.calc_path_len()
        self.start_coord = start_coord

    def move(self):
        NotImplemented

    def sample(self, **kwargs):
        NotImplemented

    def calc_path_len(self):
        NotImplemented

    def convert_latlong(self):
        NotImplemented

    def get_coord(self):
        NotImplemented


class SpiralPath(Path):
    """
    Logistic Sprial Path
    r = e^(-a*theta)
    """
    def __init__(self, center_coord=[0,0], step_size=np.pi/12, a=0.05, max_radius=1):
        self.theta = 0
        self.a = a
        self.center_coord = center_coord
        self.coord = self.convert_latlong(theta=self.theta, a=a)
        self.max_radius = max_radius

        super().__init__(step_size=step_size, start_coord=center_coord)

    def move(self, d_theta=None, c=0.025, step=1, **kwargs):
        magnitude = kwargs['magnitude']
        # Calculate expected value for d_theta and adjust curvature
        def delta_a(a, magnitude, c):
            return c * a * magnitude

        self.a = self.a + delta_a(self.a, c, magnitude)
        self.theta += d_theta
        if self.check_max():
            return self.get_coords()
        return None  # Explicity set to None if past the end of path

    def sample_path(self):
        # theta
        pass

    def convert_latlong(self, theta, a):
        r = np.exp(-a*theta)
        self.r_ = r  # Store for max radius check
        lat = r * np.sin(theta) + self.center_coord[0]
        lon = r * np.cos(theta) + self.center_coord[1]
        return(lat,lon)
    
    def get_coords(self):
        self.coord = self.convert_latlong(theta=self.theta, a=self.a)
        return self.coord

    def check_max(self):
        if self.r_ > self.max_radius:
            return False
        return True