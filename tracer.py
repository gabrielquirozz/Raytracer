from lib import *
from math import pi, tan
from random import random
from sphere import *
from cube import *
from plane import *

BLACK = color(0,0,0)
MAX_RECURSION_DEPTH = 3

class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bitmap_color = BLACK
        self.clear()
    
    def clear(self):
        self.pixels = [[ self.bitmap_color for y in range(self.height)]
                       for x in range(self.width)]
    
    def point(self,x,y,col):
        self.pixels[y][x] = col
    
    def glFinish(self, filename):
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            # InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Bitmap
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y].toBytes())
                    
                    
    def cast_ray(self, orig, direction, recursion = 0):
        material, intersect = self.scene_intersect(orig, direction)

        if material is None or recursion >= MAX_RECURSION_DEPTH:  # break recursion of reflections after n iterations
            return self.background_color

        offset_normal = mul(intersect.normal, 1.1)

        if material.albedo[2] > 0:
            reverse_direction = mul(direction, -1)
            reflect_dir = reflect(reverse_direction, intersect.normal)
            reflect_orig = sub(intersect.point, offset_normal) if dot(reflect_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
            reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
        else:
            reflect_color = color(0, 0, 0)

        if material.albedo[3] > 0:
            refract_dir = refract(direction, intersect.normal, material.refractive_index)
            refract_orig = sub(intersect.point, offset_normal) if dot(refract_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
            refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
        else:
            refract_color = color(0, 0, 0)

        light_dir = norm(sub(self.light.position, intersect.point))
        light_distance = length(sub(self.light.position, intersect.point))

        shadow_orig = sub(intersect.point, offset_normal) if dot(light_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
        shadow_intensity = 0

        if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
            shadow_intensity = 0.9

        intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)

        reflection = reflect(light_dir, intersect.normal)
        specular_intensity = self.light.intensity * (
        max(0, -dot(reflection, direction))**material.spec
        )
        
        diffuse = material.diffuse * intensity * material.albedo[0]
        specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
        reflection = reflect_color * material.albedo[2]
        refraction = refract_color * material.albedo[3]

        if material.texture and intersect.texture is not None:
            text_color = material.texture.get_color(intersect.texture[0], intersect.texture[1])
            diffuse = text_color * 255

        return diffuse + specular + reflection + refraction
    
    def scene_intersect(self, orig, direction):
        zbuffer = float('inf')

        material = None
        intersect = None

        for obj in self.scene:
          hit = obj.ray_intersect(orig, direction)
          if hit is not None:
            if hit.distance < zbuffer:
              zbuffer = hit.distance
              material = obj.material
              intersect = hit

        return material, intersect
    
    
    def render(self):
        fov = int(pi/2)
        ar = self.width/self.height
        for y in range(self.height):
            for x in range(self.width):
                if random() > 0:
                    i =  (2*(x + 0.5)/self.width - 1) * tan(fov/2) * ar
                    j =  (2*(y + 0.5)/self.height - 1) * tan(fov/2)
                    direction = norm(V3(i, j, -1))
                    self.pixels[y][x] = self.cast_ray(V3(0,0,0), direction)


    
    
ivory = Material(diffuse=color(100, 100, 80), albedo=(0.6, 0.3, 0.1, 0), spec=50)
rubber = Material(diffuse=color(80, 0, 0), albedo=(0.9, 0.1, 0, 0, 0), spec=10)
mirror = Material(diffuse=color(255, 255, 255), albedo=(0, 10, 0.8, 0), spec=1425)
sun = Material(diffuse=color(252, 212, 64))
tree = Material(texture=Texture('materials/Oak-Leaves.bmp'))
grass = Material(texture=Texture('materials/textura.bmp'))
water = Material(texture=Texture('materials/water.bmp'))
wood = Material(texture=Texture('materials/woo.bmp'))


r = Raytracer(1000, 1000)

r.light = Light(
  position=V3(-20, 20, 20),
  intensity=1.5
)

r.background_color = color(0, 196, 255)

r.scene = [
  Sphere(V3(0.6, 0, 1), 1, sun),
  Cube(V3(0, -8, -20),2,wood),
  Cube(V3(-2, -8, -20),2,wood),
  Cube(V3(2, -8, -20),2,tree),
  Cube(V3(2, -6, -20),2,tree),
  Cube(V3(2, -10, -20),2,tree),
  Cube(V3(4, -8, -20),2,tree),
  Cube(V3(-6, -10, -20),2,grass),
  Cube(V3(-7, -10, -20),2,grass),
  Cube(V3(-6, -8, -20),2,grass),
  Cube(V3(-4, -8, -20),2,grass),
  Cube(V3(-4, -10, -20),2,grass),
  Cube(V3(-4, -6, -20),2,grass),
  Cube(V3(-4, -4, -20),2,grass),
  Cube(V3(-4, -2, -20),2,grass),
  Cube(V3(-4, 0, -20),2,grass),
  Cube(V3(-4, 2, -20),2,grass),
  Cube(V3(-4, 4, -20),2,grass),
  Cube(V3(-4, 6, -20),2,grass),
  Cube(V3(-4, 8, -20),2,grass),
  Cube(V3(-4, 10, -20),2,grass),
  Cube(V3(-6, 10, -20),2,grass),
  Cube(V3(-7, 10, -20),2,grass),
  Cube(V3(-6, 8, -20),2,grass),
  Cube(V3(-4, 8, -20),2,grass),
  Cube(V3(0, 8, -20),2,wood),
  Cube(V3(-2, 8, -20),2,wood),
  Cube(V3(2, 8, -20),2,tree),
  Cube(V3(2, 6, -20),2,tree),
  Cube(V3(2, 10, -20),2,tree),
  Cube(V3(4, 8, -20),2,tree),
  Cube(V3(-13, 0, -20),15,water),
]
r.render()
r.glFinish('gabriel.bmp')
