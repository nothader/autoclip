# Dink Dunk automation runbook

Scheduled sessions follow this file. **Daily** (Short) and **weekly** (long-form) runs make one video each, upload it to YouTube as **PRIVATE**, and report the link. The owner reviews it and makes it public in YouTube Studio. Never upload as public or unlisted.

**There is one look: Block POV** (studied frame by frame from @weirdsecret_; the full breakdown is in `automation/STYLE_BLOCK_POV.md`). Every other style (film, voxel, bodycam, toon, cinematic, witness, retro, split screen, narrated explainers) has been deleted from the generator, and the schema rejects it.

Repo: `nothader/autoclip`, branch `feat/whatif-video-generator`. Commit with the session's attribution trailer. Never commit videos (`work/` is excluded).

## 0. Setup (fresh container)
```bash
cd <repo> && git checkout feat/whatif-video-generator && git pull
[ -x venv/bin/python ] || { python3 -m venv venv && ./venv/bin/pip install -q -r requirements.txt -r requirements-whatif.txt; }
./venv/bin/python -c "import playwright, kokoro_onnx" && ffmpeg -version | head -1
```
Chromium is preinstalled (do not run `playwright install`). Character voices download the Kokoro TTS model on first use (~120 MB).
If `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` or `YOUTUBE_REFRESH_TOKEN` is missing, still make the video. Skip the upload, and in the final message say which variable is missing.

## 1. Pick the topic
Use the first `- [ ]` line in the right section of `automation/topics.md` (Shorts for daily, Long-form for weekly). Skip a topic that breaks the topic rules below or is already made (see Done).

**Topic rules (owner, Nov 2026):** religious what-ifs are allowed and are told from a believer's point of view. Never set a story inside a real attack with real victims (use a fictional building and place). Immigration or other political group topics only as neutral reworks (e.g. "what if every nurse walked out"). No gore.

## 2. Write the script
Copy the closest example in `automation/scripts/` (`elevator.py`, `bp_*.py`) and adapt it. Never reuse a set or shot list as-is.
- **Library:** `automation/lib/block.py` gives `Story`, `T` (tracker), `guy`, `crowd`, `env`, `O`. `automation/lib/places.py` gives `street`, `terrace`, `hospital_room`, `bedroom`, `church`, `mosque`, `office_floor`, `stairwell`, `plain`, `living_room`, `park` (all take a seed and colours; build new places for every topic too).
- **Structure (Shorts 60–100 s, 16–26 beats of 2.8–4 s):**
  1. Beat 0: caption `""`; the serif title (one `*key word*` in the accent colour) shows over it for 3.5 s. A normal, specific moment.
  2. The event lands in 2–3 short beats. Then time jumps; each jump is a new place or angle.
  3. One real-world anchor (a real number, case or source line in `by=`).
  4. People around you get it wrong; you choose differently. Climax: tracker `alert` (red) or `big` (centre), `shake`.
  5. A quiet emotional resolution. End card: one gold question to YOU.
- **Text:** italic second-person captions, 3–9 words, grade-3 words, at least 40% say "you"/"your". Dialogue in quotes with `by=`. A tracker on most beats: `clock` (ticks), `count` (+ `unit`, `prefix="$"`), `value`, or `scramble`.
- **Sound:** no narrator. People in the scene talk (`voices=[("text", "af_heart", at)]`). Music is the tender piano bed.
- **Camera:** mostly `eyes` (first person, block hands: `idle`, `phone`, `hold`+`cup`, `reach`, `shield`, `grab`, `point`, `float`), 1–3 cutaways to `front` / `far`.
- **Long-form (weekly):** same look at 1920×1080 (`Story.save(..., )` then set `"width": 1920, "height": 1080` in the JSON), 3–4 minutes, 45–60 beats, chapters as time jumps on the tracker. Check a landscape contact sheet before rendering.
- **Framing pitfalls:**
  - The `eyes` camera looks toward −z from `eye=(x, y, z)`; people facing you need `ry=180` (or 150–210).
  - Keep faces above the caption line (about 58% down the frame).
  - Near flames and glows burn out the captions; keep them back.
  - `look="elder"` for grandparents.
  - A cramped room puts the camera inside people: move the eye back or the people away.

## 3. Check, then LOOK
```bash
./venv/bin/python automation/scripts/<topic>.py           # writes <topic>.json next to it
./venv/bin/python -m backend.cli whatif check automation/scripts/<topic>.json   # must be 100/100 or tips only
./venv/bin/python automation/novelty.py automation/scripts/<topic>.json          # must pass: different from recent videos
./venv/bin/python automation/sheet.py automation/scripts/<topic>.json   # then Read the PNG
```
Read the contact sheet and fix every shot where the subject isn't clearly visible or a face is cut off, turned away or hidden under the caption. Re-run the sheet until every frame reads.

## 4. Render (detached, resumable)
```bash
mkdir -p /tmp/frames-<topic>
setsid nohup ./venv/bin/python -m backend.cli whatif render automation/scripts/<topic>.json \
  -o work/whatif/<slug>.mp4 --pack --frames-dir /tmp/frames-<topic> > /tmp/render-<topic>.log 2>&1 < /dev/null & disown
```
A Short takes about an hour on 4 cores. Keep a background until-loop waiting on the log the whole time: the container is reclaimed when the session goes idle, which kills the render. If the container restarts, re-run the same command; existing frames are skipped. Delete `/tmp/frames-<topic>` after the video is done (the disk fills up otherwise).
Then compress: `ffmpeg -i X.mp4 -c:v libx264 -preset slow -b:v 6M -maxrate 9M -bufsize 12M -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart X_c.mp4 && mv X_c.mp4 X.mp4`.
Pull 4–5 frames from the final MP4 and look at them (check colour, faces, text). If the thumbnail beat is weak: `whatif thumb <json> --beat N --text "..."`.

## 5. Metadata
`work/whatif/<slug>_youtube.txt` is generated by `--pack`. Replace its TAGS with about 10 specific search phrases (topic phrase first, then "what if", "pov", "fyp", "dink dunk").

## 6. Upload (PRIVATE)
```bash
./venv/bin/python -m backend.cli whatif upload work/whatif/<slug>.mp4 --short     # Shorts
./venv/bin/python -m backend.cli whatif upload work/whatif/<slug>.mp4             # long-form
```
It prints the video URL and the Studio link. Never pass `--privacy public`.

## 7. Record and report
- In `automation/topics.md`, change the line to `- [x] ... (made YYYY-MM-DD, <url>)` and move it to Done. Commit the script and topics.md, then push.
- Final message to the owner, short:
  - title and length;
  - the Studio link to review;
  - suggested posting time: Shorts 4 PM ET, long-form Sunday 12 PM ET;
  - the pinned comment to post (the end-card question);
  - anything you could not do and why.
