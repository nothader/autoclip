"""免费素材：Pexels / Pixabay 官方 API 搜索并下载竖屏视频，直接喂给 beatcut。

两家都免费、可商用、无需署名（署名是礼貌，CREDITS.md 里都记下了）。需要各自的免费 API Key：
    Pexels  https://www.pexels.com/api/        → 环境变量 PEXELS_API_KEY
    Pixabay https://pixabay.com/api/docs/      → 环境变量 PIXABAY_API_KEY
不能把素材原样当素材再卖（两家 license 都禁止），剪成自己的作品发布没问题。
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

UA = "AutoClip-beatcut/1.0 (+https://github.com/zhouxiaoka/autoclip)"
LONG_SIDE = 1920
LICENSES = {
    "pexels": "Pexels License — free for commercial use, no attribution required (https://www.pexels.com/license/)",
    "pixabay": "Pixabay Content License — free for commercial use, no attribution required (https://pixabay.com/service/license-summary/)",
}
Progress = Optional[Callable[[str, int, int], None]]


class StockError(RuntimeError):
    pass


@dataclass
class StockClip:
    source: str           # pexels / pixabay
    id: str
    page_url: str
    author: str
    author_url: str
    duration: float
    width: int
    height: int
    fps: float
    download_url: str
    query: str = ""

    @property
    def filename(self) -> str:
        return f"{self.source}-{self.id}.mp4"

    @property
    def portrait(self) -> bool:
        return self.height > self.width


def api_key(source: str, explicit: Optional[str] = None) -> Optional[str]:
    return explicit or os.getenv(f"{source.upper()}_API_KEY") or os.getenv(f"AUTOCLIP_{source.upper()}_API_KEY")


def _get_json(url: str, headers: Optional[Dict[str, str]] = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 — 固定的 https API 地址
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (400, 401, 403):
            raise StockError(f"API 拒绝了请求（HTTP {e.code}）：API Key 不对或没填？") from e
        if e.code == 429:
            raise StockError("请求太频繁（HTTP 429），过几分钟再试") from e
        raise StockError(f"HTTP {e.code}：{url.split('?')[0]}") from e
    except urllib.error.URLError as e:
        raise StockError(f"连不上 {urllib.parse.urlparse(url).netloc}：{e.reason}") from e


def _download(url: str, dest: Path) -> int:
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:  # noqa: S310
            n = 0
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                n += len(chunk)
    except (urllib.error.URLError, OSError) as e:
        tmp.unlink(missing_ok=True)
        raise StockError(f"下载失败：{dest.name}（{e}）") from e
    tmp.replace(dest)
    return n


def _pick_size(files: Sequence[dict]) -> Optional[dict]:
    """最长边 ≤ 1920 里最大的一档（同尺寸取高帧率）；都超了就取最小的。"""
    ok = [f for f in files if f.get("link") or f.get("url")]
    if not ok:
        return None
    fit = [f for f in ok if max(f.get("width") or 0, f.get("height") or 0) <= LONG_SIDE]
    if fit:
        return max(fit, key=lambda f: ((f.get("width") or 0) * (f.get("height") or 0), f.get("fps") or 0))
    return min(ok, key=lambda f: (f.get("width") or 0) * (f.get("height") or 0))


def search_pexels(query: str, n: int, key: str, orientation: str = "portrait") -> List[StockClip]:
    params = {"query": query, "per_page": min(80, max(15, n * 3)), "size": "medium"}
    if orientation in ("portrait", "landscape"):
        params["orientation"] = orientation
    data = _get_json("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(params), {"Authorization": key})
    out = []
    for v in data.get("videos", []):
        files = [f for f in v.get("video_files", []) if (f.get("file_type") or "video/mp4") == "video/mp4"]
        f = _pick_size(files)
        if not f:
            continue
        user = v.get("user") or {}
        out.append(StockClip("pexels", str(v["id"]), v.get("url", ""), user.get("name", ""), user.get("url", ""),
                             float(v.get("duration") or 0), int(f.get("width") or v.get("width") or 0),
                             int(f.get("height") or v.get("height") or 0), float(f.get("fps") or 0), f["link"], query))
    return out


def search_pixabay(query: str, n: int, key: str, orientation: str = "portrait") -> List[StockClip]:
    params = {"key": key, "q": query, "per_page": min(200, max(20, n * 4)), "safesearch": "true", "video_type": "film"}
    data = _get_json("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(params))
    out = []
    for h in data.get("hits", []):
        sizes = [dict(v, link=v.get("url")) for v in (h.get("videos") or {}).values() if isinstance(v, dict)]
        f = _pick_size(sizes)
        if not f:
            continue
        out.append(StockClip("pixabay", str(h["id"]), h.get("pageURL", ""), h.get("user", ""),
                             f"https://pixabay.com/users/{h.get('user', '')}-{h.get('user_id', '')}/",
                             float(h.get("duration") or 0), int(f.get("width") or 0), int(f.get("height") or 0),
                             0.0, f["link"], query))
    if orientation == "portrait":
        out = [c for c in out if c.portrait]
    elif orientation == "landscape":
        out = [c for c in out if not c.portrait]
    return out


def search(queries: Sequence[str], n: int, *, sources: Sequence[str] = ("pexels", "pixabay"),
           orientation: str = "portrait", min_duration: float = 3, max_duration: float = 30,
           keys: Optional[Dict[str, Optional[str]]] = None) -> List[StockClip]:
    """多个关键词 × 多个来源，交替取，去重，按时长过滤，最多 n 条。"""
    keys = keys or {}
    usable = [s for s in sources if api_key(s, keys.get(s))]
    if not usable:
        raise StockError(
            "没有可用的 API Key。两家都免费：\n"
            "  Pexels  https://www.pexels.com/api/     → export PEXELS_API_KEY=...\n"
            "  Pixabay https://pixabay.com/api/docs/   → export PIXABAY_API_KEY=...")
    pools: List[List[StockClip]] = []
    for q in queries:
        for s in usable:
            fn = search_pexels if s == "pexels" else search_pixabay
            found = fn(q, n, api_key(s, keys.get(s)) or "", orientation)
            pools.append([c for c in found if min_duration <= c.duration <= max_duration])
    picked: List[StockClip] = []
    seen = set()
    i = 0
    while len(picked) < n and any(i < len(p) for p in pools):
        for p in pools:
            if i < len(p) and (p[i].source, p[i].id) not in seen and len(picked) < n:
                seen.add((p[i].source, p[i].id))
                picked.append(p[i])
        i += 1
    return picked


def write_credits(outdir: Path, clips: Sequence[StockClip]) -> Path:
    """CREDITS.md（人看）+ credits.json（机器读），追加去重。"""
    js = outdir / "credits.json"
    existing = json.loads(js.read_text(encoding="utf-8")) if js.exists() else []
    have = {(c["source"], c["id"]) for c in existing}
    existing += [dict(asdict(c), file=c.filename, license=LICENSES[c.source]) for c in clips
                 if (c.source, c.id) not in have]
    js.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Credits", "", "Free stock footage. Attribution is not required by either license but is appreciated.", "",
          "| File | Source | Author | Link |", "|---|---|---|---|"]
    md += [f"| {c['file']} | {c['source'].title()} | [{c['author'] or '—'}]({c['author_url']}) | {c['page_url']} |"
           for c in existing]
    md += ["", *sorted({f"- {LICENSES[c['source']]}" for c in existing})]
    (outdir / "CREDITS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return outdir / "CREDITS.md"


def fetch(queries: Sequence[str], outdir: Path, n: int = 12, *, progress: Progress = None, **kw) -> dict:
    outdir = Path(outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    clips = search(queries, n, **kw)
    if not clips:
        raise StockError("没搜到合适的素材：换个关键词，或放宽 --orientation any / --max-duration")
    files, total = [], 0
    for i, c in enumerate(clips):
        dest = outdir / c.filename
        if not dest.exists():
            total += _download(c.download_url, dest)
        files.append(str(dest))
        if progress:
            progress("download", i + 1, len(clips))
    credits = write_credits(outdir, clips)
    by_source: Dict[str, int] = {}
    for c in clips:
        by_source[c.source] = by_source.get(c.source, 0) + 1
    return {"folder": str(outdir), "files": files, "credits": str(credits), "by_source": by_source,
            "downloaded_mb": round(total / 1e6, 1)}


def slug(s: str) -> str:
    return re.sub(r"[^\w\-]+", "-", s, flags=re.UNICODE).strip("-").lower()[:40] or "stock"
