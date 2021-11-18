import struct
import builtins
from collections import namedtuple


def multimat(A,B):
    result = [[builtins.sum(a * b for a, b in zip(A_row, B_col))
                        for B_col in zip(*B)]
                                for A_row in A]
 
    return result

def toBytes(self):
    self.r = int(max(min(self.r, 255), 0))
    self.g = int(max(min(self.g, 255), 0))
    self.b = int(max(min(self.b, 255), 0))
    return bytes([self.b, self.g, self.r])


def glFinish(filename,width,height,pixels):
    with open(filename, "wb") as file:
        # Header
        file.write(bytes('B'.encode('ascii')))
        file.write(bytes('M'.encode('ascii')))
        file.write(dword(14 + 40 + (width * height * 3)))
        file.write(dword(0))
        file.write(dword(14 + 40))

        # InfoHeader
        file.write(dword(40))
        file.write(dword(width))
        file.write(dword(height))
        file.write(word(1))
        file.write(word(24))
        file.write(dword(0))
        file.write(dword(width * height * 3))
        file.write(dword(0))
        file.write(dword(0))
        file.write(dword(0))
        file.write(dword(0))

        # Bitmap
        for y in range(height):
            for x in range(width):
                file.write(pixels[x][y].toBytes())

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

def sum(v0, v1):

  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):

  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):

  return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):

  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v0, v1):

  return V3(
    v0.y * v1.z - v0.z * v1.y,
    v0.z * v1.x - v0.x * v1.z,
    v0.x * v1.y - v0.y * v1.x,
  )

def length(v0):

  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):

  v0length = length(v0)

  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices):

  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]
  xs.sort()
  ys.sort()

  return V2(int(xs[0]), int(ys[0])), V2(int(xs[-1]), int(ys[-1]))


def barycentric(A, B, C, P):

  bary = cross(
    V3(C.x - A.x, B.x - A.x, A.x - P.x),
    V3(C.y - A.y, B.y - A.y, A.y - P.y)
  )

  if abs(bary.z) < 1:
    return -1, -1, -1   

  return (
    1 - (bary.x + bary.y) / bary.z,
    bary.y / bary.z,
    bary.x / bary.z
  )


def char(c):

  return struct.pack('=c', c.encode('ascii'))

def word(w):
  """
  Input: requires a number such that (-0x7fff - 1) <= number <= 0x7fff
         ie. (-32768, 32767)
  Output: 2 bytes

  Example:
  >>> struct.pack('=h', 1)
  b'\x01\x00'
  """
  return struct.pack('=h', w)

def dword(d):


  return struct.pack('=l', d)

class color(object):
  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r, g, b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other
    return color(r, g, b)

  def __repr__(self):
    return "color(%s, %s, %s)" % (self.r, self.g, self.b)

  def toBytes(self):
    self.r = int(max(min(self.r, 255), 0))
    self.g = int(max(min(self.g, 255), 0))
    self.b = int(max(min(self.b, 255), 0))
    return bytes([self.b, self.g, self.r])

  __rmul__ = __mul__

def reflect(I, N):
    Lm = mul(I, -1)
    n = mul(N, 2 * dot(Lm, N))
    return norm(sub(Lm, n))

def refract(I, N, refractive_index):  # Implementation of Snell's law
    cosi = -max(-1, min(1, dot(I, N)))
    etai = 1
    etat = refractive_index

    if cosi < 0:  # if the ray is inside the object, swap the indices and invert the normal to get the correct result
        cosi = -cosi
        etai, etat = etat, etai
        N = mul(N, -1)

    eta = etai/etat
    k = 1 - eta**2 * (1 - cosi**2)
    if k < 0:
        return V3(1, 0, 0)

    return norm(sum(
      mul(I, eta),
      mul(N, (eta * cosi - k**(1/2)))
    ))


WHITE = color(255, 255, 255)

class Light(object):
    def __init__(self, position=V3(0,0,0), intensity=1):
        self.position = position
        self.intensity = intensity

class Material(object):
    def __init__(self, diffuse=WHITE, albedo=(1, 0, 0, 0), spec=0, refractive_index=1, texture = None):
        self.diffuse = diffuse
        self.albedo = albedo
        self.spec = spec
        self.refractive_index = refractive_index
        self.texture = texture

class Intersect(object):
    def __init__(self, distance, point, normal, texture = None):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.texture = texture

class Texture(object):
    def __init__(self, path):
        self.path = path
        self.read()

    def read(self):
        img = open(self.path, "rb")
        img.seek(10)
        headerSize = struct.unpack('=l', img.read(4))[0]

        img.seek(14 + 4)
        self.width = struct.unpack('=l', img.read(4))[0]
        self.height = struct.unpack('=l', img.read(4))[0]

        img.seek(headerSize)
        self.pixels = []
        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(img.read(1)) / 255
                g = ord(img.read(1)) / 255
                r = ord(img.read(1)) / 255

                self.pixels[y].append(color(r, g, b))


        img.close()

    def get_color(self, tx, ty):
      if tx >= 0 and tx <= 1 and ty >= 0 and ty <= 1:
        x = int(tx * self.width)
        y = int(ty * self.height)
        return self.pixels[y][x]
      else:
        return color(0, 0, 0)