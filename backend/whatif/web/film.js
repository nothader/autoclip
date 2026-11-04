// film 风格：头部 3D 短片频道那种观感——主体清晰、背景按深度虚化（景深）、明亮暖调、柔和暗角。
// 场景先渲染到带深度纹理的离屏目标，再用全屏三角形做景深 + 色调映射 + 调色。
import * as THREE from "three";

const VERT = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const FRAG = `
#include <packing>
uniform sampler2D tDiffuse, tDepth;
uniform float cameraNear, cameraFar, focusDist, aperture, maxBlur, aspect, tilt, pastel;
uniform vec2 res;
varying vec2 vUv;
float viewDist(vec2 uv) {
  float d = texture2D(tDepth, uv).x;
  return -perspectiveDepthToViewZ(d, cameraNear, cameraFar);
}
float coc(vec2 uv) {   // 弥散圆：离对焦距离越远越大；天空（最远处）也虚
  float z = viewDist(uv);
  float d = clamp(abs(z - focusDist) / max(z, 0.001) * aperture, 0.0, 1.0);
  // 移轴（voxel 风格）：画面上下两端按屏幕位置额外虚化，像微缩模型
  float ts = tilt * smoothstep(0.1, 0.42, abs(uv.y - 0.56));
  return clamp(max(d, ts), 0.0, 1.0);
}
void main() {
  float c0 = coc(vUv);
  vec3 acc = texture2D(tDiffuse, vUv).rgb;
  float wsum = 1.0;
  float r = c0 * maxBlur;
  if (r > 0.5) {
    const float GA = 2.39996323;
    for (int i = 1; i < 24; i++) {
      float fi = float(i);
      float rr = sqrt(fi / 24.0) * r;
      vec2 off = vec2(cos(fi * GA), sin(fi * GA)) * rr / res;
      vec2 uv = vUv + off;
      float ci = coc(uv);
      float w = smoothstep(0.0, 0.25, ci + 0.05);   // 清晰的主体不往背景里渗
      acc += texture2D(tDiffuse, uv).rgb * w;
      wsum += w;
    }
  }
  gl_FragColor = vec4(acc / wsum, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  vec3 c = gl_FragColor.rgb;
  // 调色：明亮、略暖、饱和一点、轻 S 曲线
  float l = dot(c, vec3(0.299, 0.587, 0.114));
  c = mix(vec3(l), c, 1.12);
  c *= vec3(1.035, 1.0, 0.955);
  c = mix(c, smoothstep(0.0, 1.0, c), 0.22);
  c = c * 1.03 + 0.012;
  // 粉彩调（voxel）：降对比、抬暗部、轻微偏粉
  c = mix(c, c * 0.86 + 0.12 * vec3(1.02, 0.97, 1.0), pastel);
  // 柔和暗角
  vec2 q = (vUv - 0.5) * vec2(aspect, 1.0);
  c *= 1.0 - smoothstep(0.45, 1.05, length(q) * 1.2) * 0.32;
  gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
}`;

export class FilmPass {
  constructor(renderer, w, h) {
    this.renderer = renderer;
    const depth = new THREE.DepthTexture(w, h);
    depth.type = THREE.UnsignedIntType;
    this.rt = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, depthTexture: depth, samples: 4 });
    this.mat = new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG, depthTest: false, depthWrite: false,
      uniforms: {
        tDiffuse: { value: this.rt.texture }, tDepth: { value: depth }, cameraNear: { value: 0.1 }, cameraFar: { value: 1000 },
        focusDist: { value: 10 }, aperture: { value: 0.9 }, maxBlur: { value: 14 * w / 1080 }, aspect: { value: w / h },
        res: { value: new THREE.Vector2(w, h) }, tilt: { value: 0 }, pastel: { value: 0 },
      },
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, 2, 0, 0, 2], 2));
    this.quad = new THREE.Mesh(g, this.mat);
    this.quad.frustumCulled = false;
    this.scene = new THREE.Scene();
    this.scene.add(this.quad);
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  }

  render(scene, camera, focusPoint, aperture = 0.9, tilt = 0, pastel = 0) {
    const U = this.mat.uniforms;
    U.tilt.value = tilt; U.pastel.value = pastel;
    U.cameraNear.value = camera.near; U.cameraFar.value = camera.far;
    U.focusDist.value = Math.max(0.05, camera.position.distanceTo(focusPoint));
    U.aperture.value = aperture;
    const r = this.renderer;
    r.setRenderTarget(this.rt);
    r.render(scene, camera);
    r.setRenderTarget(null);
    r.render(this.scene, this.cam);
  }
}
