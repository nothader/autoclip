"""what-if 视频生成（只剩 Block POV 格式）：分镜结构、进度块、帧数据、LLM 分镜修正循环、声音、渲染、YouTube 上传。

渲染（Chromium/WebGL）测试需要 playwright + 浏览器，缺依赖时跳过。
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.whatif.model import compile_plan, validate  # noqa: E402
from backend.whatif.planner import EXAMPLE_PATH, EXAMPLES_DIR, build_prompt, extract_json, plan_storyboard  # noqa: E402
from backend.whatif.schema import Storyboard  # noqa: E402

SCRIPTS = Path(__file__).resolve().parents[2] / "automation" / "scripts"


def _beat(cap="", **k):
    b = {"duration": 3, "camera": "eyes", "caption": cap, "hands": {"pose": "idle"},
         "env": {"set": {"background": ["#5d86ad", "#d7e3ea"], "focus": [0, 1.62, 1], "objects": [
             {"kind": "box", "at": [0, -0.02, -2], "scale": [8, 0.04, 8], "color": "#8a6a4f"},
             {"kind": "block_person", "at": [0, 0, -2], "seed": 3, "action": "wave", "rotate": [0, 180, 0]}]}}}
    b.update(k)
    return b


def _mini(**over) -> dict:
    d = {"title": "What if you got stuck in an elevator?", "premise": "p",
         "intro": {"title": "What if you got stuck in an *elevator*?"},
         "outro": {"end": {"lines": ["Would you wait?"]}},
         "beats": [_beat("", tracker={"label": "FRIDAY", "clock": "11:02:14 PM"}),
                   _beat("You press the alarm. Nothing.", tracker={"label": "STUCK FOR", "count_from": 0, "count_to": 41, "unit": " HOURS"}),
                   _beat("\"Hello? Anyone?\"", caption_by="You", voices=[{"text": "Hello?", "voice": "am_adam"}])]}
    d.update(over)
    return d


# ------------------------------------------------------------- 结构 ---
def test_defaults_are_block_pov():
    sb = Storyboard.model_validate(_mini())
    assert sb.format == "pov" and sb.theme.style == "block" and sb.theme.music == "tender"
    assert sb.beats[0].scene == "custom" and sb.pov is not None and sb.pov.hand_style == "block"
    assert sb.intro.style == "none" and sb.outro.chart is False


@pytest.mark.parametrize("bad", [
    {"theme": {"style": "film"}}, {"theme": {"style": "voxel"}}, {"theme": {"style": "bodycam"}},
    {"format": "timeline"}, {"format": "escalation"}, {"theme": {"music": "dark"}}, {"theme": {"layout": "split"}},
    {"intro": {"style": "stack"}}, {"narration": {"enabled": True}},
])
def test_old_looks_are_rejected(bad):
    with pytest.raises(Exception):
        Storyboard.model_validate(_mini(**bad))


@pytest.mark.parametrize("field,val", [("stat", {"value": "90%"}), ("chip", "5 DAYS LATER"), ("callout", {"title": "X"}),
                                       ("time", "+1 HOUR"), ("chapter", "After"), ("counter", {"to": 5})])
def test_old_overlay_fields_are_rejected(field, val):
    d = _mini()
    d["beats"][1][field] = val
    with pytest.raises(Exception):
        Storyboard.model_validate(d)


@pytest.mark.parametrize("kind", ["person", "voxel", "voxel_person", "carpet", "earth"])
def test_old_set_kinds_are_gone(kind):
    d = _mini()
    d["beats"][0]["env"]["set"]["objects"].append({"kind": kind})
    with pytest.raises(Exception):
        Storyboard.model_validate(d)


@pytest.mark.parametrize("path", sorted(str(p) for p in list(EXAMPLES_DIR.glob("*.json")) + list(SCRIPTS.glob("*.json"))
                                        if not p.name.endswith(".sheet.json")))
def test_every_block_storyboard_validates_and_compiles(path):
    sb = Storyboard.model_validate_json(Path(path).read_text(encoding="utf-8"))
    assert validate(sb) == []
    plan = compile_plan(sb)
    assert plan["theme"]["style"] == "block" and plan["theme"]["captions"] == "story"
    assert plan["theme"]["palette"] in ("natural", "warm", "cool")
    assert any("tracker" in f for f in plan["frames"]) and plan["frames"][-1].get("end")


# ------------------------------------------------------------ 规划器 ---
def test_prompt_is_block_only():
    rules = build_prompt("What if you got lost at sea?").split("EXAMPLE:")[0]
    assert "Block POV" in rules and "block_person" in rules and "tracker" in rules
    for old in ("bodycam", "voxel", "escalation", "witness", "split"):
        assert old not in rules


def test_planner_repairs_invalid_storyboard():
    good = _mini()
    bad = json.loads(json.dumps(good))
    bad["theme"] = {"style": "toon"}
    calls = []

    def fake_llm(prompt: str) -> str:
        calls.append(prompt)
        return json.dumps(bad if len(calls) == 1 else good)

    sb = plan_storyboard("What if?", call=fake_llm, hooks=False)
    assert sb.theme.style == "block"
    assert len(calls) == 2 and "theme.style" in calls[1]


def test_extract_json_handles_fences():
    assert extract_json('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}


def test_planner_gives_up_after_max_repairs():
    with pytest.raises(ValueError):
        plan_storyboard("x", call=lambda p: "not json", max_repairs=1)


# ------------------------------------------------------------- 进度块 / 帧 ---
def test_block_tracker_clock_count_and_scramble():
    from backend.whatif.model import tracker_frame, _parse_clock, _fmt_clock
    assert _parse_clock("12:05:00 AM") == 300 and _parse_clock("1:00 PM") == 13 * 3600
    assert _fmt_clock(_parse_clock("11:59:58 PM") + 3, "11:59:58 PM") == "12:00:01 AM"
    f = tracker_frame({"label": "FRIDAY", "clock": "8:46:27 AM"}, 2.0, True, 3.0)
    assert f["value"] == "8:46:29 AM" and f["label"] == "FRIDAY"
    c = tracker_frame({"count_from": 0, "count_to": 41, "unit": " HOURS", "alert": True}, 3.0, True, 3.0)
    assert c["value"] == "41 HOURS" and c["alert"]
    d = tracker_frame({"count_from": 0, "count_to": 160e9, "prefix": "$"}, 3.0, True, 3.0)
    assert d["value"] == "$160,000,000,000"
    assert ":" in tracker_frame({"scramble": True}, 0.5, True, 3.0)["value"]


def test_block_frames_title_tracker_and_story_captions():
    plan = compile_plan(Storyboard.model_validate(_mini()))
    assert plan["theme"]["captions"] == "story" and plan["pov"]["hand_style"] == "block"
    f0 = plan["frames"][int(0.5 * plan["fps"])]
    assert f0["btitle"]["text"].startswith("What if") and f0["tracker"]["value"].endswith("PM")
    f1 = plan["frames"][int((plan["beats"][1]["start"] + 2) * plan["fps"])]
    assert "btitle" not in f1 and f1["tracker"]["label"] == "STUCK FOR" and f1["cap"]["text"].startswith("You press")
    f2 = plan["frames"][int((plan["beats"][2]["start"] + 1) * plan["fps"])]
    assert f2["tracker"]["label"] == "STUCK FOR" and f2["cap"]["ref"] == "You"   # 进度块沿用；引语带出处
    assert plan["frames"][-1]["end"]["lines"] == ["Would you wait?"]


# ------------------------------------------------------------- 声音 ---
def test_audio_has_tender_music():
    np = pytest.importorskip("numpy")
    from backend.whatif.audio import SR, synthesize, _music_tender
    plan = compile_plan(Storyboard.model_validate(_mini()))
    x = synthesize(plan)
    assert x.shape == (int(round(plan["duration"] * SR)), 2) and np.isfinite(x).all()
    assert np.max(np.abs(x)) <= 0.8 and np.sqrt(np.mean(x ** 2)) > 0.003
    assert np.abs(_music_tender(SR * 4, 3)).max() > 0


# ------------------------------------------------------------- 渲染 ---
def test_render_frames_resumes_and_skips_existing(tmp_path, monkeypatch):
    from backend.whatif import render
    calls = []

    class FakeProc:
        def __init__(self, cmd, **kw):
            job = json.loads(Path(cmd[-2]).read_text())
            calls.append(job["frames"])
            for i in job["frames"]:
                (Path(job["out"]) / f"{i:06d}.jpg").write_bytes(b"x")
            Path(cmd[-1]).write_text(json.dumps({"errors": []}))
            self.stderr = None
            self.returncode = 0

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(render.subprocess, "Popen", FakeProc)
    plan = {"n_frames": 10, "fps": 30}
    out = tmp_path / "frames"
    out.mkdir()
    for i in range(6):                                   # 前 6 帧上次已经渲好了
        (out / f"{i:06d}.jpg").write_bytes(b"x")
    render.render_frames(plan, out, width=10, height=10, workers=2)
    assert sorted(i for part in calls for i in part) == [6, 7, 8, 9]
    calls.clear()
    assert render.render_frames(plan, out, width=10, height=10) == [] and not calls


def test_block_beats_render_without_page_errors(tmp_path):
    pytest.importorskip("playwright")
    from backend.whatif.render import render_frames
    plan = compile_plan(Storyboard.model_validate_json(EXAMPLE_PATH.read_text(encoding="utf-8")))
    frames = [int((b["start"] + b["duration"] * 0.5) * plan["fps"]) for b in plan["beats"][:6]] + [plan["n_frames"] - 1]
    try:
        errs = render_frames(plan, tmp_path, width=270, height=480, frames=frames, workers=2, fmt="jpg")
    except RuntimeError as e:
        if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs


# ------------------------------------------------------------- YouTube ---
def test_youtube_meta_parse_and_resumable_upload(tmp_path):
    from backend.whatif import youtube
    txt = ("TITLE\nWhat if X?\n\nDESCRIPTION\nLine one <b>.\n\nCHAPTERS\n0:00 Start\n\nTAGS\na, b, c\n\nPINNED COMMENT\nWho wins?\n")
    m = youtube.parse_meta(txt)
    assert m.title == "What if X?" and m.tags == ["a", "b", "c"] and "0:00 Start" in m.description and m.pinned_comment == "Who wins?"
    body = youtube.body_for(m, publish_at="2026-11-10T21:00:00Z")
    assert body["status"]["privacyStatus"] == "private" and body["status"]["publishAt"] and "<" not in body["snippet"]["description"]
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x" * 1000)
    thumb = tmp_path / "t.jpg"
    thumb.write_bytes(b"jpg")
    calls = []

    class R:
        def __init__(self, code, js=None, headers=None):
            self.status_code, self._js, self.headers, self.text = code, js or {}, headers or {}, ""

        def json(self):
            return self._js

    class Sess:
        def post(self, url, **kw):
            calls.append(("post", url))
            if url == youtube.TOKEN_URL:
                return R(200, {"access_token": "tok"})
            if url == youtube.UPLOAD_URL:
                assert json.loads(kw["data"])["snippet"]["title"] == "What if X?"
                return R(200, headers={"Location": "https://up/1"})
            return R(200)

        def put(self, url, **kw):
            calls.append(("put", kw["headers"]["Content-Range"]))
            return R(200, {"id": "abc123"})

    meta = tmp_path / "v_youtube.txt"
    meta.write_text(txt)
    env = {k: "x" for k in youtube.ENV_KEYS}
    res = youtube.publish(video, meta, thumb=thumb, short=True, env=env, session=Sess(), log=lambda *a: None)
    assert res["id"] == "abc123" and res["privacy"] == "private" and res["thumbnail_set"]
    assert ("put", "bytes 0-999/1000") in calls
    with pytest.raises(youtube.YouTubeError):
        youtube.credentials_from_env({})
