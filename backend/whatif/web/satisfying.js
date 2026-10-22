// 分屏下半部分的"解压循环"画面：小球沿彩色台阶一路弹跳下行，经过的台阶会亮起。
// 和主画面一样是时间 t 的纯函数（可乱序、多进程渲染）。
import * as THREE from "three";

const STEP = 1.25;       // 台阶间距（米）
const SPEED = 2.6;       // 每秒跳过的台阶数
const POOL = 46;

export class Satisfying {
  constructor() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color("#1b1630");
    this.scene.fog = new THREE.Fog("#1b1630", 14, 34);
    this.camera = new THREE.PerspectiveCamera(55, 1, 0.1, 200);
    this.scene.add(new THREE.HemisphereLight("#ffffff", "#3a2a5a", 1.4));
    const sun = new THREE.DirectionalLight("#ffffff", 1.6);
    sun.position.set(3, 8, 4);
    this.scene.add(sun);
    this.tiles = [];
    const geo = new THREE.BoxGeometry(1.1, 0.22, 1.1);
    for (let i = 0; i < POOL; i++) {
      const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: 0.45, emissive: "#000000" }));
      this.scene.add(m);
      this.tiles.push(m);
    }
    this.ball = new THREE.Mesh(new THREE.SphereGeometry(0.32, 32, 24), new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: 0.15, metalness: 0.1 }));
    this.scene.add(this.ball);
    this.trail = [];
    for (let i = 0; i < 8; i++) {
      const s = new THREE.Mesh(new THREE.SphereGeometry(0.32 * (1 - i * 0.1), 16, 12),
        new THREE.MeshBasicMaterial({ color: "#ffffff", transparent: true, opacity: 0.25 * (1 - i / 8) }));
      this.scene.add(s);
      this.trail.push(s);
    }
  }

  // 第 i 个台阶的位置（蜿蜒向下）
  tilePos(i) {
    return new THREE.Vector3(Math.sin(i * 0.55) * 1.6 + Math.sin(i * 0.17) * 0.8, -i * 0.42, -i * STEP);
  }

  ballPos(t) {
    const f = t * SPEED;
    const i = Math.floor(f), u = f - i;
    const a = this.tilePos(i), b = this.tilePos(i + 1);
    const p = a.clone().lerp(b, u);
    p.y += 0.36 + Math.sin(u * Math.PI) * 0.9;   // 每一跳的抛物线
    return p;
  }

  update(t, aspect, accent) {
    const f = t * SPEED, cur = Math.floor(f);
    for (let k = 0; k < POOL; k++) {
      const i = cur - 6 + k;
      const m = this.tiles[k];
      m.position.copy(this.tilePos(i));
      const hue = ((i * 0.045) % 1 + 1) % 1;
      const passed = i <= cur;
      m.material.color.setHSL(hue, 0.72, passed ? 0.66 : 0.5);
      m.material.emissive.setHSL(hue, 0.8, i === cur ? 0.35 : passed ? 0.12 : 0.0);
      const land = i === cur ? Math.max(0, 1 - (f - cur) * 4) : 0;   // 落地瞬间压一下
      m.scale.set(1 + land * 0.12, 1 - land * 0.35, 1 + land * 0.12);
    }
    const p = this.ballPos(t);
    this.ball.position.copy(p);
    this.ball.material.color.set(accent || "#ffffff");
    this.trail.forEach((s, j) => s.position.copy(this.ballPos(t - (j + 1) * 0.035)));
    this.camera.aspect = aspect;
    this.camera.position.set(p.x * 0.5, p.y + 3.4, p.z + 4.2);
    this.camera.lookAt(p.x * 0.8, p.y - 2.2, p.z - 4.0);
    this.camera.updateProjectionMatrix();
  }
}
