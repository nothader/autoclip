// 环境：city / highway / desert / ocean / sky / orbit / deep_space / lab / void。
// 主体沿 -z 前进；地面内容按块（chunk）循环生成，块 k 的内容只由 k 决定（确定性）。
import * as THREE from "three";
import { makeCar, std, hash, rng, skyDome, stars, canvasTex, facadeTexture, Chunks, palm, lamp, pedestrian,
  CAR_COLORS, cloudTex, earthTextures, makeEarth, addOvergrowth, addDebris } from "./common.js";

// ------------------------------------------------------------- city ---
function cityEnv(opts = {}) {
  const highway = !!opts.highway;
  const L = 48;
  const lanes = highway ? 4 : 2;            // 每个方向
  const laneW = 3.5;
  const roadL = -laneW * (lanes + 0.5), roadR = laneW * (lanes - 0.5);  // 主体在 x=0 的车道中心
  const roadW = roadR - roadL;
  const asphalt = std("#3b3e44", { roughness: 0.95 });
  const walk = std("#a7a49c", { roughness: 0.95 });
  const curb = std("#c8c5bd");
  const white = new THREE.MeshBasicMaterial({ color: 0xe9e9e4 });
  const yellow = new THREE.MeshBasicMaterial({ color: 0xd9b23a });

  const facadeCols = [
    ["#c9b79a", "#3b4652"], ["#9a5b45", "#2c343c"], ["#b9c0c6", "#33414d"], ["#e0d6c3", "#4b5866"],
    ["#7f8a94", "#25303a"], ["#d8c7a8", "#3d4954"], ["#a88f75", "#2e3842"], ["#cfd3d6", "#516170"],
  ];
  const awnings = ["#2f6e8f", "#9b2c2c", "#2f7a4a", "#d0a032", "#3a3a3a"];
  const facadeMats = [];
  for (let i = 0; i < 8; i++) {
    const [b, w] = facadeCols[i];
    facadeMats.push(facadeTexture(b, w, 100 + i, i % 2 === 0 ? awnings[i % awnings.length] : null));
  }

  const windowMats = [];
  const make = (vi) => {
    const r = rng(9000 + vi * 77);
    const g = new THREE.Group();
    const road = new THREE.Mesh(new THREE.PlaneGeometry(roadW, L), asphalt);
    road.rotation.x = -Math.PI / 2;
    road.position.set((roadL + roadR) / 2, 0, -L / 2);
    road.receiveShadow = true;
    g.add(road);
    // 车道线：中间双黄线（主体左侧），同向白色虚线
    for (const dx of [-0.12, 0.12]) {
      const y = new THREE.Mesh(new THREE.PlaneGeometry(0.12, L), yellow);
      y.rotation.x = -Math.PI / 2;
      y.position.set(-laneW / 2 + dx, 0.01, -L / 2);
      g.add(y);
    }
    for (let ln = 1; ln < lanes; ln++) for (const side of [1, -1]) {
      const xLine = side > 0 ? laneW / 2 + (ln - 1) * laneW : -laneW / 2 - ln * laneW;
      for (let d = 0; d < L; d += 12) {
        const m = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 5), white);
        m.rotation.x = -Math.PI / 2;
        m.position.set(xLine, 0.01, -d - 3);
        g.add(m);
      }
    }
    // 斑马线（部分块）
    if (!highway && vi % 3 === 0) {
      for (let x = roadL + 0.6; x < roadR - 0.4; x += 1.2) {
        const m = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 3.2), white);
        m.rotation.x = -Math.PI / 2;
        m.position.set(x, 0.012, -6);
        g.add(m);
      }
    }
    // 人行道 + 路缘
    const sideW = highway ? 3 : 5;
    for (const [x0, x1] of [[roadR, roadR + sideW], [roadL - sideW, roadL]]) {
      const s = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, 0.18, L), walk);
      s.position.set((x0 + x1) / 2, 0.09, -L / 2);
      s.receiveShadow = true;
      g.add(s);
      const cx = x0 === roadR ? x0 + 0.1 : x1 - 0.1;
      const c = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.2, L), curb);
      c.position.set(cx, 0.1, -L / 2);
      g.add(c);
    }
    // 楼
    for (const side of [1, -1]) {
      let z = 0;
      const xEdge = side > 0 ? roadR + sideW : roadL - sideW;
      while (z < L) {
        const w = 9 + r() * 9;
        const d = 10 + r() * 10;
        const h = highway ? 6 + r() * 14 : 10 + Math.pow(r(), 1.6) * 55;
        const fi = Math.floor(r() * facadeMats.length);
        const tex = facadeMats[fi].clone();
        tex.needsUpdate = true;
        tex.repeat.set(Math.max(1, Math.round(w / 6)), Math.max(1, Math.round(h / 12)));
        const glow = facadeMats[fi].userData.glow.clone();
        glow.needsUpdate = true;
        glow.repeat.copy(tex.repeat);
        const mat = std("#ffffff", { map: tex, emissiveMap: glow, emissive: 0xffffff, emissiveIntensity: 0 });
        windowMats.push(mat);
        const top = std(facadeCols[fi][0]);
        const b = new THREE.Mesh(new THREE.BoxGeometry(d, h, Math.min(w, L - z)), [mat, mat, top, top, mat, mat]);
        b.position.set(xEdge + side * (d / 2 + 0.5), h / 2, -z - Math.min(w, L - z) / 2);
        b.castShadow = true; b.receiveShadow = true;
        g.add(b);
        z += w + (r() < 0.2 ? 3 : 0);
      }
    }
    // 棕榈树、路灯
    for (let z = 4 + r() * 6; z < L; z += 12 + r() * 8) {
      for (const side of [1, -1]) {
        if (r() < 0.75) {
          const p = palm(0.9 + r() * 0.5);
          p.position.set(side > 0 ? roadR + 1.4 : roadL - 1.4, 0.18, -z);
          p.rotation.y = r() * 6;
          g.add(p);
        }
      }
    }
    for (const side of [1, -1]) {
      const l = lamp();
      l.position.set(side > 0 ? roadR + 0.6 : roadL - 0.6, 0.18, -L * 0.5 - r() * 10);
      l.rotation.y = side > 0 ? 0 : Math.PI;
      g.add(l);
    }
    addOvergrowth(g, r, roadL - 6, roadR + 6, L);
    addDebris(g, r, roadL, roadR, L);
    // 行人
    if (!highway) for (let i = 0; i < 14; i++) {
      const p = pedestrian(r);
      const side = r() < 0.5 ? 1 : -1;
      p.position.set(side > 0 ? roadR + 1.5 + r() * 3 : roadL - 1.5 - r() * 3, 0.18, -r() * L);
      p.rotation.y = r() < 0.5 ? 0 : Math.PI;
      g.add(p);
    }
    // 车：主体所在车道之外
    const laneXs = [];
    for (let i = 1; i < lanes; i++) laneXs.push(i * laneW);
    for (let i = 1; i <= lanes; i++) laneXs.push(-i * laneW);
    for (const lx of laneXs) {
      for (let z = r() * 10; z < L - 4; z += 7 + r() * (highway ? 6 : 14)) {
        if (r() < (highway ? 0.8 : 0.55)) {
          const car = makeCar(CAR_COLORS[Math.floor(r() * CAR_COLORS.length)]);
          car.position.set(lx + (r() - 0.5) * 0.4, 0, -z - 2.5);
          if (lx < 0) car.rotation.y = Math.PI;
          car.userData = { tag: "car", rank: r() };
          g.add(car);
        }
      }
    }
    return g;
  };

  const chunks = new Chunks(L, make, 8, 3, highway ? 9 : 7);
  const root = new THREE.Group();
  root.add(chunks.group);
  // 远处地面兜底
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), std(highway ? "#8f8a7c" : "#7d7a73"));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.02;
  root.add(ground);
  const sky = skyDome("#7f97b3", "#c9d3dc", "#a9adb0");
  root.add(sky);
  return {
    root, sky, windowMats, outdoor: true, defaults: { crowd: highway ? 0 : 0.45, traffic: highway ? 0.9 : 0.7 },
    fog: new THREE.Fog(highway ? 0xc6ccd0 : 0xbfc8d0, 60, highway ? 420 : 300),
    light: { sun: 2.4, hemi: 1.1, sunDir: [-0.5, 1, 0.35], sky: 0xdfe8f2, ground: 0x6d6a63 },
    update(fr, subjPos) { chunks.update(fr.z || 0); ground.position.x = subjPos.x; ground.position.z = subjPos.z; sky.position.copy(subjPos); },
  };
}

