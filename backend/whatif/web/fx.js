// 电影感特效：爆炸、火花、彩带、闪电、光束。都放在镜头注视点附近（保证在画面里），是 lt 的纯函数。
import * as THREE from "three";

function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

// 圆形柔边贴图：让烟 / 火花是软圆点而不是方块
const DOT = (() => {
  const c = document.createElement("canvas"); c.width = c.height = 64;
  const g = c.getContext("2d"), r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(0.35, "rgba(255,255,255,0.8)"); r.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = r; g.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c); return t;
})();

const SPARK_N = 420, CONF_N = 260, DEBRIS_N = 90, SMOKE_N = 60;

export class CineFX {
  constructor(scene) {
    this.root = new THREE.Group();
    scene.add(this.root);
    // 爆炸：火球 + 白热核心 + 冲击环 + 碎块 + 烟
    this.fire = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), new THREE.MeshBasicMaterial({ color: 0xff7a1a, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.core = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), new THREE.MeshBasicMaterial({ color: 0xfff3c4, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    this.ring = new THREE.Mesh(new THREE.RingGeometry(0.85, 1, 64), new THREE.MeshBasicMaterial({ color: 0xffd8a8, transparent: true, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
    this.ring.rotation.x = -Math.PI / 2;
    this.debris = this.points(DEBRIS_N, 0x2b2118, 0.22, THREE.NormalBlending);
    this.smoke = this.points(SMOKE_N, 0x5c5f66, 1.6, THREE.NormalBlending, 0.55);
    // 火花
    this.sparks = this.points(SPARK_N, 0xffd43b, 0.2, THREE.AdditiveBlending);
    // 彩带：实例化小方片，每片自己的颜色
    const cols = [0xe03131, 0x1c7ed6, 0xf59f00, 0x2f9e44, 0xae3ec9, 0xf8f9fa, 0x0ca678];
    this.conf = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.16, 0.26), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }), CONF_N);
    for (let i = 0; i < CONF_N; i++) this.conf.setColorAt(i, new THREE.Color(cols[i % cols.length]));
    this.conf.frustumCulled = false;
    // 闪电：3 条折线
    this.bolts = [0, 1, 2].map(() => {
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(24 * 3), 3));
      const l = new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xe7f5ff, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
      l.frustumCulled = false;
      return l;
    });
    // 光束：从上方斜照下来的锥形光
    this.rays = [0, 1, 2, 3, 4].map((k) => {
      const m = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 24, 1, true), new THREE.MeshBasicMaterial({ color: 0xfff4d6, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
      return m;
    });
    this.root.add(this.fire, this.core, this.ring, this.debris, this.smoke, this.sparks, this.conf, ...this.bolts, ...this.rays);
    this.hideAll();
  }

