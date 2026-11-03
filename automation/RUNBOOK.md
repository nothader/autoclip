# Dink Dunk automation runbook

Scheduled sessions follow this file. **Daily** (Short) and **weekly** (long-form) runs make one video each, upload it to YouTube as **PRIVATE**, and report the link. The owner reviews it and makes it public in YouTube Studio. Never upload as public or unlisted.

Repo: `nothader/autoclip`, branch `feat/whatif-video-generator`. Commit with the session's attribution trailer. Never commit videos (`work/` is excluded).

## 0. Setup (fresh container)
```bash
cd <repo> && git checkout feat/whatif-video-generator && git pull
[ -x venv/bin/python ] || { python3 -m venv venv && ./venv/bin/pip install -q -r requirements.txt -r requirements-whatif.txt; }
./venv/bin/python -c "import playwright, kokoro_onnx" && ffmpeg -version | head -1
```
Chromium is preinstalled (do not run `playwright install`). Narration downloads its TTS model on first use (~120 MB).
If `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` or `YOUTUBE_REFRESH_TOKEN` is missing, still make the video. Skip the upload, and in the final message say which variable is missing.

## 1. Pick the topic
Use the first `- [ ]` line in the right section of `automation/topics.md` (Shorts for daily, Long-form for weekly). Skip a topic that is unsafe or already made (see Done).

## 2. Write the script
Copy the closest example and adapt it. Never reuse a set or shot list as-is.
- Shorts: `automation/scripts/*.py`, using the `automation/lib/hit.py` helpers (`Video`, `V`, `P`, `crowd`, `room`, `city`, `park`, `school`, `BOY`/`GIRL`, palettes). Best examples: `partner.py`, `onegender.py`, `planes.py`, `mars.py`.
- Long-form: `automation/longform/swap24.py` (16:9, narrated, chapters, comment prompts) plus `hook.py` (danger-hook cold open).
  **Lessons from the first long-form** (swap, Nov 2026: 9% average viewed, 31% left at 0:32, nearly 0% by 2:15):
  - **Deliver the thumbnail promise in the first 10 seconds.** If the thumbnail says "HE GOT HER PERIOD", open on that moment, then rewind. Don't spend the first 48 s on countdown, teasers and "meet the characters". Story action must start by 0:10.
  - **No "coming up" teaser beats.** Show them, don't announce them. Introduce characters inside the action.
  - **3–4 minutes, not 6–7:** 6–8 chapters with the strongest moments only (cut filler chapters), and a faster pace (`pace` 1.35+).
  - **Big captions:** `theme.captions: "words"` and a bold or toon style. Thin serif subtitles are unreadable on phones.
  - **No dip-to-black between chapters.** It is an exit point; use whip or zoom transitions.

### The outlier formula (researched Nov 2026; supersedes the old "sound effects only" rule)
From the biggest "what if" / 3D-explainer Shorts (Zack D. Films: about 29M subscribers, about 81B views; one viral "what if" body channel: 3.9M average views over 59 videos):
- **Deep, serious narrator talking to "you"** ("documentary meets horror trailer"). `hit.save` turns this on by default: Kokoro `am_onyx`. Captions are what the narrator says.
- **Quiet dark cinematic music bed** at about 10–15% volume (`theme.music: "dark"`, on by default in `hit.save`), plus sound effects on every impact moment.
- **50–65 s is the sweet spot**; under 30 s or over 65 s underperforms. About 12–14 beats at the 0.9 pace with narration.
- **Escalation arc:** a curiosity-gap question → a mild, relatable start → it escalates every beat (never plateaus) → the peak drama → a finale of total failure, transformation or twist. Then the pick-a-side question.
- **Something always moves:** the camera is never still for long, with a scene change or new detail every 3–5 s.
- **Bold, centered captions.**
- **Top topic patterns:** "What if you were raised by ___?" (strongest category in that data), survival and body ("What happens to your body if…"), "How long could you…?" Titles with a specific number, a known brand or event, and a hidden consequence.
- An owner can still ask for sound effects only on a specific video: `v.save(..., narrate=False, music="none")`.

