from plane import *

class Cube(object):
  def __init__(self, position, size, material):
    self.position = position
    self.size = size
    self.material = material
    self.planes = []
    half = size / 2

    self.planes = [
     Plane( sum(position, V3(half,0,0)), V3(1,0,0), material),
     Plane( sum(position, V3(-half,0,0)), V3(-1,0,0), material),
     Plane( sum(position, V3(0,half,0)), V3(0,1,0), material),
     Plane( sum(position, V3(0,-half,0)), V3(0,-1,0), material),
     Plane( sum(position, V3(0,0,half)), V3(0,0,1), material),
     Plane( sum(position, V3(0,0,-half)), V3(0,0,-1), material)
    ]

  def ray_intersect(self, orig, direction):

    epsilon = 0.001
    Bounds_Min = [0,0,0]
    Bounds_Max = [0,0,0]

    for i in range(3):
      Bounds_Min[i] = self.position[i] - (epsilon + self.size / 2)
      Bounds_Max[i] = self.position[i] + (epsilon + self.size / 2)

    t = float('inf')
    intersect = None

    for plane in self.planes:
      planeIntersection = plane.ray_intersect(orig, direction)

      if planeIntersection is not None:
        if planeIntersection.point[0] >= Bounds_Min[0] and planeIntersection.point[0] <= Bounds_Max[0]:
          if planeIntersection.point[1] >= Bounds_Min[1] and planeIntersection.point[1] <= Bounds_Max[1]:
            if planeIntersection.point[2] >= Bounds_Min[2] and planeIntersection.point[2] <= Bounds_Max[2]:
              if planeIntersection.distance < t:
                t = planeIntersection.distance
                intersect = planeIntersection

                if abs(plane.normal[0]) > 0:
                    t1 = (planeIntersection.point[1] - Bounds_Min[1]) / (Bounds_Max[1] - Bounds_Min[1])
                    t2 = (planeIntersection.point[2] - Bounds_Min[2]) / (Bounds_Max[2] - Bounds_Min[2])

                elif abs(plane.normal[1]) > 0:
                    t1 = (planeIntersection.point[0] - Bounds_Min[0]) / (Bounds_Max[0] - Bounds_Min[0])
                    t2 = (planeIntersection.point[2] - Bounds_Min[2]) / (Bounds_Max[2] - Bounds_Min[2])

                elif abs(plane.normal[2]) > 0:
                    t1 = (planeIntersection.point[0] - Bounds_Min[0]) / (Bounds_Max[0] - Bounds_Min[0])
                    t2 = (planeIntersection.point[1] - Bounds_Min[1]) / (Bounds_Max[1] - Bounds_Min[1])

                textures = [t1, t2]

    if intersect is not None:
      return Intersect(distance = intersect.distance,
                      point = intersect.point,
                      texture=textures,
                      normal = intersect.normal)
    else:
      return None