// ------------------------------------------------------------ desert ---
function desertEnv() {
  const L = 60;
  const sandTex = canvasTex(512, 512, (x, w, h) => {
    const r = rng(42);
    x.fillStyle = "#d4b48a"; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 6000; i++) { const v = r(); x.fillStyle = v > 0.5 ? `rgba(255,240,210,${r() * 0.15})` : `rgba(120,90,50,${r() * 0.12})`; x.fillRect(r() * w, r() * h, 2, 2); }
  });
  sandTex.repeat.set(40, 40);
  const sand = std("#ffffff", { map: sandTex, roughness: 1 });
  const asphalt = std("#45474b", { roughness: 0.95 });
  const white = new THREE.MeshBasicMaterial({ color: 0xe6e3da });
  const yellow = new THREE.MeshBasicMaterial({ color: 0xd2ad44 });
  const poleMat = std("#5a4a3a");
  const rockMat = std("#9a7b5e");
  const brush = std("#7d7a4e");

  const make = (vi) => {
    const r = rng(500 + vi * 31);
    const g = new THREE.Group();
    const road = new THREE.Mesh(new THREE.PlaneGeometry(9, L), asphalt);
    road.rotation.x = -Math.PI / 2;
    road.position.set(1.0, 0.01, -L / 2);
    road.receiveShadow = true;
    g.add(road);
    for (let d = 0; d < L; d += 12) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.15, 5.5), yellow);
      m.rotation.x = -Math.PI / 2; m.position.set(-1.9, 0.02, -d - 3);
      g.add(m);
    }
    for (const x of [-3.3, 5.3]) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.15, L), white);
      m.rotation.x = -Math.PI / 2; m.position.set(x, 0.02, -L / 2);
      g.add(m);
    }
    // 电线杆
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.15, 9, 6), poleMat);
    pole.position.set(9, 4.5, -L / 2);
    const bar = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.12, 0.12), poleMat);
    bar.position.set(9, 8.4, -L / 2);
    pole.castShadow = true;
    g.add(pole, bar);
    for (let i = 0; i < 10; i++) {
      const s = 0.3 + r() * 1.4;
      const isRock = r() < 0.4;
      const m = new THREE.Mesh(isRock ? new THREE.DodecahedronGeometry(s, 0) : new THREE.IcosahedronGeometry(s * 0.6, 0), isRock ? rockMat : brush);
      const side = r() < 0.5 ? -1 : 1;
      m.position.set(side * (7 + r() * 40), s * 0.3, -r() * L);
      m.castShadow = true;
      g.add(m);
    }
    return g;
  };
  const chunks = new Chunks(L, make, 6, 2, 9);
  const root = new THREE.Group();
  root.add(chunks.group);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(5000, 5000), sand);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  root.add(ground);
  // 远山 / 沙丘环（跟随主体，形成地平线）
  const dunes = new THREE.Group();
  const duneMat = std("#c7a57a", { roughness: 1 });
  const r = rng(77);
  for (let i = 0; i < 40; i++) {
    const a = (i / 40) * Math.PI * 2;
    const d = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), duneMat);
    const R = 700 + r() * 300;
    d.scale.set(120 + r() * 160, 25 + r() * 70, 120 + r() * 120);
    d.position.set(Math.cos(a) * R, -2, Math.sin(a) * R);
    dunes.add(d);
  }
  root.add(dunes);
  const sky = skyDome("#6f9fd0", "#d9e3e8", "#d6c3a3");
  root.add(sky);
  return {
    root, sky, outdoor: true,
    fog: new THREE.Fog(0xdcd6c8, 120, 1100),
    light: { sun: 3.0, hemi: 1.0, sunDir: [0.6, 1, 0.2], sky: 0xeaf2ff, ground: 0xb89a70 },
    update(fr, p) {
      chunks.update(fr.z || 0);
      ground.position.set(p.x, 0, p.z);
      sandTex.offset.set(p.x / 125, -p.z / 125);
      dunes.position.set(p.x, 0, p.z);
      sky.position.copy(p);
    },
  };
}