### The recipe (what made the 41K-view swap video work)
- **About YOU:** the viewer, their partner, family, body, money, school or job. Everyone watching is in the story.
- **3-2-1 countdown cold open** (`v.save(...)` sets it up): beat 0 caption = "In 3 seconds, ..." Never start on a `flash`.
- **Open loop in the first 3 captions** ("But wait until...", "Here's the scary part...") with a payoff later.
- **Everyday funny details** over abstract facts. One real number per 2–3 beats (`stat` or `tooltip`), rounded and widely cited. Say "about".
- **Shorts:** 10–13 beats, about 40–60 s at the default 0.9 pace (`length: quick`). The owner asked for a 25% slower pace so captions can be read; never speed it back up. Captions at grade-3 reading level, under about 14 words.
- **End on a pick-a-side question** (end card lines + last caption). Examples: "WHO HAD IT HARDER?", "WOULD YOU GO?", "WHICH WORLD WINS?"
- **House look = `style: "film"`** (Nov 2026, matches the top 3D channels): bright warm grade, background blurred by depth, expressive faces. Use it for every Short so the channel has one recognizable look. Use `witness` or `bodycam` only when the format needs it (one fixed eyewitness view or found footage).
- **Faces sell it:** frame people waist-up or closer (`front`/`closeup`/`side`, zoom about 0.5–0.8, `focus` at head height) on most beats. Expressions follow the action: `kneel`/`run`/`sprint`/`fall` = scared, `point`/`phone` = smiling, everything else neutral.
- **Stay neutral** on politics, gender and religion. Present both sides and let the comments argue. No gore, nothing sexual, no real people mocked.
- **Lively backgrounds:** sky colours, places and people. No black voids. No globes or Earth-from-space shots (a small star in the sky is fine). Sound effects only for Shorts; narration for long-form.

## 3. Check, then LOOK
```bash
./venv/bin/python automation/scripts/<topic>.py           # writes <topic>.json next to it
./venv/bin/python -m backend.cli whatif check automation/scripts/<topic>.json   # must be 100/100 or tips only
./venv/bin/python automation/sheet.py automation/scripts/<topic>.json   # then Read the PNG
```
Read the contact sheet and fix every shot where the subject isn't clearly visible above the captions (bottom ~45% of a vertical frame). Known pitfalls:
- **Walls of `room()` block the camera:** use an open floor with no walls, or `camera "aerial"` with `focus` moved toward the camera (+z) so subjects sit in the top half.
- **`low_front`/`front`/`closeup` sit at −z looking toward +z:** objects placed at −z end up *behind* them. People face −z by default (`ry=180` faces the wide/follow cameras).
- **Multi-part props (`animal`, `dog`, planes, ships) with a `move` animation collapse into one point.** Animate them with `bob`/`wobble`, or move single objects only.
- **Tall `city()` buildings** block wide shots: use `far`/`aerial` or lower the zoom.
- **Thumbnail:** if the auto-picked beat is weak, re-render it: `whatif thumb <json> --beat N --text "..."`.
Re-run the sheet until every frame reads.

## 4. Render (detached, resumable)
```bash
mkdir -p /tmp/frames-<topic>
setsid nohup ./venv/bin/python -m backend.cli whatif render automation/scripts/<topic>.json \
  -o work/whatif/<slug>.mp4 --pack --frames-dir /tmp/frames-<topic> > /tmp/render-<topic>.log 2>&1 < /dev/null & disown
```
Wait with a background until-loop on the log (Shorts take about 10 min, long-form about 90 min). If the container restarts, re-run the same command: existing frames are skipped.
Then compress: `ffmpeg -i X.mp4 -c:v libx264 -preset slow -b:v 6M -maxrate 9M -bufsize 12M -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart X_c.mp4 && mv X_c.mp4 X.mp4`.
Long-form: render `hook.json` too, trim its end card (duration − 2.2 s), and concat it in front (see the git history for `long_swap_bodies_24h`).
Pull 4–5 frames from the final MP4 and look at them: frame 0, the middle, the end, and the thumbnail.

## 5. Metadata
`work/whatif/<slug>_youtube.txt` is generated by `--pack`. Replace its TAGS with about 10 specific search phrases (topic phrase first, then "what if", "fyp", "dink dunk"). For long-form, add a backup title and a sources line.

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
  - the pinned comment to post;
  - anything you could not do and why.
