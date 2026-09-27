from __future__ import annotations

from typing import Any
import time

import wgpu
from rendercanvas.glfw import RenderCanvas, loop

from camera2d import *
from colormaterial import *
from transform import *
from quad import *
from triangle import *
from circle import *
from node import *
from texture import *
from sampler import *
from textureset import *
from shader import *
from pipeline import *
from scene import *
from renderer import *
from engine import *

canvas: RenderCanvas
device: wgpu.GPUDevice
context: Any
renderer: Renderer
camera: Camera2D
scene: Scene
last_t: float = 0.0

class MovePointer(Engine):
  def __init__ (self, trf: Transform) -> None:
    self.trf = trf
  def update (self, dt: float) -> None:
    self.trf.rotate(6*dt,0,0,-1)

class Orbit(Engine):
  def __init__(self, trf: Transform, speed: float) -> None:
    self.trf = trf
    self.speed = speed

  def update(self, dt: float) -> None:
    self.trf.rotate(self.speed * dt, 0, 0, 1)

class Rotate(Engine):
  def __init__(self, shader: Shader, speed: float) -> None:
    self.shader = shader
    self.angle = 0.0
    self.speed = speed

  def update(self, dt: float) -> None:
    self.angle += self.speed * dt
    self.shader.set_value("angle", self.angle)

def initialize (device: wgpu.GPUDevice, target_format: str) -> None:
  # create objects
  global camera
  camera = Camera2D(0,10,0,10)

  textura_terra = Texture(device, "decal_texture", "../images/earth.jpg")
  textura_mercurio = Texture(device, "decal_texture", "../images/mercury.jpg")
  textura_moon = Texture(device, "decal_texture", "../images/moon.jpg")
  textura_sun = Texture(device, "decal_texture", "../images/sun.jpg")
  textura_fundo = Texture(device, "decal_texture", "../images/stars.jpg")
  sampler = Sampler(device, "decal_sampler")

  trf_sun = Transform()
  trf_sun.translate(5,5,0)
  trf_sun.scale(1,1,1)
  sun_material = ColorMaterial(1,1,0)

  trf_mercury_orbit = Transform()
  
  trf_mercury = Transform()
  trf_mercury.translate(1.5,0,0)
  trf_mercury.scale(0.12,0.12,1)
  mercury_material = ColorMaterial(0.1,0.1,0.1)

  trf_earth_orbit = Transform()

  trf_earth_position = Transform()
  trf_earth_position.translate(3,0,0)

  trf_earth = Transform()
  trf_earth.scale(0.25,0.25,1)
  earth_material = ColorMaterial(0,0.3,0.9)

  trf_moon_orbit = Transform()

  trf_moon = Transform()
  trf_moon.translate(0.3,0.3,0)
  trf_moon.scale(0.1,0.1,1)
  moon_material = ColorMaterial(0.2,0.2,0.2)

  background_material = ColorMaterial(1, 1, 1)
  trf_fundo = Transform()
  trf_fundo.translate(0, 0, 0)
  trf_fundo.scale(10, 10, 1)

  shader_tex = Shader(device, "../shaders/2d/textured.wgsl")
  shader_tex.set_vertex_buffers([
    {"array_stride": 2 * 4, "step_mode": "vertex",
     "attributes": [{"format": "float32x2", "offset": 0, "var_name": "pos"}]},
    {"array_stride": 2 * 4, "step_mode": "vertex",
      "attributes": [{"format": "float32x2",  "offset": 0, "var_name": "texcoord"}]}
  ])

  shader = Shader(device, "../shaders/2d/shader.wgsl")
  shader.set_vertex_buffers([
    {"array_stride": 2 * 4, "step_mode": "vertex",
      "attributes": [{"format": "float32x2", "offset": 0, "var_name": "pos"}]},
  ])
  pipeline = Pipeline(shader, target_format, depth_stencil=None)
  pipeline_tex = Pipeline(shader_tex, target_format, depth_stencil=None)

  shader.add_material(sun_material)
  shader.add_material(earth_material)
  shader.add_material(moon_material)
  shader.add_material(mercury_material)

  shader_tex.add_material(earth_material)
  shader_tex.add_material(sun_material)
  shader_tex.add_material(moon_material)
  shader_tex.add_material(mercury_material)
  shader_tex.add_material(background_material)
  textures_terra = TextureSet([textura_terra, sampler])
  textures_sun = TextureSet([textura_sun, sampler])
  textures_mercurio = TextureSet([textura_mercurio, sampler])
  textures_moon = TextureSet([textura_moon, sampler])
  textures_fundo = TextureSet([textura_fundo, sampler])
  shader_tex.add_texture_set(textures_terra)
  shader_tex.add_texture_set(textures_sun)
  shader_tex.add_texture_set(textures_mercurio)
  shader_tex.add_texture_set(textures_moon)
  shader_tex.add_texture_set(textures_fundo)

  # build scene
  moon = Node(pipeline_tex, trf=trf_moon,apps=[textures_moon],shps=[Circle(device)])
  moon_orbit = Node(pipeline, trf=trf_moon_orbit,nodes=[moon])
  
  earth = Node(pipeline_tex, trf=trf_earth, apps=[textures_terra], shps=[Circle(device)])
  earth_position = Node(pipeline, trf=trf_earth_position, nodes=[earth, moon_orbit])
  earth_orbit = Node(pipeline, trf=trf_earth_orbit, nodes=[earth_position])

  mercury = Node(pipeline_tex, trf=trf_mercury,apps=[textures_mercurio],shps=[Circle(device)])
  mercury_orbit = Node(pipeline, trf=trf_mercury_orbit, nodes=[mercury])

  sun = Node(pipeline_tex, trf=trf_sun, apps=[sun_material, textures_sun], shps=[Circle(device)], nodes=[earth_orbit, mercury_orbit])

  background = Node(pipeline_tex,trf=trf_fundo,apps=[background_material, textures_fundo],shps=[Quad(device)])

  root = Node(pipeline_tex, nodes = [background, sun])
  global scene
  scene = Scene(root)
  scene.add_engine(Orbit(trf_earth_orbit, 5))
  scene.add_engine(Orbit(trf_earth, -5))
  scene.add_engine(Orbit(trf_moon_orbit, 15))
  scene.add_engine(Rotate(shader_tex, 0.5)) 
  scene.add_engine(Orbit(trf_mercury_orbit, 30))

def update (dt: float) -> None:
  scene.update(dt)

def draw () -> None:
  global last_t
  t = time.perf_counter()
  update(t - last_t)
  last_t = t

  target_texture = context.get_current_texture()
  renderer.render(target_texture, scene, camera)

def on_key (event: Any) -> None:
  if event["key"] == "q":
    canvas.close()

def main () -> None:
  global canvas, device, context, renderer, last_t

  canvas = RenderCanvas(size=(600, 600), title="2D scene", update_mode="continuous", max_fps=60)
  adapter = wgpu.gpu.request_adapter_sync()
  device = adapter.request_device_sync()
  context = canvas.get_context("wgpu")
  # formato preferido COM "-srgb": a GPU codifica de linear para sRGB
  # automaticamente na saída — correto desde que o shader faça a conta de
  # iluminação em espaço linear.
  target_format = context.get_preferred_format(device.adapter)
  context.configure(device=device, format=target_format)

  renderer = Renderer(device, clear_value=(0.8, 1.0, 1.0, 1.0))

  initialize(device, target_format)

  canvas.add_event_handler(on_key, "key_down")
  last_t = time.perf_counter()
  canvas.request_draw(draw)
  loop.run()

if __name__ == "__main__":
  main()