// ------------------------------------------------------------- ocean ---
function oceanEnv() {
  const seg = 120, size = 600;
  const geo = new THREE.PlaneGeometry(size, size, seg, seg);
  geo.rotateX(-Math.PI / 2);
  const base = geo.attributes.position.array.slice();
  const water = new THREE.Mesh(geo, std("#1f5f7d", { roughness: 0.25, metalness: 0.1, flatShading: true }));
  water.receiveShadow = true;
  const root = new THREE.Group();
  root.add(water);
  const sky = skyDome("#5b8fc7", "#cfe0ea", "#2b5d78");
  root.add(sky);
  return {
    root, sky, outdoor: true,
    fog: new THREE.Fog(0xbfd3de, 80, 700),
    light: { sun: 2.6, hemi: 1.0, sunDir: [-0.4, 0.8, -0.6], sky: 0xdcecff, ground: 0x1d4256 },
    update(fr, p) {
      water.position.set(p.x, 0, p.z);
      const a = geo.attributes.position.array, t = fr.t;
      for (let i = 0; i < a.length; i += 3) {
        const x = base[i] + p.x, z = base[i + 2] + p.z;
        a[i + 1] = -0.4 + Math.sin(x * 0.15 + t * 1.3) * 0.35 + Math.sin(z * 0.11 - t * 1.1) * 0.45 + Math.sin((x + z) * 0.31 + t * 2.0) * 0.12;
      }
      geo.attributes.position.needsUpdate = true;
      geo.computeVertexNormals();
      sky.position.copy(p);
    },
  };
}

