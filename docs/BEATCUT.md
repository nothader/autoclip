# Beatcut — product UGC beat-sync editor (`autoclip beatcut`)

Faceless product content lives or dies on the edit: macro angles, hands, fast cuts that hit the beat,
speed ramps, a flash on the drop, the *click* of the product under the music, and an ending that loops
back into the start. Beatcut does that edit for you.

**Input:** a folder of footage (or one long raw take) + a song.
**Output:** a 9:16 MP4 where every cut lands on a beat, plus an editable edit-decision list (JSON).

No LLM, no API key, no GPU — just `ffmpeg` + `numpy`.

```bash
pip install numpy            # or: pip install -e ".[beatcut]"

autoclip beatcut make ./shoot-0412 -m song.mp3                       # 15 s, 9:16, one cut per beat
autoclip beatcut make ./shoot-0412 -m song.mp3 -d 12 --pace hype --grade moody
autoclip beatcut make ./shoot-0412 -m song.mp3 --variants 3          # 3 versions, different hooks → A/B test
autoclip beatcut make raw_take.mov -m song.mp3 --preview             # half-res, fast — check the rhythm first
autoclip beatcut make ./shoot -d 10 --bpm 110 --foley 1.0            # no music: ASMR, product sounds only

autoclip beatcut plan ./shoot -m song.mp3 -o edit.json               # edit list only
autoclip beatcut render edit.json                                    # … tweak it, then render
autoclip beatcut beats song.mp3                                      # BPM, beats, best section to use
```

Output goes to `<data dir>/beatcut/` (same data dir as the desktop app) unless you pass `-o`.

## What the edit does

| Moment | Rule |
|---|---|
| **Hook** (first shot) | The best-scoring window in all your footage — sharp, well exposed, some motion. No flash, no ramp: it starts on the money shot. Each `--variants` version opens on a different hook. |
| **Cuts** | Always on a beat, frame-exact (cut points are computed once in frames, no drift). `normal` = every beat (every 2 if the song is fast), `calm` = 2–4 beats, `hype` = half-beats in high-energy parts. Quiet passages cut half as often. |
| **Flash** | White flash + a low "impact" on the strongest hits (the drop, big snares). |
| **Punch-in** | 12 % zoom that settles in 0.25 s, on bar downbeats. |
| **Speed ramp** | On moving shots: 2.6× then 0.65× so it *slows into* the next beat, with a synthesized whoosh peaking on the cut. Off in `calm`. |
| **Slow-mo** | 60 fps+ footage in quiet passages plays at 0.5× (shoot 60 fps!). |
| **Loop** | The last shot is the half-second *right before* the hook in the same clip, so the end flows straight into the start. |
| **Music** | Picks the section of the song with the highest energy that starts on a bar downbeat (override with `--music-start`). The ending snaps to a beat. |
| **Foley** | The clip's own sound (taps, clicks, pours, zips) is kept under the music for normal-speed shots and normalized across clips (`--foley 0`–`1.5`). |
| **Grade** | `clean` (default), `warm`, `moody`, `mono`, `punchy`, `none`, plus your own `.cube` LUT via `--lut`. iPhone HDR (HLG) clips are tone-mapped to SDR automatically. |

## Footage

- **Folder of clips** or **one long take**: a raw take is split wherever the picture changes hard (both a histogram jump and a pixel jump, so a light flicker doesn't count).
- Each 0.1 s of footage is scored: sharpness (main factor), moderate motion (hands, turntable), exposure; shaky whip-pans and dark/blown frames score low. The editor uses the best windows, never reuses the same moment twice while there's fresh footage, and never puts the same shot back to back.
- Shoot **more angles than you think**: ~25 clips of 2–5 s each (macro texture, top-down, hand-in/hand-out, turntable spin with a light sweep, rack focus) for a 15 s video. If the footage is shorter than the video, the editor warns and reuses moments.

## Editing the plan

`plan` / `make` write a JSON next to the video. Every shot is:

```json
{ "source": "/shoot/macro_03.mov", "src_start": 2.4, "frames": 15,
  "speed": [[0.4, 2.6], [0.6, 0.65]], "punch": 0.12, "flash": false, "foley": true, "note": "ramp punch" }
```

Swap `source` / `src_start` to change what's on screen, change `speed` (`[[fraction of the shot, speed], …]`),
toggle `flash` / `punch`, change `grade` / `lut` / `foley` at the top. **Keep `frames` as is** so cuts stay on the beat;
if you change one shot's `frames`, change a neighbour's by the opposite amount. Then `autoclip beatcut render edit.json`.

## MCP

`autoclip mcp` exposes `beatcut_video(footage[], music_path?, output_path?, duration, pace, aspect, grade, variants, foley, loop, preview, bpm?, music_start?)`,
which returns the video paths, plan paths and a shot-by-shot description.

## Code

| File | Role |
|---|---|
| `backend/beatcut/audio.py` | Decoding, spectral-flux onsets, tempo (autocorrelation + prior), Ellis DP beat tracking, downbeats from kick-band onsets, per-beat energy, picking the section to use |
| `backend/beatcut/footage.py` | Probing (fps, rotation, HDR, audio), 10 fps grayscale sampling, sharpness / motion / exposure, shot splitting, window search |
| `backend/beatcut/plan.py` | Beat grid → slots → effects → shot assignment (hook, variety, loop tail) → `EditPlan` (pydantic, `extra=forbid`) |
| `backend/beatcut/render.py` | Per-shot ffmpeg (piecewise `setpts` speed curve → `fps` → cover crop → punch → grade/LUT → flash), concat, numpy mix (music + foley + whoosh/impact), mux |
| `backend/beatcut/pipeline.py` | Shared by the CLI and MCP |
| `backend/tests/test_beatcut.py` | Beat accuracy at 85–174 BPM (< 1 frame), plan invariants, and an end-to-end render that re-detects beats in the output's own audio and checks every cut is within 1 frame |

Limits / next: no on-screen text or captions yet (use `autoclip export`-style overlays or your editor), no
masking/match-cut transitions (those need object tracking), and there's no desktop UI for it yet — CLI and MCP only.
