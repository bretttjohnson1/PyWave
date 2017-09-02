
class Particle(object):

    # position variables for storing location/velocity info
    x = 0
    y = 0
    z = 0
    vx = 0
    vy = 0
    vz = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def tick(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
