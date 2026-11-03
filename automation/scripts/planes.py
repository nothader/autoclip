"""What if airplanes didn't exist? (swap recipe, toon). Facts (rounded, widely cited): ~100,000 flights a day; NY->LA ~2,800 mi by road
(~41 h nonstop driving, ~4 days); transatlantic liner ~7 days (Queen Mary 2); Hawaii ~2,400 mi from California; donor hearts ~4-6 h outside the body;
air cargo ~35% of world trade by value (IATA); Japan's bullet trains reach ~200 mph."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
def plane(at, s=1.0, anim=()):
    x, y, z = at
    a = list(anim)
    return [O("capsule", at, [1.2 * s, 11 * s, 1.2 * s], "#f8f9fa", material="glossy", rotate=[90, 0, 0], animate=a),
            O("box", (x, y, z), [13 * s, 0.25 * s, 2.2 * s], "#dee2e6", animate=a),
            O("box", (x, y + 1.2 * s, z + 5 * s), [0.25 * s, 2.4 * s, 1.6 * s], "#1c7ed6", animate=a)]
tarmac = lambda extra=(): [O("box", (0, -0.02, -20), [200, 0.04, 200], "#868e96"), O("box", (0, 0, -20), [10, 0.03, 200], "#495057"),
                           O("box", (-30, 4, -40), [30, 8, 14], "#dee2e6"), O("box", (-30, 4, -32.9), [28, 4, 0.1], "#a5d8ff", material="glass")] + list(extra)
FADE = [{"type": "fade_out"}]
v.B(4.4, "wide", "In 3 seconds, every airplane on Earth vanishes. All 100,000 flights a day.",
    V(tarmac(plane((0, 1.3, -14), anim=FADE) + plane((14, 1.3, -26), anim=FADE) + plane((-6, 9, -40), anim=FADE + [{"type": "move", "to": [20, 16, -60]}])),
      SKY, focus=(2, 2, -18), zoom=1.8), "+0 SEC", "A NORMAL MONDAY", move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.8}])
term = room("#e9ecef", "#ced4da", "#a5d8ff", w=16, d=12, extra=[O("box", (0, 2.4, -11.9), [6, 1.4, 0.05], "#212529"),
             O("plane", (0, 2.4, -11.85), [5.6, 1.2, 1], "#e03131", material="glow", animate=[{"type": "pulse", "amount": 0.2, "speed": 2}]),
             crowd(18, 4, at=(0, 0, -6), spread=(14, 0, 8), act="idle"), O("box", (0, 0.3, -5), [0.5, 0.6, 0.3], "#7048e8", count=8, seed=6, spread=[12, 0, 8])])
v.B(3.4, "wide", "Your vacation? Cancelled. But wait till you see the hospitals.", V(term, ["#e9ecef", "#a5d8ff"], focus=(0, 1.4, -7), zoom=1.2, bounce="#e9ecef"),
    "+1 MIN", banner={"kicker": "DEPARTURES", "title": "ALL FLIGHTS CANCELLED", "subtitle": "FOREVER"})
desert = [O("box", (0, -0.02, -20), [400, 0.04, 400], "#d9a066"), O("box", (0, 0, -20), [8, 0.03, 400], "#495057"),
          O("box", (0, 0.01, -20), [0.15, 0.02, 400], "#ffd43b"), O("cone", (-60, 10, -120), [60, 20, 30], "#c97a40"), O("cone", (50, 14, -150), [70, 28, 30], "#b5652d"),
          O("box", (1.5, 0.65, -8), [2.0, 1.3, 4.4], "#e03131", animate=[{"type": "move", "to": [1.5, 0.65, -30]}])]
v.B(3.4, "follow", "New York to LA? Not 6 hours. About 4 days of driving.", V(desert, GOLD, focus=(1.5, 1, -14), zoom=1.4), "+1 DAY", transition="whip",
    stat={"value": "2,800 MI", "label": "NEW YORK TO LOS ANGELES", "count_up": True}, effects=["speedlines"])
ship = lambda: [O("box", (0, -0.4, -20), [600, 0.04, 600], "#1c7ed6", material="glossy"), O("box", (0, 1.2, -14), [6, 3, 26], "#212529", animate=[{"type": "bob", "amount": 0.3, "speed": 0.6}]),
                O("box", (0, 4.5, -14), [5, 3.6, 16], "#f8f9fa", animate=[{"type": "bob", "amount": 0.3, "speed": 0.6}]),
                O("cylinder", (0, 8, -12), [1.2, 3, 1.2], "#e03131", animate=[{"type": "bob", "amount": 0.3, "speed": 0.6}])]
v.B(3.4, "wide", "Going to Europe? Get on a ship. That's about a week each way.", V(ship(), SKY, focus=(0, 3, -14), zoom=2.4, amb="ocean"), "+1 WEEK",
    stat={"value": "7 DAYS", "label": "NEW YORK TO ENGLAND BY SHIP", "count_up": False})
island = [O("box", (0, -0.4, -20), [600, 0.04, 600], "#22b8cf", material="glossy"), O("sphere", (0, -3, -16), [16, 4, 12], "#ffe8a3"),
          O("cylinder", (-3, 3, -16), [0.3, 6, 0.3], "#8d6e57", rotate=[0, 0, 10]), O("cone", (-2.5, 6.2, -16), [3, 1, 3], "#2f9e44", rotate=[180, 0, 0]),
          O("cylinder", (4, 2.5, -17), [0.3, 5, 0.3], "#8d6e57", rotate=[0, 0, -8]), O("cone", (4.4, 5.2, -17), [3, 1, 3], "#2f9e44", rotate=[180, 0, 0]),
          O("box", (0, 0.6, -13), [1.4, 0.2, 0.6], "#f783ac", count=6, seed=3, spread=[10, 0, 4]),
          O("box", (0, -0.35, -6), [30, 0.05, 1.2], "#e7f5ff", opacity=0.7, animate=[{"type": "drift", "axis": "z", "amount": 0.4}])]
v.B(3.4, "establishing", "Hawaii is 2,400 miles from California. Its beaches go quiet.", V(island, ["#4dabf7", "#e3fafc"], focus=(0, 1.5, -16), zoom=2.0, amb="ocean"),
    "+1 MONTH", transition="whip")
hosp = room("#e7f5ff", "#dee2e6", w=12, d=12, extra=[O("box", (0, 0.5, -7), [1.4, 0.7, 2.6], "#f8f9fa"), P((-1.6, 0, -6.5), "#40c057", "walk", 8, outfit="scrubs", ry=90,
            anim=[{"type": "move", "to": [-0.8, 0, -6.5]}]), O("box", (1.6, 0.9, -6.5), [0.6, 0.5, 0.5], "#e03131")])
v.B(3.6, "aerial", "Here's the scary part: a donor heart only lasts about 4 to 6 hours.", V(hosp, ["#e7f5ff", "#d0ebff"], focus=(0, 0.5, 0.2), zoom=0.3, bounce="#e7f5ff"),
    "+2 MONTHS", transition="dip", effects=["tunnel"], sfx=[{"type": "heartbeat", "at": 0.2, "dur": 3.2, "gain": 0.8}],
    tooltip={"label": "REAL", "text": "Organs often fly to patients. Without planes, many couldn't arrive in time."})
store = room("#fff3bf", "#e9ecef", w=14, d=12, extra=[O("box", (-3, 0.9, -7), [0.8, 1.8, 8], "#adb5bd", material="metal"), O("box", (3, 0.9, -7), [0.8, 1.8, 8], "#adb5bd", material="metal"),
             O("box", (-3, 1.3, -7), [0.9, 0.2, 0.3], "#40c057", count=6, seed=4, spread=[0, 0, 7], animate=[{"type": "shrink"}]),
             O("box", (3, 1.3, -7), [0.9, 0.2, 0.3], "#212529", count=6, seed=5, spread=[0, 0, 7], animate=[{"type": "shrink"}]), crowd(5, 9, at=(0, 0, -6), spread=(3, 0, 8))])
v.B(3.4, "wide", "Planes carry about 35% of world trade by value. Phones get pricier.", V(store, ["#fff3bf", "#ffe066"], focus=(0, 1.2, -6), zoom=1.0, bounce="#fff3bf"),
    "+6 MONTHS", stat={"value": "35%", "label": "OF WORLD TRADE (BY VALUE) FLIES", "count_up": True})
rail = [O("box", (0, -0.02, -20), [300, 0.04, 300], "#69a84f"), O("box", (0, 0.05, -20), [3, 0.1, 300], "#868e96"),
        O("capsule", (0, 1.4, 10), [2.4, 40, 2.4], "#f8f9fa", material="glossy", rotate=[90, 0, 0], animate=[{"type": "move", "to": [0, 1.4, -80]}]),
        O("tree", (-20, 0, -60), 1.6, "#3f8f3a", count=14, seed=3, spread=[40, 0, 30])]
v.B(3.4, "side", "Super-fast trains take over. Like Japan's, at 200 mph.", V(rail, SKY, focus=(0, 1.4, -14), zoom=1.8), "+1 YEAR", transition="whip",
    effects=["speedlines"], sfx=[{"type": "whoosh", "at": 0.6, "dur": 1.8, "gain": 0.9}])
v.B(3.4, "wide", "And the sky? Totally quiet. No more jet trails.", V(park([crowd(6, 11, at=(0, 0, -10), spread=(20, 0, 6), act="idle"),
    O("cone", (0, 12, -20), [0.14, 0.45, 0.14], "#2b2f36", rotate=[0, 0, 90], count=14, seed=2, spread=[20, 4, 8], animate=[{"type": "drift", "axis": "x", "amount": 0.3}])]),
    ["#339af0", "#d0ebff"], focus=(0, 6, -14), zoom=1.6, amb="forest"), "+1 YEAR", effects=["rays"])
v.B(3.8, "far", "Would you take a 7-day boat for your next vacation?", V(ship(), DUSK, focus=(0, 3, -14), zoom=2.0, amb="ocean"), "+1 YEAR", move="pull_out", effects=["glow"])
v.save("planes", "What if airplanes didn't exist?", "Every airplane on Earth vanishes. Road trips, ships, hospitals, trade and the sky itself change.",
       "toon", "SINCE THE LAST FLIGHT", ["WOULD YOU TAKE", "A 7-DAY BOAT?"], "NO MORE *PLANES*", 0, accent="#4dabf7", captions=None, countdown=True)
