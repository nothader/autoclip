// 叠加层：HUD / 标注 / 字幕 / 卡片 / 片头 / 结尾图表 / 问句。
// 每帧的文本与透明度都由 Python 侧算好（plan.frames[i]），这里只负责摆放。
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

export function layout(width) {
  const s = width / 1080;
  $("#ov").style.transform = `scale(${s})`;
}

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
    setText(cap, "cap", fr.cap.text);
    cap.style.opacity = fr.cap.a;
    cap.style.top = fr.sec === "chart" ? "1560px" : "1090px";
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

  // 片头
  const intro = $("#intro");
  show(intro, !!fr.intro);
  if (fr.intro) {
    const lines = fr.intro.lines.map((l, i) => {
      const cls = i === fr.intro.accent ? "acc" : (i === 0 ? "small" : "");
      return `<div class="ln ${cls}">${esc(l)}</div>`;
    }).join("");
    setHTML(intro, "intro", `<div class="logo"><i style="height:12px"></i><i style="height:22px"></i><i style="height:32px"></i><i style="height:46px"></i></div>${lines}`);
    intro.style.opacity = fr.intro.a;
  }

  // 问句
  const q = $("#question");
  show(q, !!fr.question);
  if (fr.question) {
    setText(q.querySelector(".q"), "q", fr.question.text);
    q.style.opacity = fr.question.a;
  }

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