// ---------------------------------------------------------- 云海 / sky ---
function skyEnv() {
  const L = 400;
  const tex = cloudTex();
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0.95 });
  const make = (vi) => {
    const r = rng(800 + vi * 13);
    const g = new THREE.Group();
    for (let i = 0; i < 26; i++) {
      const s = new THREE.Sprite(mat);
      const sc = 80 + r() * 160;
      s.scale.set(sc * 1.8, sc, 1);
      const x = (r() - 0.5) * 1400;
      s.position.set(Math.abs(x) < 120 ? x + Math.sign(x || 1) * 120 : x, -220 - r() * 160, -r() * L);
      g.add(s);
    }
    return g;
  };
  const chunks = new Chunks(L, make, 5, 2, 6);
  const root = new THREE.Group();
  root.add(chunks.group);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(20000, 20000), std("#6c7f6a"));
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -1500;
  root.add(ground);
  const sky = skyDome("#2c5f9e", "#a9c6e0", "#9fb2bf");
  root.add(sky);
  return {
    root, sky, outdoor: true,
    fog: new THREE.Fog(0xb7cadb, 400, 2600),
    light: { sun: 2.8, hemi: 1.0, sunDir: [0.3, 1, -0.4], sky: 0xe8f1ff, ground: 0x8899aa },
    update(fr, p) { chunks.update(fr.z || 0); ground.position.x = p.x; ground.position.z = p.z; sky.position.copy(p); },
  };
}

function orbitEnv() {
  const R = 700;
  const root = new THREE.Group();
  const st = stars();
  root.add(st);
  const earth = makeEarth(R);
  root.add(earth);
  return {
    root, fog: null, background: 0x000000,
    light: { sun: 3.2, hemi: 0.25, sunDir: [1, 0.6, 0.3], sky: 0x8899bb, ground: 0x000000 },
    update(fr, p) {
      // 主体在地球上方 ~60 单位处掠过，地球缓慢转动
      // 球心在正下方，任何朝向的镜头都能看到弧形地平线；本段内逐渐远离
      const k = fr.frac || 0;
      const h = 30 + 70 * k;
      earth.position.set(p.x, p.y - R - h, p.z);
      earth.rotation.x = (fr.z || 0) / R * 0.6 + 0.4;
      earth.rotation.y = 0.8;
      earth.userData.clouds.rotation.y = fr.t * 0.003;
      st.position.copy(p);
    },
  };
}

