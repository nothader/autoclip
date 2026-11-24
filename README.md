# DinkCam — first-person toy-world "what if" videos for Dink Dunk

    npm i                                   # three.js
    python3 -m venv venv && ./venv/bin/pip install numpy playwright kokoro-onnx soundfile
    ./venv/bin/python stories/<slug>.py     # writes stories/<slug>.json
    ./venv/bin/python -m dink.render stories/<slug>.json --sheet   # one still per beat -> out/<slug>_sheet.jpg
    ./venv/bin/python -m dink.render stories/<slug>.json           # -> out/<slug>.mp4

- web/engine.js: three.js renderer (bean people with googly eyes, mitten hands, rounded toy props, emoji props) + 2D overlay
  (hook title, word-pop captions, speech bubbles, badges, stamps, floaties, labels, meters, freeze-frame gags, progress bar).
- dink/assets.py: creatures, props and places. dink/kit.py: Story / beat API. dink/audio.py: synthesized SFX, generated music, Kokoro voices.
- Chrome: /usr/bin/google-chrome (or DINK_CHROME). Kokoro model: ~/.cache/dinkcam/tts (kokoro-v1.0.int8.onnx, voices-v1.0.bin).
