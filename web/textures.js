// Procedural surface textures (canvas) so floors, walls and streets aren't flat colour.
// tex: planks | tiles | bricks | asphalt | grass | carpet | concrete | marble | stripes | noise | sidewalk | wallpaper | fabric | road
import * as THREE from 'three';

function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function hsl(hex) { const c = new THREE.Color(hex); const o = {}; c.getHSL(o); return o; }
function col(h, s, l, a = 1) { return `hsla(${(h * 360).toFixed(1)},${(s * 100).toFixed(1)}%,${(Math.min(Math.max(l, 0), 1) * 100).toFixed(1)}%,${a})`; }

const base = new Map();
// Each texture covers `tile` metres; returns {map, bump}
export function surface(kind, color) {
  const key = kind + color;
  if (base.has(key)) return base.get(key);
  const N = 512, cv = document.createElement('canvas'); cv.width = cv.height = N; const c = cv.getContext('2d');
  const bm = document.createElement('canvas'); bm.width = bm.height = N; const b = bm.getContext('2d');
  const { h, s, l } = hsl(color); const R = rng(kind.length * 977 + Math.round(l * 1000));
  c.fillStyle = color; c.fillRect(0, 0, N, N); b.fillStyle = '#808080'; b.fillRect(0, 0, N, N);
  const speckle = (n, amp, size = 2) => { for (let i = 0; i < n; i++) { const v = (R() - 0.5) * amp; c.fillStyle = col(h, s, l + v, 0.5); c.fillRect(R() * N, R() * N, size, size); } };
  let tile = 1;
  switch (kind) {
    case 'planks': {   // wood floor, 4 boards across, staggered joints
      tile = 1.6; const rows = 6, rh = N / rows;
      for (let r = 0; r < rows; r++) {
        const off = R() * N;
        for (let k = -1; k < 2; k++) {
          const x0 = off + k * N * 0.9, w = N * 0.9; const dl = (R() - 0.5) * 0.12;
          c.fillStyle = col(h, s * (0.9 + R() * 0.2), l + dl); c.fillRect(x0, r * rh, w, rh);
          for (let g = 0; g < 14; g++) { c.strokeStyle = col(h, s, l + dl - 0.06 - R() * 0.05, 0.35); c.lineWidth = 1 + R() * 1.5; c.beginPath(); const yy = r * rh + R() * rh; c.moveTo(x0, yy); c.bezierCurveTo(x0 + w * 0.3, yy + (R() - 0.5) * 8, x0 + w * 0.6, yy + (R() - 0.5) * 8, x0 + w, yy + (R() - 0.5) * 6); c.stroke(); }
          b.fillStyle = '#202020'; b.fillRect(x0 - 1, r * rh, 3, rh);
          c.fillStyle = col(h, s, l - 0.2, 0.7); c.fillRect(x0 - 1, r * rh, 2, rh);
        }
        c.fillStyle = col(h, s, l - 0.22, 0.8); c.fillRect(0, r * rh, N, 2); b.fillStyle = '#202020'; b.fillRect(0, r * rh - 1, N, 4);
      }
      break;
    }
    case 'tiles': case 'sidewalk': {
      tile = kind === 'sidewalk' ? 2.4 : 1.2; const n = kind === 'sidewalk' ? 2 : 4, sz = N / n;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { c.fillStyle = col(h, s, l + (R() - 0.5) * 0.05); c.fillRect(i * sz, j * sz, sz, sz); }
      speckle(3000, 0.12, 2);
      c.strokeStyle = col(h, s * 0.6, l - 0.18, 0.9); c.lineWidth = kind === 'sidewalk' ? 5 : 4;
      b.strokeStyle = '#151515'; b.lineWidth = 7;
      for (let i = 0; i <= n; i++) { for (const g of [c, b]) { g.beginPath(); g.moveTo(i * sz, 0); g.lineTo(i * sz, N); g.moveTo(0, i * sz); g.lineTo(N, i * sz); g.stroke(); } }
      break;
    }
    case 'bricks': {
      tile = 1.2; const rows = 8, rh = N / rows, bw = N / 4;
      c.fillStyle = col(h, 0.05, 0.75); c.fillRect(0, 0, N, N);
      for (let r = 0; r < rows; r++) for (let k = -1; k < 5; k++) {
        const x = k * bw + (r % 2) * bw / 2; c.fillStyle = col(h, s, l + (R() - 0.5) * 0.12); c.fillRect(x + 3, r * rh + 3, bw - 6, rh - 6);
        b.fillStyle = '#b0b0b0'; b.fillRect(x + 3, r * rh + 3, bw - 6, rh - 6);
      }
      speckle(2500, 0.15, 2); break;
    }
    case 'asphalt': case 'road': {
      tile = 3; speckle(16000, 0.2, 2); speckle(3000, 0.3, 1);
      for (let i = 0; i < 6; i++) { c.strokeStyle = col(h, s, l - 0.06, 0.5); c.lineWidth = 2; c.beginPath(); let x = R() * N, y = R() * N; c.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (R() - 0.5) * 60; y += (R() - 0.5) * 60; c.lineTo(x, y); } c.stroke(); }
      break;
    }
    case 'grass': {
      tile = 2; for (let i = 0; i < 9000; i++) { c.strokeStyle = col(h + (R() - 0.5) * 0.03, s, l + (R() - 0.5) * 0.18, 0.6); c.lineWidth = 1.5; const x = R() * N, y = R() * N; c.beginPath(); c.moveTo(x, y); c.lineTo(x + (R() - 0.5) * 4, y - 4 - R() * 6); c.stroke(); }
      break;
    }
    case 'carpet': case 'fabric': {
      tile = kind === 'fabric' ? 0.6 : 1.0; speckle(26000, 0.08, 2);
      for (let y = 0; y < N; y += 4) { c.fillStyle = col(h, s, l - 0.03, 0.15); c.fillRect(0, y, N, 1); }
      break;
    }
    case 'concrete': {
      tile = 3; speckle(9000, 0.08, 3); speckle(3000, 0.16, 1);
      for (let i = 0; i < 40; i++) { c.fillStyle = col(h, s, l + (R() - 0.5) * 0.06, 0.25); c.beginPath(); c.arc(R() * N, R() * N, 10 + R() * 50, 0, 7); c.fill(); }
      c.fillStyle = col(h, s, l - 0.15, 0.6); c.fillRect(0, 0, N, 2); c.fillRect(0, 0, 2, N); b.fillStyle = '#303030'; b.fillRect(0, 0, N, 3); b.fillRect(0, 0, 3, N);
      break;
    }
    case 'marble': {
      tile = 1.5; for (let i = 0; i < 18; i++) { c.strokeStyle = col(h, s * 0.4, l - 0.12 - R() * 0.1, 0.35); c.lineWidth = 1 + R() * 2.5; c.beginPath(); let x = R() * N, y = 0; c.moveTo(x, y); while (y < N) { x += (R() - 0.5) * 40; y += 20 + R() * 30; c.lineTo(x, y); } c.stroke(); }
      break;
    }
    case 'stripes': case 'wallpaper': {
      tile = 1.0; const n = kind === 'wallpaper' ? 10 : 6;
      for (let i = 0; i < n; i++) if (i % 2) { c.fillStyle = col(h, s, l - 0.05, 1); c.fillRect(i * N / n, 0, N / n, N); }
      if (kind === 'wallpaper') for (let i = 0; i < 60; i++) { c.fillStyle = col(h, s, l + 0.07, 0.6); c.beginPath(); c.arc((i % 8) * 64 + 32, Math.floor(i / 8) * 64 + 32, 6, 0, 7); c.fill(); }
      break;
    }
    case 'paint': case 'noise': default: {
      tile = 2; speckle(12000, 0.035, 3); break;
    }
  }
  const map = new THREE.CanvasTexture(cv); map.colorSpace = THREE.SRGBColorSpace; map.wrapS = map.wrapT = THREE.RepeatWrapping; map.anisotropy = 4;
  const bump = new THREE.CanvasTexture(bm); bump.wrapS = bump.wrapT = THREE.RepeatWrapping;
  const r = { map, bump, tile }; base.set(key, r); return r;
}
