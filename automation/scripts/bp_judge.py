"""What if Jesus came back to judge? (Part 2 of the return; what happens to people who never believed.) Believer's POV, our own scenes.
Sources: Matthew 24:31 (a loud trumpet), Revelation 20:12 (the books were opened), Philippians 2:10-11 (every knee should bow),
Matthew 25:31-46 (he separates people as a shepherd separates sheep from goats; 'whatever you did for one of the least of these')."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DUSK, GOLDEN, OVERCAST  # noqa: E402
from places import street  # noqa: E402

s = Story()
ROOF = lambda extra=(), sky=DUSK, amb=1.3: env([O("box", (0, -0.02, -4), [14, 0.04, 12], "#4b4f58"), O("box", (0, 0.55, -10), [14, 1.1, 0.1], "#2b2f36"),
                                                O("box", (-3, 1.1, -5), [0.08, 2.2, 0.08], "#2f9e44", count=2, seed=1, spread=[6, 0, 0]),
                                                O("box", (-3, 2.2, -5), [6, 0.08, 0.08], "#2f9e44"),
                                                O("box", (0, 20, -40), [14, 40, 14], "#8d97a5"), O("box", (-22, 14, -46), [12, 28, 12], "#a8b0bb"),
                                                O("box", (22, 18, -50), [12, 36, 12], "#7d8794")] + list(extra), sky, eye=(0, 1.62, 1.6), amb="wind", ambient=amb)
BRO = lambda act="idle", face="neutral", anim=(): guy((0.9, 0, -1.6), "#1f6f5a", "#212529", act=act, face=face, seed=1201, ry=200, anim=anim)
GIRL = lambda act="idle", face="smile", anim=(): guy((-0.9, 0, -2.0), "#f8f9fa", "#3f4a5a", act=act, face=face, seed=1202, ry=160, anim=anim)
HOMELESS = guy((-1.6, 0.12, -4.6), "#7a6a55", "#5a524a", act="sit", face="sad", seed=1203, ry=150)
LIGHT = [O("sphere", (0, 26, -70), 5, "#fffbe8", material="glow"), O("block_person", (0, 21.5, -68), 2.4, "#fff8e8", seed=1299, action="float", expression="neutral", rotate=[0, 180, 0]),
         O("cone", (0, 26, -70), [30, 3, 30], "#fff3d0", material="glow", opacity=0.25)]
BRIGHT = ["#7f8fbf", "#ffe8c0"]

s.B(3.8, "eyes", "", env(street(seed=121, people=12, cars=3, extra=[HOMELESS]), GOLDEN, eye=(0, 1.62, 2.4), amb="calm"), tracker=T("HE RETURNS IN", scramble=True, sub="PART 2"),
    hands={"pose": "phone", "phone_text": "rooftop at 6?", "phone_time": "5:48"}, gaze=(-18, -10), head="walk")
s.B(3.4, "eyes", "You walk past a man asking for food. Like every day.", env(street(seed=121, people=12, cars=3, extra=[HOMELESS]), GOLDEN, eye=(0, 1.62, 1.2), amb="calm"),
    hands={"pose": "phone", "phone_text": "rooftop at 6?", "phone_time": "5:49"}, gaze=(-28, -12), head="walk", voices=[("Spare anything? Anything at all?", "am_adam", 0.5)])
s.B(3.6, "eyes", "Evening. Pull-ups on the roof with your two best friends.", ROOF([BRO(), GIRL()]), hands={"pose": "idle"}, gaze=(0, -4))
s.B(3.4, "eyes", "She wears a cross. He thinks it's all a story.", ROOF([BRO(face="smirk"), GIRL()]), hands={"pose": "idle"}, gaze=(10, -2),
    voices=[("You actually believe that stuff?", "am_eric", 0.5)])
s.B(3.2, "eyes", "And you? You never really decided.", ROOF([BRO(), GIRL()]), tracker=T("YOU", value="UNDECIDED", sub="LIKE MOST PEOPLE"), hands={"pose": "none"}, gaze=(0, 10))
s.B(3.6, "eyes", "Out of nowhere: a trumpet. The sky lights up.", ROOF([BRO(face="shock"), GIRL(face="shock")] + LIGHT, BRIGHT, 1.8), by="Matthew 24:31",
    tracker=T("TRUMPET", count=(1, 7), unit=" / 7"), hands={"pose": "shield"}, gaze=(0, 22), effects=["shake", "rays"], sfx=[{"type": "swell", "at": 0.1, "dur": 3.2, "gain": 1.2}])
s.B(3.8, "far", "Every eye in the city sees him.", env(street(seed=122, people=80, cars=4, extra=LIGHT), BRIGHT, focus=(0, 6, -20), zoom=3.4, amb="wind"),
    tracker=T("HE RETURNS IN", value="00:00:00", sub="HE IS HERE", alert=True), effects=["rays"])
s.B(3.6, "eyes", "Then every knee bows. Even the ones who never believed.", env(street(seed=123, people=0, cars=3, extra=LIGHT + [crowd(80, 1231, at=(0, 0.12, -12), spread=(10, 0, 18),
                                                                                                                                  act="pray", ry=180)]),
                                                                              BRIGHT, eye=(0, 4, 2), amb="wind"), by="Philippians 2:10", hands={"pose": "none"}, gaze=(0, -18))
s.B(3.6, "eyes", "Your friend kneels next to you. Shaking.", ROOF([BRO("kneel", "shock"), GIRL("pray", "smile")] + LIGHT, BRIGHT, 1.8), hands={"pose": "none"}, gaze=(14, -14))
s.B(3.6, "eyes", "Then the books are opened. Everything you ever did.", ROOF(LIGHT + [O("box", (0, 2.2, -3), [1.2, 0.08, 0.9], "#f1ece4", animate=[{"type": "bob", "amount": 0.1}])],
                                                                             BRIGHT, 1.8), by="Revelation 20:12", hands={"pose": "none"}, gaze=(0, 10), effects=["bloom"])
s.B(3.6, "eyes", "He separates everyone. Like a shepherd with his sheep.", env(street(seed=124, people=0, cars=0, extra=LIGHT + [
    crowd(50, 1241, at=(-5, 0.12, -14), spread=(6, 0, 14), act="cheer", face="smile", ry=180), crowd(50, 1242, at=(5, 0.12, -14), spread=(6, 0, 14), act="idle", face="sad", ry=180)]),
    BRIGHT, eye=(0, 9, 4), amb="wind"), by="Matthew 25:32", tracker=T("RIGHT | LEFT", value="RISE | STAY", sub="ON YOUR STREET"), gaze=(0, -30), hands={"pose": "none"})
s.B(3.6, "eyes", "Your girl rises toward him.", ROOF([BRO("kneel", "sad"), GIRL("float", "smile", [{"type": "move", "to": [-0.9, 3.0, -2.0]}])] + LIGHT, BRIGHT, 1.8),
    hands={"pose": "reach"}, gaze=(-10, 24), effects=["bloom"])
s.B(3.4, "eyes", "Your boy stays below.", ROOF([BRO("kneel", "sad")] + LIGHT, BRIGHT, 1.6), hands={"pose": "none"}, gaze=(14, -14))
s.B(3.8, "eyes", "And you? It comes down to one question.", ROOF(LIGHT, BRIGHT, 1.8), tracker=T("YOU", value="?", sub="WAITING", big=True), hands={"pose": "none"}, gaze=(0, 20),
    effects=["rays"])
s.B(3.8, "eyes", "The man you walked past this morning. That counts.", env(street(seed=121, people=6, cars=1, extra=[HOMELESS] + LIGHT), BRIGHT, eye=(0, 1.62, 1.2), amb="calm"),
    by="Matthew 25:40", hands={"pose": "none"}, gaze=(-28, -12))

s.save("bp_judge", "What if *Jesus* came back to judge?",
       "Believer's POV, part 2: a rooftop with a believing friend and a skeptic; a trumpet, every knee bows, the books are opened, people are separated, and the man you walked past that morning matters.",
       "Do you make it to heaven?", accent="#f2c94c", skin="#8d5524", sleeve="#212529", thumb="RISE OR STAY?", thumb_beat=10)
