// 通用小工具：确定性随机数、星空、星云天空、云层、canvas 纹理。
import * as THREE from "three";

export function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

export function stars(n = 4000, radius = 3000, seed = 7) {
  const r = rng(seed);
  const p = new Float32Array(n * 3), c = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const u = r() * 2 - 1, th = r() * Math.PI * 2, s = Math.sqrt(1 - u * u);
    p[i * 3] = s * Math.cos(th) * radius; p[i * 3 + 1] = u * radius; p[i * 3 + 2] = s * Math.sin(th) * radius;
    const b = 0.35 + Math.pow(r(), 3) * 0.65;
    c[i * 3] = b; c[i * 3 + 1] = b; c[i * 3 + 2] = b * (0.9 + r() * 0.2);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(p, 3));
  g.setAttribute("color", new THREE.BufferAttribute(c, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ size: 2.2, sizeAttenuation: false, vertexColors: true, fog: false, depthWrite: false }));
  pts.renderOrder = -9;
  return pts;
}

export function spaceSky(radius = 900, seed = 3) {
  const g = new THREE.Group();
  const [c1, c2] = NEBULA_PALETTES[Math.abs(seed) % NEBULA_PALETTES.length];
  const mat = new THREE.ShaderMaterial({
    uniforms: { c1: { value: new THREE.Color(c1) }, c2: { value: new THREE.Color(c2) }, sd: { value: (seed % 17) * 1.37 } },
    vertexShader: `varying vec3 vP; void main(){ vP=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 c1; uniform vec3 c2; uniform float sd; varying vec3 vP;
      float h(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
      float n(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),
                   mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      float fbm(vec3 p){ float a=0.5, s=0.0; for(int k=0;k<5;k++){ s+=a*n(p); p*=2.03; a*=0.5; } return s; }
      void main(){
        vec3 d = normalize(vP);
        float band = exp(-pow((d.y - 0.35 * d.x) * 3.2, 2.0));
        float a = fbm(d * 2.6 + sd), b = fbm(d * 4.1 - sd + 3.0);
        vec3 col = vec3(0.025, 0.035, 0.075) + vec3(0.03, 0.03, 0.06) * (1.0 - abs(d.y));
        col += c1 * smoothstep(0.48, 0.85, a) * 0.55;
        col += c2 * smoothstep(0.52, 0.9, b) * 0.45;
        col += vec3(0.55, 0.52, 0.62) * band * (0.18 + 0.45 * b);
        gl_FragColor = vec4(col, 1.0);
      }`,
    side: THREE.BackSide, depthWrite: false, depthTest: false, fog: false,
  });
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(radius, 48, 24), mat);
  sphere.renderOrder = -10;
  g.add(sphere, stars(5000, radius * 0.9, seed + 17));
  return g;
}

export function skyClouds(radius = 800, tint = "#ffffff", seed = 5, n = 16) {
  CLOUD_TEX ??= canvasTex(256, 128, (x) => {
    for (let k = 0; k < 7; k++) {
      const cx = 50 + k * 26 + Math.sin(k * 2.3) * 10, cy = 70 + Math.cos(k * 1.7) * 12, r = 34 + (k % 3) * 10;
      const gr = x.createRadialGradient(cx, cy, 0, cx, cy, r);
      gr.addColorStop(0, "rgba(255,255,255,0.95)"); gr.addColorStop(1, "rgba(255,255,255,0)");
      x.fillStyle = gr; x.fillRect(0, 0, 256, 128);
    }
  }, false);
  const r = rng(seed), g = new THREE.Group();
  const col = new THREE.Color("#ffffff").lerp(new THREE.Color(tint), 0.25);
  for (let i = 0; i < n; i++) {
    const az = r() * Math.PI * 2, el = (4 + r() * 26) * Math.PI / 180;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: CLOUD_TEX, color: col, transparent: true, opacity: 0.55 + r() * 0.35, depthWrite: false, fog: false }));
    sp.position.set(Math.cos(az) * Math.cos(el) * radius, Math.sin(el) * radius, Math.sin(az) * Math.cos(el) * radius);
    const w = 160 + r() * 220;
    sp.scale.set(w, w * 0.45, 1);
    sp.renderOrder = -8;
    g.add(sp);
  }
  return g;
}

export function canvasTex(w, h, draw, repeat = true) {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  draw(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  t.anisotropy = 4;
  return t;
}
