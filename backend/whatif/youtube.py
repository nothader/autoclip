"""
上传到 YouTube（YouTube Data API v3，可续传上传 + 自定义封面）。

凭据从环境变量读（不落盘、不进仓库）：
  YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN
refresh token 用 scripts/youtube_auth.py 在自己电脑上授权一次拿到（scope 只有 youtube.upload）。

注意：2020-07-28 之后创建、还没通过 YouTube API 审核的项目，上传的视频会被锁成 private。
默认就是 private：上传后人工在 YouTube Studio 里看一遍再公开。
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
THUMB_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
ENV_KEYS = ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
CATEGORY_EDUCATION = "27"
CHUNK = 8 * 1024 * 1024
MAX_TITLE, MAX_DESC, MAX_TAG_CHARS = 100, 5000, 480


class YouTubeError(RuntimeError):
    pass


@dataclass
class VideoMeta:
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    pinned_comment: str = ""


def parse_meta(text: str) -> VideoMeta:
    """读 publish 生成的 *_youtube.txt：TITLE / DESCRIPTION / CHAPTERS / TAGS / PINNED COMMENT 等大写标题分段。"""
    sections: Dict[str, List[str]] = {}
    cur = None
    for line in text.splitlines():
        if re.fullmatch(r"[A-Z][A-Z ()/&-]{2,}", line.strip()):
            cur = line.strip()
            sections[cur] = []
        elif cur:
            sections[cur].append(line)
    get = lambda k: "\n".join(sections.get(k, [])).strip()
    title = get("TITLE").splitlines()[0].strip() if get("TITLE") else ""
    if not title:
        raise YouTubeError("metadata has no TITLE section")
    desc_parts = [get("DESCRIPTION")]
    for extra in ("CHAPTERS", "SOURCES (ROUNDED, WIDELY CITED)", "SOURCES"):
        if get(extra):
            desc_parts.append(get(extra) if extra == "CHAPTERS" else "Sources: " + get(extra))
    tags = [t.strip() for t in get("TAGS").replace("\n", ",").split(",") if t.strip()]
    return VideoMeta(title=title, description="\n\n".join(p for p in desc_parts if p), tags=tags,
                     pinned_comment=get("PINNED COMMENT"))


def body_for(meta: VideoMeta, *, privacy: str = "private", publish_at: Optional[str] = None,
             category: str = CATEGORY_EDUCATION) -> Dict:
    """videos.insert 的请求体。publish_at（RFC3339）只在 private 时有效：到点自动公开（需项目已通过审核）。"""
    tags, n = [], 0
    for t in meta.tags:                                  # YouTube 限制所有标签合计约 500 字符
        if n + len(t) + 1 > MAX_TAG_CHARS:
            break
        tags.append(t)
        n += len(t) + 1
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "embeddable": True}
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at
    desc = meta.description.replace("<", "‹").replace(">", "›")   # 尖括号会被 API 拒收
    return {"snippet": {"title": meta.title[:MAX_TITLE], "description": desc[:MAX_DESC], "tags": tags,
                        "categoryId": category, "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": status}


def credentials_from_env(env=os.environ) -> Dict[str, str]:
    missing = [k for k in ENV_KEYS if not env.get(k)]
    if missing:
        raise YouTubeError("missing environment variables: " + ", ".join(missing)
                           + " (run scripts/youtube_auth.py once on your own computer to get them)")
    return {k: env[k] for k in ENV_KEYS}


def access_token(creds: Dict[str, str], session=None) -> str:
    import requests
    s = session or requests
    r = s.post(TOKEN_URL, data={"client_id": creds["YOUTUBE_CLIENT_ID"], "client_secret": creds["YOUTUBE_CLIENT_SECRET"],
                                "refresh_token": creds["YOUTUBE_REFRESH_TOKEN"], "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200:
        raise YouTubeError(f"token refresh failed ({r.status_code}): {r.text[:300]}")
    return r.json()["access_token"]


def upload(video: Path, body: Dict, token: str, session=None, log=print) -> str:
    """可续传上传，返回 videoId。网络抖动时按 Range 续传。"""
    import requests
    s = session or requests
    size = video.stat().st_size
    init = s.post(UPLOAD_URL, params={"uploadType": "resumable", "part": "snippet,status"},
                  headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8",
                           "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
                  data=json.dumps(body), timeout=60)
    if init.status_code != 200 or "Location" not in init.headers:
        raise YouTubeError(f"upload init failed ({init.status_code}): {init.text[:500]}")
    url = init.headers["Location"]
    pos, tries = 0, 0
    with open(video, "rb") as f:
        while pos < size:
            f.seek(pos)
            chunk = f.read(CHUNK)
            end = pos + len(chunk) - 1
            try:
                r = s.put(url, data=chunk, timeout=300, headers={"Authorization": f"Bearer {token}",
                                                                 "Content-Range": f"bytes {pos}-{end}/{size}"})
            except Exception as e:                                       # 断线：查询服务器收到多少再续
                tries += 1
                if tries > 5:
                    raise YouTubeError(f"upload failed after retries: {e}")
                time.sleep(2 ** tries)
                pos = _uploaded_bytes(s, url, token, size)
                continue
            if r.status_code in (200, 201):
                return r.json()["id"]
            if r.status_code == 308:
                rng = r.headers.get("Range")
                pos = int(rng.split("-")[1]) + 1 if rng else 0
                log(f"  uploaded {pos * 100 // size}%")
                tries = 0
                continue
            if r.status_code >= 500 and tries < 5:
                tries += 1
                time.sleep(2 ** tries)
                pos = _uploaded_bytes(s, url, token, size)
                continue
            raise YouTubeError(f"upload failed ({r.status_code}): {r.text[:500]}")
    raise YouTubeError("upload ended without a video id")


def _uploaded_bytes(s, url: str, token: str, size: int) -> int:
    r = s.put(url, headers={"Authorization": f"Bearer {token}", "Content-Range": f"bytes */{size}"}, timeout=60)
    if r.status_code == 308:
        rng = r.headers.get("Range")
        return int(rng.split("-")[1]) + 1 if rng else 0
    return 0


def set_thumbnail(video_id: str, thumb: Path, token: str, session=None) -> bool:
    """自定义封面需要频道已做手机验证；失败不影响视频本身。"""
    import requests
    s = session or requests
    ctype = "image/png" if thumb.suffix.lower() == ".png" else "image/jpeg"
    r = s.post(THUMB_URL, params={"videoId": video_id}, headers={"Authorization": f"Bearer {token}", "Content-Type": ctype},
               data=thumb.read_bytes(), timeout=120)
    return r.status_code == 200


def publish(video: Path, meta_txt: Path, *, thumb: Optional[Path] = None, privacy: str = "private",
            publish_at: Optional[str] = None, short: Optional[bool] = None, env=os.environ, session=None, log=print) -> Dict:
    meta = parse_meta(meta_txt.read_text(encoding="utf-8"))
    if short and "#shorts" not in meta.description.lower():
        meta.description += "\n\n#shorts"
    creds = credentials_from_env(env)
    token = access_token(creds, session)
    vid = upload(video, body_for(meta, privacy=privacy, publish_at=publish_at), token, session, log)
    thumb_ok = set_thumbnail(vid, thumb, token, session) if thumb and thumb.exists() else False
    url = f"https://youtu.be/{vid}"
    return {"id": vid, "url": url, "studio": f"https://studio.youtube.com/video/{vid}/edit", "title": meta.title,
            "privacy": "private" if publish_at else privacy, "publish_at": publish_at, "thumbnail_set": thumb_ok,
            "pinned_comment": meta.pinned_comment}
