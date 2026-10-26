// bodycam 风格：整帧后期（鱼眼 + 边缘色散 + 传感器噪点 + 暗角 + 夜视 + 数字掉帧块）。
// 场景先渲染到离屏目标，再用一个全屏三角形按这个着色器画到屏幕上；色调映射和 sRGB 输出在这里做。
import * as THREE from "three";

const VERT = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const FRAG = `
uniform sampler2D tDiffuse;
uniform float time, k, aspect, night, glitch, jolt, seed;
uniform vec2 res;
varying vec2 vUv;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed) * 43758.5453); }
vec2 barrel(vec2 uv, float kk) {
  vec2 c = uv - 0.5; c.x *= aspect;
  float r2 = dot(c, c);
  float rmax = 0.25 * aspect * aspect + 0.25;
  c *= (1.0 + kk * r2) / (1.0 + kk * rmax);   // 鱼眼：中间放大、边缘压缩；整体缩放让四角不露黑
  c.x /= aspect;
  return c + 0.5;
}
void main() {
  vec2 uv = vUv;
  // 数字掉帧：一些块横向错位
  if (glitch > 0.0) {
    vec2 blk = floor(uv * vec2(18.0, 34.0));
    float h = hash(blk + floor(time * 14.0));
    if (h < glitch * 0.35) uv.x += (hash(blk.yx + 3.1) - 0.5) * 0.09 * glitch;
  }
  // 边缘色散：三个通道用略不同的鱼眼强度
  vec3 col = vec3(texture2D(tDiffuse, barrel(uv, k * 1.035)).r, texture2D(tDiffuse, barrel(uv, k)).g, texture2D(tDiffuse, barrel(uv, k * 0.965)).b);
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  vec3 c = gl_FragColor.rgb;
  // 传感器调色：略褪色、黑位抬起、高光发硬
  float l = dot(c, vec3(0.299, 0.587, 0.114));
  c = mix(vec3(l), c, 0.82);
  c = c * 0.94 + 0.035;
  c = mix(c, smoothstep(0.0, 1.0, c), 0.35);
  // 夜视：绿色荧光 + 更重的噪点
  vec3 nv = vec3(0.26, 0.95, 0.36) * (pow(l, 1.15) * 1.05 + 0.03);
  c = mix(c, nv, night);
  // 噪点、曝光闪烁、切镜瞬间的过曝
  float n = hash(vUv * res + fract(time * 7.13) * 91.7) - 0.5;
  c += n * (0.05 + 0.1 * night);
  c *= 1.0 + 0.012 * sin(time * 47.0) + jolt * 0.45;
  // 暗角（鱼眼的圆形边缘）
  vec2 q = (vUv - 0.5) * vec2(aspect, 1.0);
  c *= 1.0 - smoothstep(0.3, 0.78, length(q) * 1.15) * (0.75 + 0.15 * night);
  // 掉帧块：颜色量化
  if (glitch > 0.0) { float b = hash(floor(vUv * vec2(18.0, 34.0)) + floor(time * 14.0)); if (b < glitch * 0.25) c = floor(c * 5.0) / 5.0 + vec3(0.0, 0.05, 0.08); }
  gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}`;

export class BodycamPass {
  constructor(renderer, w, h) {
    this.renderer = renderer;
    this.rt = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, samples: 4 });
    this.mat = new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG, depthTest: false, depthWrite: false,
      uniforms: {
        tDiffuse: { value: this.rt.texture }, time: { value: 0 }, k: { value: 0.8 }, aspect: { value: w / h },
        night: { value: 0 }, glitch: { value: 0 }, jolt: { value: 0 }, seed: { value: 0 }, res: { value: new THREE.Vector2(w, h) },
      },
    });
    // 全屏三角形
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, 2, 0, 0, 2], 2));
    this.quad = new THREE.Mesh(g, this.mat);
    this.quad.frustumCulled = false;
    this.scene = new THREE.Scene();
    this.scene.add(this.quad);
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  }

  setSize(w, h) {
    if (this.rt.width === w && this.rt.height === h) return;
    this.rt.setSize(w, h);
    this.mat.uniforms.aspect.value = w / h;
    this.mat.uniforms.res.value.set(w, h);
  }

  render(scene, camera, u) {
    const U = this.mat.uniforms;
    U.time.value = u.time; U.night.value = u.night; U.glitch.value = u.glitch; U.jolt.value = u.jolt; U.seed.value = u.seed || 0;
    const r = this.renderer;
    r.setRenderTarget(this.rt);
    r.render(scene, camera);
    r.setRenderTarget(null);
    r.render(this.scene, this.cam);
  }
}

// 手持晃动：低频漂移 + 切镜后 0.25 秒的猛一抖（每帧都是 t 的纯函数）
export function handheld(camera, t, lt, noise1) {
  const jolt = Math.max(0, 1 - lt / 0.25) ** 2;
  const a = 1 + 5 * jolt;
  camera.rotateX(noise1(t * 0.55, 11) * 0.007 * a);
  camera.rotateY(noise1(t * 0.45, 13) * 0.009 * a);
  camera.rotateZ(noise1(t * 0.35, 17) * 0.012 * a);
  return jolt;
}
