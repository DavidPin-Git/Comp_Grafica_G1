from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import math
import wgpu
from shape import *

if TYPE_CHECKING:
  from state import State

class Circle (Shape):
  def __init__ (self, device: wgpu.GPUDevice, n: int = 64) -> None:
    coords = []
    coords += [0.0, 0.0]

    texcoords = []
    texcoords += [0.5, 0.5]

    for i in range(n + 1):
        angle = 2.0 * math.pi * (i / n)

        x = math.cos(angle)
        y = math.sin(angle)

        coords += [x, y]

        # Converte [-1, 1] para [0, 1]
        u = 0.5 + 0.5 * x
        v = 0.5 + 0.5 * y

        texcoords += [u, v]

    indices = []
    for i in range(n):
        indices += [0, i + 1, i + 2]

    self.nind = len(indices)

    bcoord = np.array(coords, dtype='float32')
    self.coord_vbo = device.create_buffer_with_data(data=bcoord, usage=wgpu.BufferUsage.VERTEX)

    btexcoords = np.array(texcoords, dtype='float32')
    self.texcoord_vbo = device.create_buffer_with_data(data=btexcoords,usage=wgpu.BufferUsage.VERTEX)

    bindices = np.array(indices, dtype='uint32')
    self.ibo = device.create_buffer_with_data(data=bindices, usage=wgpu.BufferUsage.INDEX)

  def draw (self, st: State) -> None:
    first_instance = st.get_shader().commit_matrix(st)
    st.render_pass.set_vertex_buffer(0, self.coord_vbo)
    st.render_pass.set_vertex_buffer(1, self.texcoord_vbo)
    st.render_pass.set_index_buffer(self.ibo, wgpu.IndexFormat.uint32)
    st.render_pass.draw_indexed(self.nind, 1, 0, 0, first_instance)
