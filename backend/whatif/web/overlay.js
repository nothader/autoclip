// 叠加层（Block POV）：顶部衬线标题、左侧进度块、斜体小字幕、新闻横幅、屏幕、眼皮、黑底金色问句结尾。
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

export function layout(width, plan) {
  const land = !!(plan && plan.width > plan.height);
  document.body.classList.toggle("land", land);
  $("#ov").style.transform = `scale(${width / (land ? 1920 : 1080)})`;
  if (plan && plan.theme && plan.theme.accent) document.documentElement.style.setProperty("--accent", plan.theme.accent);
}

// "What if you fell into a *coma*?" → 强调词着色
const accentize = (t) => esc(t).replace(/\*([^*]+)\*/g, "<em>$1</em>");

export function drawOverlay(fr, plan) {
  // 顶部衬线标题（前 3.5 秒）+ 左侧进度块（小标签 / 粗体大值 / 小副标签；危险变红，高潮居中放大）
  const bt = $("#btitle");
  show(bt, !!fr.btitle);
  if (fr.btitle) { setHTML(bt, "btitle", accentize(fr.btitle.text)); bt.style.opacity = fr.btitle.a; }
  const trk = $("#trk");
  show(trk, !!fr.tracker && !fr.end);
  if (fr.tracker) {
    const k = fr.tracker;
    setText(trk.querySelector(".l"), "trkl", k.label || "");
    setText(trk.querySelector(".v"), "trkv", k.value || "");
    setText(trk.querySelector(".s"), "trks", k.sub || "");
    trk.classList.toggle("alert", !!k.alert);
    trk.classList.toggle("big", !!k.big);
    trk.style.opacity = k.a;
  }
  // 斜体衬线小字幕；引语带出处小字
  const cap = $("#cap");
  show(cap, !!fr.cap);
  if (fr.cap) {
    setHTML(cap, "cap", esc(fr.cap.text) + (fr.cap.ref ? `<span class="by">${esc(fr.cap.ref)}</span>` : ""));
    cap.style.opacity = fr.cap.a;
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

  // 结尾卡：黑底，居中衬线标题 + 金色斜体问句
  const en = $("#end");
  show(en, !!fr.end);
  if (fr.end) {
    setHTML(en, "end", `<div class="bt">${esc((plan.intro && plan.intro.title || plan.title || "").replace(/\*/g, ""))}</div>` +
      `<div class="bq">${esc((fr.end.lines || []).join(" "))}</div>`);
    en.style.opacity = fr.end.a;
  }
  const tr = fr.tr && !fr.tr.out ? fr.tr : null;   // 转场：dip 从黑场淡入；flash 白闪
  $("#darken").style.opacity = Math.max(fr.darken || 0, fr.end ? fr.end.a : 0, tr && tr.k === "dip" ? (1 - tr.p) ** 1.5 : 0);
  $("#flash").style.opacity = Math.max(fr.flash || 0, tr && tr.k === "flash" ? (1 - tr.p) ** 1.8 : 0);
  drawPov(fr, plan);
}

function drawPov(fr, plan) {
  const lt = $("#lidT"), lb = $("#lidB");
  const p = plan.pov && fr.pov;
  show(lt, !!p && p.lid > 0.001); show(lb, !!p && p.lid > 0.001);
  const beat = fr.b !== undefined && plan.beats ? plan.beats[fr.b] : null;
  const tun = beat && beat.effects.includes("tunnel") ? 0.75 + 0.25 * Math.sin((fr.t || 0) * Math.PI * 2 / 0.85) : 0;
  $("#tunnel").style.opacity = p ? tun.toFixed(3) : "0";
  if (!p) return;
  if (p.lid > 0.001) {
    // 眼皮：上下各一片弧形，lid=1 时在画面中线合上
    // edge = 上眼皮弧形最低点的 y；全闭时再多压一个弧高，让眼角也合上
    const land = plan.width > plan.height, h = land ? 680 : 1180, mid = land ? 540 : 960, arc = land ? 200 : 300;
    const edge = -40 + p.lid * (mid + 40) + p.lid ** 3 * arc;
    lt.style.transform = `translateY(${(edge - h).toFixed(1)}px)`;
    lb.style.transform = `translateY(${(h - edge).toFixed(1)}px)`;
  }
}

