from lib import *

class Plane(object):
  def __init__(self, position, normal, material):
    self.position = position
    self.normal = norm(normal)
    self.material = material

  def ray_intersect(self, orig, direction):
    d = dot(direction, self.normal)
    epsilon = 0.0001

    if abs(d) > epsilon:
      t = dot(self.normal, sub(self.position, orig)) / d
      if t > 0:
        hit = sum(orig, mul(direction, t))

        return Intersect(distance = t,
                         point = hit,
                         normal = self.normal)

    return None