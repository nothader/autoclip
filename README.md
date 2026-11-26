# DinkCam — first-person "what if" videos for Dink Dunk

> **Direction since 2026-11-26: humans and real-life scenarios only — no animals, creatures or fantasy premises, no bean() people.**
> New stories use the v2 film look (now the default for `Story`), `person()`/`people()` and the real-life sets — see the v2 section below
> and `stories/first_thanksgiving.py`. Renders take ~15 min per Short: run them in the background with `--frames-dir` and poll.

    npm i                                   # three.js
    python3 -m venv venv && ./venv/bin/pip install numpy playwright kokoro-onnx soundfile
    ./venv/bin/python stories/<slug>.py     # writes stories/<slug>.json
    ./venv/bin/python -m dink.render stories/<slug>.json --sheet   # one still per beat -> out/<slug>_sheet.jpg
    ./venv/bin/python -m dink.render stories/<slug>.json           # -> out/<slug>.mp4

- web/engine.js: three.js renderer (bean people with googly eyes, mitten hands, rounded toy props, emoji props) + 2D overlay
  (hook title, word-pop captions, speech bubbles, badges, stamps, floaties, labels, meters, freeze-frame gags, progress bar).
- dink/assets.py: creatures, props and places. dink/kit.py: Story / beat API. dink/audio.py: synthesized SFX, generated music, Kokoro voices.
- Chrome: /usr/bin/google-chrome (or DINK_CHROME). Kokoro model: ~/.cache/dinkcam/tts (kokoro-v1.0.int8.onnx, voices-v1.0.bin).

## v2 "film look" — humans & real life (2026-11-26)

`Story(..., look="film")` switches the engine to the v2 pipeline (old stories keep the toy look unchanged):

- **People** — `person(at, top, bottom, skin, hair, outfit, age, expr, act, talk=[(start, dur)], hold=...)`: jointed humans
  (arms/legs/hands), eyes that blink and follow the camera, brows, lip-sync, 13 hair styles, beards, glasses, hats,
  14 outfits, ages kid/teen/adult/elder, ~50 acts (talk, walk, sit_type, phone, call, facepalm, panic, cheer…), 21 expressions.
  `people(n, seed, …)` makes a varied deterministic crowd. Lists: `ACTS`, `EXPRS`, `OUTFITS`, `HAIRS`, `SKIN`, `HAIR`.
- **Your hands** — real 5-finger hands + sleeves (+ `watch=True`). Poses: idle point reach hold wave shrug facepalm shield run
  cheer thumbsup fist peace stop offer phone wheel type grab count money none. `hands="phone", screen=screen_ui(...)` shows
  a real phone UI (chat bubbles, big numbers, buttons).
- **Real places** — textured `room()` shells and sets: apartment, bedroom, kitchen_home, office, meeting_room, cafe, street,
  car_inside, gym, elevator, school_hall, grocery, restaurant, airport_gate, classroom_real, front_door; props: table, chair,
  office_chair, desk, laptop, monitor, plant, window, door, bookshelf, fridge, counter, bed, alarm_clock, steering_wheel,
  shopping_cart, car_real, traffic_light, street_lamp, building, bench, locker_row, dumbbell, treadmill, coffee_machine,
  menu_board, cash_register, elevator_doors, roast_turkey, oven, smoke_cloud, dining_table. `text()` = signs with real words,
  `screen_panel()` = TVs/monitors/boards, `lamp()`/`spotlight()` = real lights. Surfaces take `tex=` (planks tiles bricks asphalt
  grass carpet concrete marble stripes wallpaper sidewalk fabric paint).
- **Rendering** — image-based lighting, ground-truth AO, soft shadows, bloom, camera-side fill light, gentle handheld drift,
  depth of field per shot (`cam(..., dof=True)`), film grade with grain (`Story(grade={...})`, per-beat `beat(grade=...)`).
- New SFX: `alarm`, `doorbell`, `notify`.
- Reference story: `stories/first_thanksgiving.py`. Pose/hand/face galleries: `stories/_poses.py`, `_hands.py`, `_faces.py`.
- Framing in 9:16: at depth d only about ±0.33·d m is visible left/right — keep subjects near the look line, faces 1.5–3 m away,
  and use `hands="none"`/`"idle"` when a face matters.
- **Speed (2 CPU cores, software WebGL):** film-look Short ≈15 min (SMAA by default; `Story(msaa=…)` is not exposed because
  MSAA doubles render time). Long-form: use `Story(..., render_scale=0.75)` → ≈100 min for 5 min of 1080p. Always render in the
  background with `--frames-dir` (resumable) and poll.
