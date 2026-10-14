// 标题卡 / 结尾卡用的小图标（64×64，描边用 currentColor，强调部分用 var(--accent)）。
const A = "var(--accent)";
const W = "currentColor";
export const ICONS = {
  bars: `<rect x="8" y="40" width="9" height="16" fill="${W}" opacity=".7"/><rect x="21" y="30" width="9" height="26" fill="${W}" opacity=".7"/><rect x="34" y="20" width="9" height="36" fill="${W}" opacity=".7"/><rect x="47" y="8" width="9" height="48" fill="${A}"/>`,
  people: `<circle cx="22" cy="12" r="6" fill="${W}"/><path d="M14 22h16v18h-4v18h-8V40h-4z" fill="${W}"/><circle cx="43" cy="12" r="6" fill="${A}"/><path d="M36 22h14l5 22h-6v14h-8V44h-6z" fill="${A}"/>`,
  person: `<circle cx="32" cy="12" r="7" fill="${W}"/><path d="M22 23h20v20h-5v17h-10V43h-5z" fill="${W}"/>`,
  earth: `<circle cx="32" cy="32" r="24" fill="#2f6fb3"/><path d="M18 20c6-2 10 2 9 7s-7 5-6 11-3 8-6 6c-4-8-2-19 3-24zM38 14c5 1 10 5 12 11-4 1-6-2-9 0s0 7-4 8-5-5-3-9-2-7 4-10zM40 44c3-1 7 0 8 3-3 4-7 7-11 8 0-4 0-9 3-11z" fill="#5f9e55"/><circle cx="32" cy="32" r="24" fill="none" stroke="${A}" stroke-width="2"/>`,
  sun: `<circle cx="32" cy="32" r="13" fill="${A}"/>${[...Array(12)].map((_, i) => { const a = i * Math.PI / 6; return `<line x1="${32 + Math.cos(a) * 18}" y1="${32 + Math.sin(a) * 18}" x2="${32 + Math.cos(a) * 26}" y2="${32 + Math.sin(a) * 26}" stroke="${A}" stroke-width="3.5" stroke-linecap="round"/>`; }).join("")}`,
  moon: `<circle cx="32" cy="32" r="22" fill="#d9d6cc"/><circle cx="24" cy="26" r="4" fill="#b9b5a8"/><circle cx="40" cy="38" r="6" fill="#b9b5a8"/><circle cx="38" cy="22" r="3" fill="#b9b5a8"/><path d="M14 30l12 4 6-10 8 12 10-2" fill="none" stroke="${A}" stroke-width="2.5"/>`,
  volcano: `<path d="M6 58l18-30h16l18 30z" fill="#6b5b4d"/><path d="M24 28h16l-3 6h-10z" fill="${A}"/><path d="M26 22c-6-4-4-12 4-12 2-6 12-6 14 0 7 0 9 9 2 12z" fill="#9a948c"/>`,
  tornado: `${[0, 1, 2, 3, 4, 5].map((i) => `<rect x="${8 + i * 3.5}" y="${8 + i * 8.5}" width="${48 - i * 7}" height="5" rx="2.5" fill="${i === 0 ? A : W}" opacity="${1 - i * 0.08}"/>`).join("")}`,
  wave: `<path d="M4 44c8 0 10-22 26-22 10 0 14 10 8 16 8 2 14-2 22-8v28H4z" fill="#3c7fb8"/><path d="M4 44c8 0 10-22 26-22 10 0 14 10 8 16" fill="none" stroke="${A}" stroke-width="3"/>`,
  snake: `<path d="M8 40c6-10 14-10 18-2s12 8 16 0 12-8 16 0" fill="none" stroke="${A}" stroke-width="7" stroke-linecap="round"/><circle cx="58" cy="38" r="2" fill="#000"/>`,
  bolt: `<path d="M36 4L12 36h16l-6 24 26-34H32z" fill="${A}"/>`,
  drop: `<path d="M32 6c10 16 18 24 18 34a18 18 0 01-36 0c0-10 8-18 18-34z" fill="${A}"/>`,
  clock: `<circle cx="32" cy="32" r="24" fill="none" stroke="${W}" stroke-width="4"/><path d="M32 16v16l11 7" stroke="${A}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  flame: `<path d="M32 4c4 12 18 18 18 34a18 18 0 01-36 0c0-8 4-12 8-16 0 6 4 10 6 10-2-10 0-20 4-28z" fill="${A}"/>`,
  mountain: `<path d="M4 56l20-34 10 16 8-12 18 30z" fill="#7a8a99"/><path d="M24 22l6 10-6-3-6 3z" fill="#fff"/>`,
  building: `<rect x="14" y="10" width="24" height="48" fill="${W}" opacity=".8"/><rect x="38" y="26" width="14" height="32" fill="${A}"/>${[0, 1, 2, 3, 4].map((r) => `<rect x="19" y="${15 + r * 8}" width="5" height="4" fill="#223"/><rect x="28" y="${15 + r * 8}" width="5" height="4" fill="#223"/>`).join("")}`,
  heart: `<path d="M32 56S6 40 6 22a13 13 0 0126-4 13 13 0 0126 4c0 18-26 34-26 34z" fill="${A}"/>`,
  warning: `<path d="M32 6l28 50H4z" fill="${A}"/><rect x="29" y="22" width="6" height="18" fill="#000"/><rect x="29" y="44" width="6" height="6" fill="#000"/>`,
  star: `<path d="M32 4l8 18 20 2-15 13 5 19-18-10-18 10 5-19L4 24l20-2z" fill="${A}"/>`,
  ice: `<rect x="8" y="20" width="48" height="26" rx="4" fill="#9fd4f0"/><path d="M8 28c8 4 14-4 22 0s16-4 26 0" stroke="#fff" stroke-width="3" fill="none"/><path d="M32 4v12m-5-5l5 5 5-5" stroke="${A}" stroke-width="3" fill="none"/>`,
  rocket: `<path d="M32 4c10 8 12 22 10 34H22C20 26 22 12 32 4z" fill="${W}"/><circle cx="32" cy="22" r="5" fill="${A}"/><path d="M22 38l-8 10 10-2zM42 38l8 10-10-2z" fill="${A}"/><path d="M26 40h12l-6 18z" fill="${A}"/>`,
  horse: `<path d="M14 54l4-22 10-6 4-14 10 2 8 10-6 4-4-3-2 9 4 20h-5l-3-14-12 2-3 12z" fill="${W}"/><circle cx="40" cy="15" r="1.5" fill="#000"/>`,
};

export function icon(name) {
  if (!name || name === "none" || !ICONS[name]) return "";
  return `<svg viewBox="0 0 64 64" width="100%" height="100%">${ICONS[name]}</svg>`;
}