function deepSpaceEnv() {
  const root = new THREE.Group();
  const st = stars(6000, 3000, 11);
  root.add(st);
  const earth = makeEarth(60);
  root.add(earth);
  const moon = new THREE.Mesh(new THREE.SphereGeometry(16, 48, 32), std("#9a9a96", { roughness: 1, fog: false }));
  root.add(moon);
  const sun = new THREE.Sprite(new THREE.SpriteMaterial({ map: canvasTex(128, 128, (x) => {
    const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
    g.addColorStop(0, "rgba(255,250,235,1)"); g.addColorStop(0.15, "rgba(255,230,180,0.8)"); g.addColorStop(1, "rgba(255,200,120,0)");
    x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  }, false), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
  sun.scale.set(500, 500, 1);
  root.add(sun);
  return {
    root, fog: null, background: 0x000000,
    light: { sun: 3.0, hemi: 0.2, sunDir: [1, 0.3, 0.6], sky: 0x8899bb, ground: 0x000000 },
    update(fr, p) {
      const k = fr.frac || 0;
      earth.position.set(p.x - 40, p.y - 30, p.z + 250 + k * 900);   // 地球在身后渐远
      earth.rotation.y = fr.t * 0.05;
      moon.position.set(p.x + 220, p.y + 60, p.z - 900 + k * 500);
      sun.position.set(p.x + 1800, p.y + 900, p.z - 1500);
      st.position.copy(p);
    },
  };
}

function labEnv() {
  const root = new THREE.Group();
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), std("#e9e9ea", { roughness: 0.9 }));
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  root.add(floor);
  const grid = new THREE.GridHelper(4000, 800, 0xc9c9cc, 0xd8d8db);
  grid.position.y = 0.01;
  root.add(grid);
  return {
    root, fog: new THREE.Fog(0xf2f2f3, 40, 260), background: 0xf2f2f3,
    light: { sun: 2.2, hemi: 1.4, sunDir: [-0.3, 1, 0.5], sky: 0xffffff, ground: 0xcccccc },
    update(fr, p) {
      floor.position.set(p.x, 0, p.z);
      grid.position.set(p.x - (p.x % 5), 0.01, p.z - (p.z % 5));
    },
  };
}

function voidEnv() {
  const root = new THREE.Group();
  return { root, fog: null, background: 0x000000, light: { sun: 0.5, hemi: 0.3, sunDir: [0, 1, 0], sky: 0x222222, ground: 0 }, update() {} };
}

import {
  suburbEnv, parkEnv, fieldsEnv, forestEnv, mountainsEnv, volcanoEnv, coastEnv, outbackEnv, ancientEnv,
  interiorEnv, globeEnv, mapEnv,
} from "./envs.js";

const BUILDERS = {
  city: () => cityEnv(), highway: () => cityEnv({ highway: true }), desert: desertEnv, ocean: oceanEnv,
  sky: skyEnv, orbit: orbitEnv, deep_space: deepSpaceEnv, lab: labEnv, void: voidEnv,
  suburb: suburbEnv, park: parkEnv, fields: fieldsEnv, forest: forestEnv, mountains: mountainsEnv,
  volcano: volcanoEnv, coast: coastEnv, outback: outbackEnv, ancient: ancientEnv,
  interior: (e) => interiorEnv(e.room), globe: (e) => globeEnv(e.globe || {}), map: mapEnv,
};

// 时段 / 天象调色：天空三段色、太阳色/强度/高度、半球光、雾色、窗户亮度、星星
const PALETTES = {
  golden: { top: "#8a9ec0", mid: "#f0c89a", bottom: "#c9a27a", sun: "#ffc98a", sunI: 2.3, sunY: 0.32, hemiI: 0.8, hemiSky: "#ffe2c0", fog: "#e8c9a6", win: 0.15 },
  dusk: { top: "#25304f", mid: "#d98a6a", bottom: "#5a4a50", sun: "#ff9a6a", sunI: 1.2, sunY: 0.1, hemiI: 0.6, hemiSky: "#8a7aa0", fog: "#7a6070", win: 0.7, stars: 0.3 },
  night: { top: "#040814", mid: "#16223c", bottom: "#0c1018", sun: "#8fa6d8", sunI: 0.6, sunY: 0.6, hemiI: 0.42, hemiSky: "#4a5a88", fog: "#111a2e", win: 1.0, stars: 1 },
  dawn: { top: "#3d4a74", mid: "#f2b9a0", bottom: "#8a7a80", sun: "#ffd1b0", sunI: 1.3, sunY: 0.15, hemiI: 0.6, hemiSky: "#c8b8d0", fog: "#d8b8b0", win: 0.4, stars: 0.15 },
};
const SKY_EVENTS = {
  red: { top: "#2a0806", mid: "#c2381e", bottom: "#4a140c", sun: "#ff5a2a", sunI: 1.6, hemiI: 0.6, hemiSky: "#ff8060", fog: "#7a2414" },
  dark: { top: "#000000", mid: "#07080a", bottom: "#000000", sun: "#556070", sunI: 0.08, hemiI: 0.08, hemiSky: "#202530", fog: "#030405", win: 0.6, stars: 0.6 },
  meteors: { stars: 1 },
  aurora: { stars: 1 },
};
const WEATHER = {
  overcast: { top: "#8a939b", mid: "#c3c8cc", sunI: 0.9, hemiI: 1.0, fog: "#b9bfc4", fogK: 0.7 },
  rain: { top: "#5a636b", mid: "#8d969d", sunI: 0.5, hemiI: 0.8, fog: "#7d868d", fogK: 0.45 },
  storm: { top: "#272d35", mid: "#4a525a", sunI: 0.25, hemiI: 0.5, fog: "#3a4148", fogK: 0.35 },
  snow: { top: "#aab3bb", mid: "#dfe4e8", sunI: 0.9, hemiI: 1.2, fog: "#dfe4e8", fogK: 0.4 },
  ash: { top: "#4a4540", mid: "#7a726a", sunI: 0.4, hemiI: 0.6, fog: "#6d665e", fogK: 0.25 },
  fog: { top: "#b9c0c5", mid: "#cfd4d8", sunI: 0.9, hemiI: 1.1, fog: "#c9ced2", fogK: 0.12 },
  dust: { top: "#a07a50", mid: "#d0a46a", sunI: 1.2, hemiI: 0.9, fog: "#c49a68", fogK: 0.3 },
};

function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

class Atmosphere {
  // 天气粒子（雨/雪/灰/尘）、流星、夜空星星；全部是 t 的函数
  constructor(scene) {
    const N = 2400;
    this.N = N;
    const lg = new THREE.BufferGeometry();
    lg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 6), 3));
    this.rain = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xc8d4e0, transparent: true, opacity: 0.45, depthWrite: false }));
    this.rain.frustumCulled = false;
    const pg = new THREE.BufferGeometry();
    pg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    this.flakes = new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xffffff, size: 0.12, transparent: true, opacity: 0.9, depthWrite: false }));
    this.flakes.frustumCulled = false;
    const M = 40;
    this.M = M;
    const mg = new THREE.BufferGeometry();
    mg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(M * 6), 3));
    this.meteors = new THREE.LineSegments(mg, new THREE.LineBasicMaterial({ color: 0xffe2b0, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
    this.meteors.frustumCulled = false;
    this.nightStars = stars(3000, 2500, 21);
    this.nightStars.material.transparent = true;
    scene.add(this.rain, this.flakes, this.meteors, this.nightStars);
  }
  update(spec, fr, cam, outdoor, starsLevel) {
    const w = outdoor ? spec.weather : "clear";
    const t = fr.t, N = this.N;
    this.rain.visible = w === "rain" || w === "storm";
    if (this.rain.visible) {
      const a = this.rain.geometry.attributes.position.array;
      for (let i = 0; i < N; i++) {
        const x = cam.x + (rnd(i) - 0.5) * 60, z = cam.z + (rnd(i + 9) - 0.5) * 60;
        const y = cam.y + 20 - ((t * 28 + rnd(i + 3) * 40) % 40);
        a[i * 6] = x; a[i * 6 + 1] = y; a[i * 6 + 2] = z;
        a[i * 6 + 3] = x + 0.08; a[i * 6 + 4] = y - 0.9; a[i * 6 + 5] = z;
      }
      this.rain.geometry.attributes.position.needsUpdate = true;
    }
    const flaky = { snow: [0xffffff, 1.6, 0.12], ash: [0x8a837b, 1.0, 0.16], dust: [0xc49a68, 0.6, 0.08] }[w];
    this.flakes.visible = !!flaky;
    if (flaky) {
      const a = this.flakes.geometry.attributes.position.array;
      for (let i = 0; i < N; i++) {
        a[i * 3] = cam.x + ((rnd(i) - 0.5) * 50 + Math.sin(t * 0.7 + i) * 0.8);
        a[i * 3 + 1] = cam.y + 15 - ((t * flaky[1] + rnd(i + 3) * 30) % 30);
        a[i * 3 + 2] = cam.z + (rnd(i + 9) - 0.5) * 50 + (w === "dust" ? ((t * 6 + rnd(i) * 50) % 50) - 25 : 0);
      }
      this.flakes.geometry.attributes.position.needsUpdate = true;
      this.flakes.material.color.setHex(flaky[0]);
      this.flakes.material.size = flaky[2];
    }
    this.meteors.visible = spec.sky === "meteors";
    if (this.meteors.visible) {
      const a = this.meteors.geometry.attributes.position.array;
      for (let i = 0; i < this.M; i++) {
        const life = 1.4 + rnd(i) * 1.2;
        const k = ((t + rnd(i + 5) * 10) % life) / life;
        const sx = cam.x + (rnd(i + 1) - 0.3) * 600, sy = cam.y + 180 + rnd(i + 2) * 200, sz = cam.z - 400 - rnd(i + 4) * 300;
        const dx = -260, dy = -320;
        const x = sx + dx * k, y = sy + dy * k;
        a[i * 6] = x; a[i * 6 + 1] = y; a[i * 6 + 2] = sz;
        a[i * 6 + 3] = x - dx * 0.12; a[i * 6 + 4] = y - dy * 0.12; a[i * 6 + 5] = sz;
      }
      this.meteors.geometry.attributes.position.needsUpdate = true;
    }
    this.nightStars.visible = outdoor && starsLevel > 0;
    this.nightStars.material.opacity = starsLevel;
    this.nightStars.position.copy(cam);
  }
}

export class World {
  constructor(scene) {
    this.scene = scene;
    this.envs = {};
    this.active = null;
    this.hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
    this.sun = new THREE.DirectionalLight(0xffffff, 2.5);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    this.sun.shadow.bias = -0.0004;
    this.sun.shadow.normalBias = 0.02;
    scene.add(this.hemi, this.sun, this.sun.target);
    this.atmo = new Atmosphere(scene);
    this.spec = {};
  }
  key(name, spec) {
    if (name === "interior") return `interior:${spec.room || "office"}`;
    if (name === "globe") return `globe:${JSON.stringify(spec.globe || {})}`;
    return name;
  }
  use(name, spec = {}) {
    const key = this.key(name, spec);
    this.spec = spec;
    if (this.active === key) return this.envs[key];
    if (this.active) this.scene.remove(this.envs[this.active].root);
    if (!this.envs[key]) {
      const b = BUILDERS[name] || BUILDERS.void;
      this.envs[key] = b(spec);
      const e = this.envs[key];
      if (e.sky) e.skyBase = ["top", "mid", "bottom"].map((k) => e.sky.material.uniforms[k].value.clone());
      if (e.fog) e.fogBase = { color: e.fog.color.clone(), near: e.fog.near, far: e.fog.far };
    }
    const env = this.envs[key];
    this.scene.add(env.root);
    this.scene.fog = env.fog;
    this.scene.background = env.background !== undefined ? new THREE.Color(env.background) : null;
    this.active = key;
    return env;
  }
  // 每帧：时段/天气/天象 → 灯光、天空、雾；人群/车辆/荒废/损毁 → 显隐
  applyMods(env, spec, fr, beat, cam) {
    const L = env.light;
    let sunColor = new THREE.Color(0xffffff), sunI = L.sun, hemiI = L.hemi, hemiSky = new THREE.Color(L.sky);
    let sunDir = new THREE.Vector3(...L.sunDir);
    let win = 0, starsLevel = 0;
    this.exposure = 1.0;
    if (env.sky) {
      const [t0, m0, b0] = env.skyBase;
      env.sky.material.uniforms.top.value.copy(t0);
      env.sky.material.uniforms.mid.value.copy(m0);
      env.sky.material.uniforms.bottom.value.copy(b0);
    }
    if (env.fog) { env.fog.color.copy(env.fogBase.color); env.fog.near = env.fogBase.near; env.fog.far = env.fogBase.far; }
    const apply = (p) => {
      if (!p) return;
      if (env.sky) {
        const u = env.sky.material.uniforms;
        if (p.top) u.top.value.set(p.top);
        if (p.mid) u.mid.value.set(p.mid);
        if (p.bottom) u.bottom.value.set(p.bottom);
      }
      if (p.sun) sunColor.set(p.sun);
      if (p.sunI !== undefined) sunI = Math.min(sunI, p.sunI * (L.sun / 2.5));
      if (p.sunY !== undefined) sunDir.y = p.sunY;
      if (p.hemiI !== undefined) hemiI = p.hemiI * (L.hemi / 1.0);
      if (p.hemiSky) hemiSky.set(p.hemiSky);
      if (p.fog && env.fog) env.fog.color.set(p.fog);
      if (p.fogK && env.fog) { env.fog.near *= p.fogK; env.fog.far = Math.max(env.fog.far * p.fogK, env.minFogFar || 0); }
      if (p.win !== undefined) win = Math.max(win, p.win);
      if (p.stars !== undefined) starsLevel = Math.max(starsLevel, p.stars);
    };
    if (env.outdoor) {
      this.exposure = { night: 1.7, dusk: 1.25, dawn: 1.1 }[spec.time] || 1.0;
      if (spec.sky === "dark") this.exposure = 1.4;
      apply(PALETTES[spec.time]);
      apply(WEATHER[spec.weather]);
      apply(SKY_EVENTS[spec.sky]);
    } else if (env.globe) {
      this.exposure = 1.35;
    } else if (env.interior) {
      const night = spec.time === "night" || spec.time === "dusk";
      env.winM.color.set(night ? 0x101828 : (spec.time === "golden" ? 0xf2c89a : 0xcfe3f2));
      env.panelM.emissiveIntensity = spec.lights_off ? 0.04 : 0.9;
      hemiI = spec.lights_off ? 0.25 : L.hemi;
      if (spec.sky === "red") hemiSky.set(0xff8060);
    }
    if (spec.weather === "storm" && env.outdoor && fr.lightning) { hemiI += 2.5 * fr.lightning; if (env.sky) env.sky.material.uniforms.mid.value.lerp(new THREE.Color(0xdfe6ff), fr.lightning); }
    if (spec.lights_off) win = 0;
    for (const m of env.windowMats || []) m.emissiveIntensity = win * 1.2;
    this.sun.color.copy(sunColor);
    this.sun.intensity = sunI;
    this.hemi.intensity = hemiI;
    this.hemi.color.copy(hemiSky);
    this.hemi.groundColor.set(L.ground);
    this.sunDir = sunDir.normalize();
    if (this.scene.fog !== env.fog) this.scene.fog = env.fog;
    // 显隐：行人 / 车 / 植被 / 碎片 / 路灯
    const dflt = env.defaults || {};
    const crowd = spec.empty ? 0 : (spec.crowd ?? dflt.crowd ?? 0.3);
    const traffic = spec.traffic ?? dflt.traffic ?? 0.5;
    const vanish = beat && beat.effects.includes("vanish") ? Math.min(1, (fr.frac || 0) * 1.25) : 0;
    const over = spec.overgrown || 0, dmg = spec.damage || 0;
    env.root.traverse((o) => {
      const u = o.userData;
      if (!u || !u.tag) return;
      if (u.tag === "ped") o.visible = u.rank < crowd && !(vanish > 0 && u.rank / crowd < vanish);
      else if (u.tag === "car") o.visible = u.rank < traffic;
      else if (u.tag === "green") o.visible = u.rank < over;
      else if (u.tag === "debris") o.visible = u.rank < dmg;
      else if (u.tag === "lamp" && o.material) { o.material.emissive.set(0xffd9a0); o.material.emissiveIntensity = win * 2; }
    });
    this.atmo.update(spec, fr, cam, !!env.outdoor, starsLevel);
  }
  update(fr, subjPos, scale = 1, beat = null, camPos = null) {
    const env = this.envs[this.active];
    env.update(fr, subjPos, beat);
    this.applyMods(env, this.spec || {}, fr, beat, camPos || subjPos);
    // 阴影相机跟随主体
    const ext = 30 * Math.max(1, scale);
    const sc = this.sun.shadow.camera;
    sc.left = -ext; sc.right = ext; sc.top = ext; sc.bottom = -ext; sc.near = 1; sc.far = 400 * Math.max(1, scale);
    sc.updateProjectionMatrix();
    this.sun.position.copy(subjPos).addScaledVector(this.sunDir, 150 * Math.max(1, scale));
    this.sun.target.position.copy(subjPos);
  }
  get current() { return this.envs[this.active]; }
}
