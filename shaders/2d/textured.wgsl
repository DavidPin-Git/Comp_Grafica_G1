struct Matrix {
  vertex: mat4x4<f32>,       // objeto -> espaco global (2D nao ilumina)
}
@group(0) @binding(0) var<storage, read> matrix: array<Matrix>;

struct Global {
  projection: mat4x4<f32>,   // espaco de iluminacao -> NDC
  angle: f32,
}
@group(2) @binding(0) var<uniform> global: Global;


struct ColorBlock {
  color: vec3<f32>,
  opacity: f32,
}
@group(1) @binding(0) var<uniform> material: ColorBlock;

@group(3) @binding(0) var decal_texture: texture_2d<f32>;
@group(3) @binding(1) var decal_sampler: sampler;


struct VertexOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) texcoord: vec2<f32>,
}

@vertex
fn vs_main (@builtin(instance_index) instance_index: u32, @location(0) pos: vec2<f32>, @location(1) texcoord: vec2<f32>) -> VertexOutput {
  var output: VertexOutput;

  output.position = global.projection * (matrix[instance_index].vertex * vec4<f32>(pos, 0.0, 1.0));
  output.texcoord = texcoord;;

  return output;
}

@fragment
fn fs_main (@location(0) texcoord: vec2<f32>) -> @location(0) vec4<f32> {

  let angle = radians(160.0);
  let angle_r = radians(300.0);

  let axis = vec2<f32>(cos(angle),sin(angle));

  // Inclina a textura
  let p = texcoord - vec2<f32>(0.5, 0.5);
  let rotated = vec2<f32>(p.x * axis.x - p.y * axis.y, p.x * axis.y + p.y * axis.x);

  let tilted_texcoord = rotated + vec2<f32>(0.5, 0.5);

  // Deslocamento na mesma direção da inclinação
  let direction = vec2<f32>(sin(angle_r),-cos(angle_r)) + vec2<f32>(0.5, 0.5);

  let texcoord2 = fract(tilted_texcoord - direction * global.angle);

  return textureSample(decal_texture, decal_sampler, texcoord2);
}
