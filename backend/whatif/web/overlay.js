// 叠加层：HUD / 标注 / 字幕 / 卡片 / 片头 / 结尾图表 / 问句。
// 每帧的文本与透明度都由 Python 侧算好（plan.frames[i]），这里只负责摆放。
import { icon } from "./icons.js";

const $ = (s) => document.querySelector(s);
const show = (el, on) => el.classList.toggle("hidden", !on);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let cache = {};
function setHTML(el, key, html) {
  if (cache[key] !== html) { el.innerHTML = html; cache[key] = html; }
}
function setText(el, key, text) {
  if (cache[key] !== text) { el.textContent = text; cache[key] = text; }
}

export function layout(width, plan) {
  const land = !!(plan && plan.width > plan.height);
  document.body.classList.toggle("land", land);
  if (land) $("#map").setAttribute("preserveAspectRatio", "xMidYMid slice");
  const s = width / (land ? 1920 : 1080);
  $("#ov").style.transform = `scale(${s})`;
  if (plan && plan.theme && plan.theme.accent) document.documentElement.style.setProperty("--accent", plan.theme.accent);
}

// "What if all *women* disappeared?" → 强调词
const accentize = (t) => esc(t).replace(/\*([^*]+)\*/g, "<em>$1</em>");

export function drawOverlay(fr, plan) {
  // HUD
  const hud = $("#hud");
  show(hud, !!fr.hud);
  if (fr.hud) {
    const h = fr.hud;
    setText(hud.querySelector(".head"), "head", h.head);
    setText(hud.querySelector(".n"), "n", h.value);
    setText(hud.querySelector(".u"), "u", h.unit);
    hud.querySelector(".val").classList.toggle("over", !!h.over);
    setText(hud.querySelector(".sub"), "sub", h.sub);
    const right = h.right.map(([k, v]) => `<div class="k">${esc(k)}</div><div class="v">${esc(v)}</div>`).join("")
      + `<div class="tag ${h.tag_style}">${esc(h.tag)}</div>`;
    setHTML(hud.querySelector(".r"), "right", right);
    const bar = hud.querySelector(".bar");
    show(bar, !!h.bar);
    if (h.bar) {
      bar.querySelector(".f").style.width = `${Math.max(0.4, h.bar.frac * 100)}%`;
      bar.querySelector(".f").style.background = h.bar.frac >= 1 ? "var(--warn)" : "var(--accent)";
      setText(bar.querySelector(".lab"), "barlab", h.bar.label);
    }
  }

  // 标注
  const co = $("#callout");
  show(co, !!fr.callout);
  if (fr.callout) {
    setText(co.querySelector(".t"), "cot", fr.callout.title);
    setText(co.querySelector(".s"), "cos", fr.callout.sub || "");
    co.classList.toggle("note", fr.callout.kind === "note");
    co.style.opacity = fr.callout.a;
    co.style.transform = `translateX(${(1 - fr.callout.a) * -24}px)`;
  }

  // 字幕
  const cap = $("#cap");
  show(cap, !!fr.cap);
  if (fr.cap) {
    setHTML(cap, "cap", esc(fr.cap.text) + (fr.cap.ref ? `<span class="ref">${esc(fr.cap.ref)}</span>` : ""));
    cap.style.opacity = fr.cap.a;
    cap.style.top = plan.width > plan.height ? "" :   // 横屏：CSS 贴底
      fr.sec === "chart" ? "1560px" : `${(plan.layout && plan.layout.cap_top) || 1090}px`;
  }

  // 卡片
  const card = $("#card");
  show(card, !!fr.card);
  if (fr.card) {
    setText(card.querySelector(".t"), "cardt", fr.card.title);
    setHTML(card.querySelector(".rows"), "cardr",
      fr.card.rows.map(([k, v]) => `<div class="row"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join(""));
    card.classList.toggle("warning", fr.card.tone === "warning");
    card.style.opacity = fr.card.a;
    card.style.transform = `scale(${0.94 + 0.06 * fr.card.a})`;
  }

  // 片头：stack（逐行大字）或 title / chapter（图标 + 一句话标题）
  const ti = $("#title");
  const titleStyle = fr.intro && fr.intro.style !== "stack";
  show(ti, !!titleStyle);
  if (titleStyle) {
    const it = fr.intro;
    setHTML(ti, "title", `${it.icon && it.icon !== "none" ? `<div class="icon">${icon(it.icon)}</div>` : ""}`
      + (it.kicker ? `<div class="kick caps">${esc(it.kicker)}</div>` : "")
      + `<div class="t">${accentize(it.title || it.lines.join(" "))}</div>`
      + (it.subtitle ? `<div class="sub caps">${esc(it.subtitle)}</div>` : ""));
    ti.classList.toggle("chapter", it.style === "chapter");
    ti.style.opacity = it.a;
  }
  const intro = $("#intro");
  show(intro, !!fr.intro && !titleStyle);
  if (fr.intro && !titleStyle) {
    const lines = fr.intro.lines.map((l, i) => {
      const cls = i === fr.intro.accent ? "acc" : (i === 0 ? "small" : "");
      return `<div class="ln ${cls}">${esc(l)}</div>`;
    }).join("");
    setHTML(intro, "intro", `<div class="logo"><i style="height:12px"></i><i style="height:22px"></i><i style="height:32px"></i><i style="height:46px"></i></div>${lines}`);
    intro.style.opacity = fr.intro.a;
  }

  show($("#question"), false);

  // 时钟
  const ck = $("#clock");
  show(ck, !!fr.clock);
  if (fr.clock) {
    setText(ck.querySelector(".lab"), "cklab", fr.clock.label || "");
    setText(ck.querySelector(".v"), "ckv", fr.clock.value);
    setText(ck.querySelector(".s"), "cks", fr.clock.sub || "");
    ck.style.opacity = fr.clock.a;
    ck.style.transform = `translateY(${(1 - fr.clock.a) * 12}px)`;
  }

  // 统计大字
  const st = $("#stat");
  show(st, !!fr.stat);
  if (fr.stat) {
    setText(st.querySelector(".v"), "stv", fr.stat.value);
    setText(st.querySelector(".l"), "stl", fr.stat.label || "");
    st.style.opacity = fr.stat.a;
  }

  // 章节条 + 时间标签
  const chEl = $("#chapter");
  show(chEl, !!fr.chapter);
  if (fr.chapter) {
    const c = fr.chapter;
    setHTML(chEl.querySelector(".bar"), "chbar", [...Array(c.n)].map((_, i) =>
      `<div class="seg ${i < c.i ? "done" : i === c.i ? "cur" : ""}"><i></i><b>${i + 1}</b></div>`).join(""));
    setText(chEl.querySelector(".k"), "chk", `PART ${c.i + 1} OF ${c.n}`);
    setText(chEl.querySelector(".t"), "cht", c.title);
  }
  const chip = $("#chip");
  show(chip, !!fr.chip);
  if (fr.chip) {
    setText(chip, "chip", fr.chip);
    chip.classList.toggle("alone", !fr.chapter);
  }

  // 信息框
  const tip = $("#tip");
  show(tip, !!fr.tooltip);
  if (fr.tooltip) {
    setText(tip.querySelector(".l"), "tipl", fr.tooltip.label);
    setText(tip.querySelector(".x"), "tipx", fr.tooltip.text);
    tip.style.opacity = fr.tooltip.a;
    tip.style.top = fr.chapter ? "330px" : (fr.hud ? "430px" : "260px");
  }

  // 新闻横幅
  const bn = $("#banner");
  show(bn, !!fr.banner);
  if (fr.banner) {
    setText(bn.querySelector(".k"), "bnk", fr.banner.kicker);
    setText(bn.querySelector(".t"), "bnt", fr.banner.title);
    setText(bn.querySelector(".s"), "bns", fr.banner.subtitle || "");
    show(bn.querySelector(".s"), !!fr.banner.subtitle);
    bn.style.opacity = fr.banner.a;
    bn.style.transform = `translateX(${(1 - fr.banner.slide) * -120}px)`;
  }

  // 屏幕
  const sc = $("#screen");
  show(sc, !!fr.screen);
  if (fr.screen) {
    const x = fr.screen;
    let html = "";
    if (x.kind === "phone_call") {
      const pulse = 1 + 0.06 * Math.abs(Math.sin(x.lt * 4));
      html = `<div class="phone"><div class="clk">${esc(x.rows && x.rows[0] ? x.rows[0][1] : "")}</div>`
        + `<div class="av" style="transform:scale(${pulse.toFixed(3)})">${esc((x.title || "?").slice(0, 1))}</div>`
        + `<div class="nm">${esc(x.title)}</div><div class="st">${esc(x.subtitle || "incoming call")}</div>`
        + (x.badge ? `<div class="bd">${esc(x.badge)}</div>` : "")
        + `<div class="btns"><i style="background:#e5484d"></i><i style="background:#30a46c"></i></div></div>`;
    } else if (x.kind === "vitals") {
      const ph = x.lt * 2.2;
      let d = "M0,45";
      for (let i = 0; i <= 104; i++) {
        const u = (i / 104 * 3 + ph) % 1;
        const yy = u > 0.42 && u < 0.46 ? 5 : u > 0.46 && u < 0.5 ? 80 : u > 0.5 && u < 0.53 ? 30 : 45;
        d += ` L${i * 5},${yy}`;
      }
      html = `<div class="vitals">` + (x.rows || []).map(([k, v], i) =>
        `<div class="row"><div><span>${esc(k)}</span>${i === 0 ? `<svg viewBox="0 0 520 90"><path d="${d}" stroke="#3ddc84" stroke-width="4" fill="none"/></svg>` : ""}</div>`
        + `<b style="color:${["#3ddc84", "#4cc3ff", "#ffd166", "#ff6b6b"][i % 4]}">${esc(v)}</b></div>`).join("") + `</div>`;
    } else {
      html = `<div class="board"><div class="t">${esc(x.title)}</div>` + (x.subtitle ? `<div class="s">${esc(x.subtitle)}</div>` : "")
        + (x.rows || []).map(([k, v]) => `<div class="row"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("") + `</div>`;
    }
    setHTML(sc, "screen", html);
    sc.style.opacity = x.a;
    sc.style.top = plan.width > plan.height ? "" : x.kind === "phone_call" ? "430px" : "620px";
  }

  // 结尾卡
  const en = $("#end");
  show(en, !!fr.end);
  if (fr.end) {
    const e = fr.end;
    let html = "";
    if (e.kind === "question" || e.kind === "tagline") {
      html += `<div class="icon" style="width:70px;height:70px;margin:0 auto 24px">${icon(e.icon === "none" ? "" : "bars")}</div>`;
    }
    if (e.kicker) html += `<div class="k caps">${esc(e.kicker)}</div>`;
    if (e.kind === "title" && e.title) html += `<div class="t">${accentize(e.title)}</div>`;
    html += (e.lines || []).map((l, i) => `<div class="ln ${i === e.accent_line ? "acc" : ""}">${esc(l)}</div>`).join("");
    if (e.sub) html += `<div class="sub caps">${esc(e.sub)}</div>`;
    setHTML(en, "end", html);
    en.className = `shadow ${e.kind}`;
    en.style.opacity = e.a;
  }
  $("#darken").style.opacity = fr.darken || 0;
  const mp = $("#map");
  show(mp, !!fr.map);
  if (fr.map) drawMap(mp, fr.map);

  // 图表
  const ch = $("#chart");
  show(ch, !!fr.chart && !!plan.chart);
  if (fr.chart && plan.chart) {
    drawChart(ch, plan.chart, fr.chart.p);
    ch.style.opacity = fr.chart.a;
  }

  $("#flash").style.opacity = fr.flash || 0;
}

function fmtAxis(v) {
  if (v >= 1e9) return `${+(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `${+(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${+(v / 1e3).toFixed(1)}K`;
  return `${+v.toFixed(2)}`;
}

function drawChart(svg, c, p) {
  const X0 = 150, X1 = 960, Y0 = 1300, Y1 = 520;
  const steps = c.steps;
  const tMax = steps[steps.length - 1][0] + (steps.length > 1 ? steps[1][0] - steps[0][0] : 1);
  const vals = steps.map((s) => s[1]).concat(c.refs.map((r) => r.value)).filter((v) => v > 0);
  const lo = Math.log10(Math.min(...vals)) - 0.2, hi = Math.log10(Math.max(...vals)) + 0.25;
  const x = (t) => X0 + (t / tMax) * (X1 - X0);
  const y = (v) => Y0 - ((Math.log10(Math.max(v, 1e-12)) - lo) / (hi - lo)) * (Y0 - Y1);
  let html = "";
  html += `<text x="540" y="400" text-anchor="middle" fill="#fff" font-size="26" letter-spacing="4" font-weight="600" font-family="Inter">${esc(c.title)}</text>`;
  html += `<text x="540" y="440" text-anchor="middle" fill="rgba(255,255,255,0.55)" font-size="18" letter-spacing="3" font-family="Inter">${esc(c.subtitle)}</text>`;
  html += `<line x1="${X0}" y1="${Y0}" x2="${X1}" y2="${Y0}" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>`;
  html += `<line x1="${X0}" y1="${Y0}" x2="${X0}" y2="${Y1 - 20}" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>`;
  html += `<text x="${(X0 + X1) / 2}" y="${Y0 + 48}" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="16" letter-spacing="3" font-family="Inter">SECONDS</text>`;
  for (const r of c.refs) {
    const yy = y(r.value);
    const col = r.limit ? "rgba(255,255,255,0.75)" : "rgba(255,255,255,0.4)";
    html += `<line x1="${X0}" y1="${yy}" x2="${X1}" y2="${yy}" stroke="${col}" stroke-width="2" stroke-dasharray="8 8"/>`;
    const anchorLeft = r.limit;
    html += `<text x="${anchorLeft ? X0 + 8 : X1 - 8}" y="${yy - 10}" text-anchor="${anchorLeft ? "start" : "end"}" fill="${col}" font-size="15" letter-spacing="2" font-family="Inter" font-weight="600">${esc(r.label)}</text>`;
  }
  // 阶梯折线，按进度揭示
  const tEnd = p * tMax;
  let d = "";
  let lastX = X0, lastY = y(steps[0][1]);
  for (let i = 0; i < steps.length; i++) {
    const [t0, v] = steps[i];
    const t1 = i + 1 < steps.length ? steps[i + 1][0] : tMax;
    if (t0 > tEnd) break;
    const yy = y(v);
    d += (d ? `L${x(t0)},${yy}` : `M${x(t0)},${yy}`);
    const te = Math.min(t1, tEnd);
    d += `L${x(te)},${yy}`;
    lastX = x(te); lastY = yy;
  }
  html += `<path d="${d}" fill="none" stroke="var(--accent)" stroke-width="4" stroke-linejoin="miter"/>`;
  html += `<circle cx="${lastX}" cy="${lastY}" r="7" fill="#fff"/>`;
  if (c.breach && tEnd >= c.breach.sim) {
    const bx = x(c.breach.sim), by = y(c.refs.find((r) => r.limit)?.value || 1);
    html += `<g stroke="var(--warn)" stroke-width="5"><line x1="${bx - 14}" y1="${by - 14}" x2="${bx + 14}" y2="${by + 14}"/><line x1="${bx + 14}" y1="${by - 14}" x2="${bx - 14}" y2="${by + 14}"/></g>`;
    html += `<text x="${X1 - 8}" y="${by - 50}" text-anchor="end" fill="var(--warn)" font-size="17" letter-spacing="2" font-weight="600" font-family="Inter">${esc(c.breach.label)}</text>`;
    html += `<text x="${X1 - 8}" y="${by - 26}" text-anchor="end" fill="rgba(255,255,255,0.5)" font-size="14" letter-spacing="2" font-family="Inter">NOT ALLOWED FOR ANYTHING WITH MASS</text>`;
  }
  svg.innerHTML = html;
}

// ---------------------------------------------------------------- 地图 ---
function mrand(seed) { let s = seed >>> 0 || 1; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
const MAP_STYLES = {
  dark: { bg: "#10161e", grid: "rgba(255,255,255,0.05)", road: "rgba(255,255,255,0.22)", major: "#c9a24a", land: "#141c26", text: "#e8eef4" },
  satellite: { bg: "#3f4f32", grid: "rgba(0,0,0,0.08)", road: "rgba(240,235,220,0.45)", major: "#e8d8a8", land: "#55663f", text: "#ffffff" },
  paper: { bg: "#e9e1cf", grid: "rgba(0,0,0,0.06)", road: "rgba(80,70,60,0.35)", major: "#a8552e", land: "#ddd3bd", text: "#2b2622" },
};
let mapBase = null;
function drawMap(svg, m) {
  const st = MAP_STYLES[m.style] || MAP_STYLES.dark;
  const X = (x) => 40 + x * 1000, Y = (y) => 260 + y * 1400;
  // 缓慢推近
  const z = 1 + 0.06 * Math.min(1, m.p);
  if (!mapBase || mapBase.style !== m.style) {
    const r = mrand(42);
    let base = `<rect width="1080" height="1920" fill="${st.bg}"/>`;
    for (let i = 0; i < 1080; i += 60) base += `<line x1="${i}" y1="0" x2="${i}" y2="1920" stroke="${st.grid}"/>`;
    for (let j = 0; j < 1920; j += 60) base += `<line x1="0" y1="${j}" x2="1080" y2="${j}" stroke="${st.grid}"/>`;
    for (let i = 0; i < 9; i++) {
      const y0 = r() * 1920, y1 = y0 + (r() - 0.5) * 600;
      base += `<path d="M-20,${y0} C 360,${y0 + (r() - 0.5) * 300} 720,${y1 + (r() - 0.5) * 300} 1100,${y1}" stroke="${st.road}" stroke-width="${2 + r() * 3}" fill="none"/>`;
    }
    for (let i = 0; i < 5; i++) {
      const x0 = r() * 1080;
      base += `<path d="M${x0},-20 C ${x0 + (r() - 0.5) * 300},640 ${x0 + (r() - 0.5) * 300},1280 ${x0 + (r() - 0.5) * 200},1940" stroke="${st.road}" stroke-width="${2 + r() * 2}" fill="none"/>`;
    }
    const yMaj = 400 + r() * 1100;
    base += `<path d="M-20,${yMaj} L1100,${yMaj + (r() - 0.5) * 200}" stroke="${st.major}" stroke-width="5" fill="none" opacity="0.8"/>`;
    mapBase = { style: m.style, html: base };
  }
  let html = `<g transform="translate(540 960) scale(${z.toFixed(4)}) translate(-540 -960)">${mapBase.html}`;
  if (m.zone) {
    const R = (m.zone_radius || 0.12) * 1000 * (0.9 + 0.1 * Math.sin(m.t * 3));
    html += `<defs><radialGradient id="zg"><stop offset="0" stop-color="var(--accent)" stop-opacity="0.75"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0.15"/></radialGradient></defs>`;
    html += `<circle cx="${X(m.zone.x)}" cy="${Y(m.zone.y)}" r="${R}" fill="url(#zg)" stroke="var(--accent)" stroke-width="3"/>`;
    if (m.zone.text) html += mapLabel(X(m.zone.x), Y(m.zone.y) + R + 34, m.zone.text, st, true);
  }
  if (m.path && m.path.length > 1) {
    const pts = m.path.map((q) => [X(q.x), Y(q.y)]);
    const seg = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); total += d; }
    let left = total * Math.min(1, m.p * 1.1);
    let d = `M${pts[0][0]},${pts[0][1]}`, head = pts[0];
    for (let i = 1; i < pts.length && left > 0; i++) {
      const k = Math.min(1, left / seg[i - 1]);
      head = [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * k, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * k];
      d += ` L${head[0]},${head[1]}`;
      left -= seg[i - 1];
    }
    html += `<path d="${d}" stroke="#ffffff" stroke-width="5" fill="none" stroke-linecap="round"/>`;
    html += `<circle cx="${head[0]}" cy="${head[1]}" r="12" fill="#fff"/><circle cx="${head[0]}" cy="${head[1]}" r="${20 + 8 * Math.sin(m.t * 5)}" fill="none" stroke="#fff" stroke-opacity="0.5" stroke-width="2"/>`;
    const last = m.path[m.path.length - 1];
    if (last.text) html += mapLabel(head[0], head[1] - 34, last.text, st, false);
  }
  for (const l of m.labels || []) html += mapLabel(X(l.x), Y(l.y), l.text, st, false);
  html += "</g>";
  svg.innerHTML = html;
}
function mapLabel(x, y, text, st, accent) {
  const w = Math.max(60, text.length * 12 + 26);
  return `<g><rect x="${x - w / 2}" y="${y - 18}" width="${w}" height="34" rx="6" fill="rgba(8,10,14,0.82)" stroke="${accent ? "var(--accent)" : "rgba(255,255,255,0.6)"}" stroke-width="1.5"/>`
    + `<text x="${x}" y="${y + 6}" text-anchor="middle" fill="${st.text === "#2b2622" ? "#fff" : st.text}" font-family="Inter" font-weight="600" font-size="16" letter-spacing="2">${esc(text.toUpperCase())}</text></g>`;
}