  points(n, color, size, blending, opacity = 1) {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    const p = new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: DOT, transparent: true, opacity, blending, depthWrite: false }));
    p.frustumCulled = false;
    return p;
  }

  hideAll() { for (const o of this.root.children) o.visible = false; }

  // center: 注视点；S: 场景尺度；返回闪光强度（给画面整体提亮用）
  update(fr, beat, center, S, camera) {
    this.hideAll();
    const fx = new Set(beat ? beat.effects : []);
    if (!fx.size) return 0;
    const lt = fr.lt || 0, t = fr.t || 0, seed = (beat && beat.i) || 0;
    let flash = 0;
    if (fx.has("explosion")) flash = Math.max(flash, this.explosion(lt, center, S, seed));
    if (fx.has("sparks")) this.sparkFx(lt, center, S, seed);
    if (fx.has("confetti")) this.confetti(lt, center, S, camera);
    if (fx.has("lightning")) flash = Math.max(flash, this.lightning(fr, center, S, seed));
    if (fx.has("rays")) this.rayFx(t, center, S);
    return flash;
  }

  explosion(lt, c, S, seed) {
    const k = Math.min(1, lt / 0.9), e = 1 - (1 - k) ** 3;
    this.fire.visible = this.core.visible = this.ring.visible = this.debris.visible = this.smoke.visible = true;
    this.fire.position.copy(c); this.core.position.copy(c);
    this.fire.scale.setScalar((0.3 + 3.2 * e) * S);
    this.fire.material.opacity = Math.max(0, 0.95 - lt * 0.32);
    this.fire.material.color.setHSL(0.07 - 0.05 * k, 1, 0.55 - 0.2 * k);
    this.core.scale.setScalar((0.2 + 1.6 * e) * S);
    this.core.material.opacity = Math.max(0, 1 - lt * 1.1);
    const rk = Math.min(1, lt / 1.4);
    this.ring.position.set(c.x, c.y - 0.8 * S, c.z);
    this.ring.scale.setScalar((0.5 + 11 * rk) * S);
    this.ring.material.opacity = Math.max(0, 0.8 * (1 - rk));
    const a = this.debris.geometry.attributes.position.array;
    for (let i = 0; i < DEBRIS_N; i++) {
      const th = rnd(seed * 31 + i) * Math.PI * 2, up = 0.4 + rnd(i + 7) * 1.2, sp = (3 + rnd(i + 3) * 6) * S;
      const tt = Math.min(lt, 2.4);
      a[i * 3] = c.x + Math.cos(th) * sp * tt * 0.6;
      a[i * 3 + 1] = Math.max(c.y - 1.1 * S, c.y + up * sp * tt * 0.6 - 4.9 * S * tt * tt);
      a[i * 3 + 2] = c.z + Math.sin(th) * sp * tt * 0.6;
    }
    this.debris.geometry.attributes.position.needsUpdate = true;
    this.debris.material.size = 0.25 * S;
    const sm = this.smoke.geometry.attributes.position.array;
    for (let i = 0; i < SMOKE_N; i++) {
      const th = rnd(i + 50) * Math.PI * 2, r = (0.5 + rnd(i + 51) * 3.5) * S * Math.min(1, lt / 1.5);
      sm[i * 3] = c.x + Math.cos(th) * r;
      sm[i * 3 + 1] = c.y + (rnd(i + 52) * 2 + lt * 1.2) * S;
      sm[i * 3 + 2] = c.z + Math.sin(th) * r;
    }
    this.smoke.geometry.attributes.position.needsUpdate = true;
    this.smoke.material.size = (1.2 + lt * 0.5) * S;
    this.smoke.material.opacity = Math.min(0.55, lt * 0.6) * Math.max(0, 1 - (lt - 2.5) / 2);
    return Math.max(0, 1 - lt / 0.35);
  }

  sparkFx(lt, c, S, seed) {
    this.sparks.visible = true;
    const a = this.sparks.geometry.attributes.position.array;
    for (let i = 0; i < SPARK_N; i++) {
      const life = 0.6 + rnd(i + seed) * 0.6, age = ((lt + rnd(i + 9) * life) % life);
      const th = rnd(i + 3) * Math.PI * 2, sp = (1.5 + rnd(i + 5) * 3) * S, up = 0.5 + rnd(i + 11) * 1.5;
      a[i * 3] = c.x + Math.cos(th) * sp * age;
      a[i * 3 + 1] = c.y + up * sp * age - 4.9 * S * age * age;
      a[i * 3 + 2] = c.z + Math.sin(th) * sp * age;
    }
    this.sparks.geometry.attributes.position.needsUpdate = true;
    this.sparks.material.size = 0.22 * S;
  }

  confetti(lt, c, S, camera) {
    this.conf.visible = true;
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sc = new THREE.Vector3(S, S, S), pos = new THREE.Vector3();
    for (let i = 0; i < CONF_N; i++) {
      const fall = 0.8 + rnd(i + 2) * 0.9, h = 9 * S;
      const y = c.y + h * 0.6 - ((lt * fall * S + rnd(i + 4) * h) % h);
      pos.set(c.x + (rnd(i) - 0.5) * 12 * S + Math.sin(lt * 2 + i) * 0.3 * S, y, c.z + (rnd(i + 6) - 0.5) * 8 * S);
      e.set(lt * (2 + rnd(i + 8) * 4) + i, lt * 3 + i * 0.7, lt * (1 + rnd(i + 10) * 3));
      q.setFromEuler(e);
      m.compose(pos, q, sc);
      this.conf.setMatrixAt(i, m);
    }
    this.conf.instanceMatrix.needsUpdate = true;
  }

  lightning(fr, c, S, seed) {
    const li = fr.lightning || 0;
    if (li <= 0) return 0;
    this.bolts.forEach((b, k) => {
      b.visible = k === 0 || li > 0.5;
      const a = b.geometry.attributes.position.array;
      const x0 = c.x + (rnd(seed * 5 + k) - 0.5) * 14 * S, z0 = c.z - (6 + rnd(seed + k * 3) * 10) * S;
      for (let j = 0; j < 24; j++) {
        const f = j / 23;
        a[j * 3] = x0 + (rnd(seed * 97 + k * 31 + j) - 0.5) * 2.2 * S * (j ? 1 : 0) + f * (rnd(k + 2) - 0.5) * 4 * S;
        a[j * 3 + 1] = c.y + (22 - 23 * f) * S;
        a[j * 3 + 2] = z0;
      }
      b.geometry.attributes.position.needsUpdate = true;
      b.material.opacity = li;
    });
    return li * 0.9;
  }

  rayFx(t, c, S) {
    this.rays.forEach((r, k) => {
      r.visible = true;
      const len = 26 * S;
      r.scale.set((1.2 + k * 0.4) * S, len, (1.2 + k * 0.4) * S);
      r.position.set(c.x + (k - 2) * 2.4 * S, c.y + len * 0.42, c.z - 4 * S);
      r.rotation.set(0, 0, 0.32 + k * 0.03);
      r.material.opacity = 0.05 + 0.035 * Math.sin(t * 0.9 + k * 1.7);
    });
  }
}
