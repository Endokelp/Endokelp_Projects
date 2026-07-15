"""
fire & ice hand particles
left hand = fire, right = ice, both close = fusion
point index to draw, fist to explode
q quit / r reset / s screenshot / f fullscreen / 1-3 themes / b stars
"""

import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time
import os

# was 6k lol dont — laptop webcam dies around that
PARTICLE_COUNT = 1000
HAND_RADIUS = 180
IDEAL_ORBIT_R = 80
ORBIT_FORCE = 0.75
REPEL_FORCE = 0.015
NOISE_F = 0.6
DAMPING = 0.90
HAND_DAMPING = 0.90
MAX_SPEED = 6.0
HAND_SPEED = 15.0
SMOOTH = 0.18
TRAIL_FADE = 0.85
CANVAS_FADE = 0.99
CAM_BRIGHTNESS = 0.30
SCREENSHOT_DIR = "screenshots"
STAR_COUNT = 40  # 300 was overkill
CAM_W, CAM_H = 640, 480  # keep cam small or mediapipe eats the frame budget

# bgr palettes — theme 1 is default
FIRE_PALETTES = {
    1: [(100,180,255),(80,120,255),(40,60,255),(20,40,220),(200,240,255)],
    2: [(0,150,255),(0,100,200),(0,200,255),(0,80,180),(50,220,255)],
    3: [(50,50,255),(30,30,200),(150,80,255),(200,100,255),(255,200,255)],
}
ICE_PALETTES = {
    1: [(255,255,255),(255,240,240),(255,220,150),(255,120,120),(250,200,100)],
    2: [(255,230,100),(255,255,200),(200,255,255),(150,240,255),(255,255,255)],
    3: [(255,200,150),(255,170,80),(200,220,255),(180,255,255),(255,255,255)],
}
FUSION_PALETTE = [
    (100,255,200),(50,255,150),(200,200,255),(255,100,200),(255,200,100),
]

mp_hands = mp.solutions.hands
PALM_IDS = [0, 5, 9, 13, 17]


def is_index_pointing(lm):
    # tip above pip, other fingers curled
    index_up = lm[8].y < lm[6].y
    mid_down = lm[12].y > lm[10].y
    ring_down = lm[16].y > lm[14].y
    pink_down = lm[20].y > lm[18].y
    return index_up and mid_down and ring_down and pink_down


def is_fist(lm):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    return all(lm[t].y > lm[p].y for t, p in zip(tips, pips))


def is_open_palm(lm):
    tips = [8, 12, 16, 20]
    mcps = [5, 9, 13, 17]
    return all(lm[t].y < lm[m].y for t, m in zip(tips, mcps))


def get_hand_gesture(lm):
    if is_index_pointing(lm):
        return "write"
    if is_fist(lm):
        return "fist"
    if is_open_palm(lm):
        return "open"
    return "neutral"


class Star:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.x = random.uniform(0, W)
        self.y = random.uniform(0, H)
        self.r = random.uniform(0.3, 1.5)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.01, 0.04)
        self.base = random.uniform(0.2, 0.6)

    def draw(self, frame):
        a = self.base + math.sin(self.phase) * 0.3
        self.phase += self.speed
        b = int(a * 255)
        cv2.circle(frame, (int(self.x), int(self.y)), max(1, int(self.r)), (b, b, b), -1)


class Particle:
    def __init__(self, W, H, theme=1):
        self.W, self.H = W, H
        self.theme = theme
        self.element = None
        self.color = (255, 255, 255)
        self.fusion = False
        self._spawn()

    def _spawn(self):
        self.x = random.uniform(0, self.W)
        self.y = random.uniform(0, self.H)
        self.vx = random.gauss(0, 0.6)
        self.vy = random.gauss(0, 0.6)
        self.size = random.uniform(0.8, 2.2)
        self.original_alpha = random.uniform(0.6, 1.0)
        self.alpha_base = self.original_alpha
        self.drift_ang = random.uniform(0, math.pi * 2)
        self.drift_rot = random.uniform(0.005, 0.020) * random.choice([1, -1])
        self.twinkle = random.uniform(0, math.pi * 2)
        self.twinkle_sp = random.uniform(0.04, 0.12)
        self.life = 1.0
        self.tail = []  # unused now, tails were too expensive

    def update(self, hands_info, fusion_active=False):
        self.twinkle += self.twinkle_sp
        self.drift_ang += self.drift_rot

        if not hands_info:
            self.alpha_base = 0.0
            self.vx *= 0.5
            self.vy *= 0.5
            return False, 0.0

        self.alpha_base = self.original_alpha

        # closest hand
        best_d, best_hand = float("inf"), None
        for h in hands_info:
            tx, ty = (h["tip"] if h["gesture"] == "write" else h["pos"])
            d = math.hypot(self.x - tx, self.y - ty)
            if d < best_d:
                best_d, best_hand = d, h

        tx, ty = (best_hand["tip"] if best_hand["gesture"] == "write" else best_hand["pos"])
        dx = self.x - tx
        dy = self.y - ty
        d = math.hypot(dx, dy) or 0.001

        new_elem = "Fusion" if fusion_active else best_hand["element"]
        if self.element != new_elem:
            self.element = new_elem
            if fusion_active:
                self.color = random.choice(FUSION_PALETTE)
            else:
                palette = FIRE_PALETTES[self.theme] if new_elem == "Fire" else ICE_PALETTES[self.theme]
                self.color = random.choice(palette)
        self.fusion = fusion_active

        is_writing = best_hand["gesture"] == "write"
        is_fist_g = best_hand["gesture"] == "fist"

        snap_r = HAND_RADIUS * (0.4 if is_writing else 1.2)
        orbit_r = IDEAL_ORBIT_R * (0.1 if is_writing else (2.0 if fusion_active else 1.0))
        logic_r = HAND_RADIUS * (0.5 if is_writing else 1.5)

        # teleport if too far — ugly but works
        if d > snap_r:
            ang = random.uniform(0, math.pi * 2)
            r_new = random.uniform(0, snap_r * 0.8)
            self.x = tx + math.cos(ang) * r_new
            self.y = ty + math.sin(ang) * r_new
            dx = self.x - tx
            dy = self.y - ty
            d = math.hypot(dx, dy) or 0.001

        fx, fy = 0.0, 0.0
        near_hand = False

        if d < logic_r:
            near_hand = True
            nx, ny = dx / d, dy / d
            tx2, ty2 = -ny, nx

            t_str = ORBIT_FORCE * (1.0 - d / logic_r)
            if is_writing:
                t_str *= 3.0
            if fusion_active:
                t_str *= 2.0
            fx += tx2 * t_str * 9.0
            fy += ty2 * t_str * 9.0

            shell_err = orbit_r - d
            rep = REPEL_FORCE * (5.0 if is_writing else 1.0)
            fx += nx * shell_err * rep
            fy += ny * shell_err * rep

            if self.element == "Fire":
                fy -= 0.8  # rises
            elif self.element == "Ice":
                fy += 0.4
                fx += random.gauss(0, 0.3)
            elif self.element == "Fusion":
                ang2 = math.atan2(dy, dx) + 0.08
                fx += math.cos(ang2) * 1.5
                fy += math.sin(ang2) * 1.5

            if is_fist_g:
                fx += nx * 4.0
                fy += ny * 4.0

        fx += random.gauss(0, NOISE_F)
        fy += random.gauss(0, NOISE_F)

        self.vx += fx
        self.vy += fy

        damp = HAND_DAMPING if near_hand else DAMPING
        if is_writing:
            damp *= 0.80
        if fusion_active:
            damp *= 0.85
        self.vx *= damp
        self.vy *= damp

        spd = math.hypot(self.vx, self.vy)
        cap = HAND_SPEED if near_hand else MAX_SPEED
        if spd > cap:
            self.vx = self.vx / spd * cap
            self.vy = self.vy / spd * cap

        self.x += self.vx
        self.y += self.vy

        return near_hand, spd

    def draw(self, layer, near_hand, spd):
        if self.alpha_base <= 0.01:
            return
        ix, iy = int(self.x), int(self.y)
        if not (0 <= ix < self.W and 0 <= iy < self.H):
            return

        twinkle = 0.6 + math.sin(self.twinkle) * 0.4
        spd_frac = min(spd / HAND_SPEED, 1.0)
        a = self.alpha_base * twinkle
        r = max(1, int(self.size * (1.0 + spd_frac * 0.8)))
        core = tuple(int(c * a) for c in self.color)
        # just a circle, glow rings were tanking fps
        cv2.circle(layer, (ix, iy), r + (2 if self.fusion else 0), core, -1)


def put_text_shadow(img, text, pos, font, scale, color, thick=1):
    # name lied, no shadow anymore — too slow
    cv2.putText(img, text, pos, font, scale, color, thick)


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    ret, probe = cap.read()
    if not ret:
        print("no camera?")
        return

    H, W = probe.shape[:2]
    print(f"cam {W}x{H}, {PARTICLE_COUNT} particles")
    print("left=fire right=ice both close=fusion")
    print("point to draw, fist explodes")
    print("q/r/s/f/b  1-3 themes")

    theme = 1
    show_stars = True
    fullscreen = False
    screenshot_n = 0
    fps_t = time.time()
    fps_val = 0.0
    frame_count = 0
    tick = 0
    session_start = time.time()

    particles = [Particle(W, H, theme) for _ in range(PARTICLE_COUNT)]
    particle_layer = np.zeros((H, W, 3), dtype=np.uint8)
    canvas_layer = np.zeros((H, W, 3), dtype=np.uint8)
    stars = [Star(W, H) for _ in range(STAR_COUNT)]
    star_layer = np.zeros((H, W, 3), dtype=np.uint8)
    smooth_hands = []

    # complexity 0 is fine for this, 1 was laggy on my machine
    hands_model = mp_hands.Hands(
        max_num_hands=2,
        model_complexity=0,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )

    cv2.namedWindow("Fire & Ice Magic", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Fire & Ice Magic", W, H)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1
        tick += 1

        now = time.time()
        if now - fps_t >= 0.5:
            fps_val = frame_count / (now - fps_t)
            frame_count = 0
            fps_t = now

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_model.process(rgb)

        raw_hands = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_lm, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                element = "Fire" if label == "Left" else "Ice"
                lm = hand_lm.landmark
                sx = sum(lm[i].x * W for i in PALM_IDS) / len(PALM_IDS)
                sy = sum(lm[i].y * H for i in PALM_IDS) / len(PALM_IDS)
                tx, ty = lm[8].x * W, lm[8].y * H
                gesture = get_hand_gesture(lm)
                raw_hands.append(
                    {"pos": [sx, sy], "tip": [tx, ty], "gesture": gesture, "element": element}
                )

        new_smooth = []
        for raw in raw_hands:
            best_s, best_d2 = None, float("inf")
            for s in smooth_hands:
                if s["element"] == raw["element"]:
                    d2 = math.hypot(s["pos"][0] - raw["pos"][0], s["pos"][1] - raw["pos"][1])
                    if d2 < best_d2:
                        best_d2, best_s = d2, s

            if best_s and best_d2 < 300:
                sp = [
                    best_s["pos"][0] + (raw["pos"][0] - best_s["pos"][0]) * SMOOTH,
                    best_s["pos"][1] + (raw["pos"][1] - best_s["pos"][1]) * SMOOTH,
                ]
                tp = [
                    best_s["tip"][0] + (raw["tip"][0] - best_s["tip"][0]) * SMOOTH,
                    best_s["tip"][1] + (raw["tip"][1] - best_s["tip"][1]) * SMOOTH,
                ]
                new_smooth.append(
                    {
                        "pos": sp,
                        "tip": tp,
                        "gesture": raw["gesture"],
                        "element": raw["element"],
                    }
                )
                if raw["gesture"] == "write" and best_s["gesture"] == "write":
                    c_glow = (
                        FIRE_PALETTES[theme][2]
                        if raw["element"] == "Fire"
                        else ICE_PALETTES[theme][2]
                    )
                    pt1 = (int(best_s["tip"][0]), int(best_s["tip"][1]))
                    pt2 = (int(tp[0]), int(tp[1]))
                    cv2.line(canvas_layer, pt1, pt2, c_glow, 10)
                    cv2.line(canvas_layer, pt1, pt2, (255, 255, 255), 3)
            else:
                new_smooth.append(raw)

        smooth_hands = new_smooth

        fusion_active = False
        if len(smooth_hands) == 2:
            d_hands = math.hypot(
                smooth_hands[0]["pos"][0] - smooth_hands[1]["pos"][0],
                smooth_hands[0]["pos"][1] - smooth_hands[1]["pos"][1],
            )
            fusion_active = d_hands < 180

        cv2.convertScaleAbs(canvas_layer, canvas_layer, alpha=TRAIL_FADE)
        cv2.convertScaleAbs(particle_layer, particle_layer, alpha=TRAIL_FADE)

        n_hands = len(smooth_hands)
        for i, p in enumerate(particles):
            p.theme = theme
            assigned = [smooth_hands[i % n_hands]] if n_hands > 0 else []
            near, spd = p.update(assigned, fusion_active)
            p.draw(particle_layer, near, spd)

        # every other frame is enough for stars
        if show_stars and (tick % 2 == 0):
            star_layer[:] = 0
            for s in stars:
                s.draw(star_layer)

        dark_cam = cv2.convertScaleAbs(frame, alpha=CAM_BRIGHTNESS, beta=0)
        if show_stars:
            dark_cam = cv2.add(dark_cam, star_layer)
        output = cv2.add(cv2.add(dark_cam, canvas_layer), particle_layer)

        elapsed = int(time.time() - session_start)
        mm, ss = divmod(elapsed, 60)
        n = len(smooth_hands)
        if n == 0:
            label, lc = "No Hands", (80, 80, 80)
        elif n == 1:
            label, lc = f"{smooth_hands[0]['element']}", (80, 220, 80)
        elif fusion_active:
            label, lc = "FUSION", (80, 255, 180)
        else:
            label, lc = "both hands", (80, 220, 200)

        put_text_shadow(output, label, (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, lc, 1)
        put_text_shadow(
            output,
            f"FPS {fps_val:.0f}  {mm:02d}:{ss:02d}",
            (W - 160, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
        )
        put_text_shadow(
            output,
            "q quit  point:draw  fist:boom",
            (16, H - 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (180, 180, 180),
        )

        cv2.imshow("Fire & Ice Magic", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r"):
            particles = [Particle(W, H, theme) for _ in range(PARTICLE_COUNT)]
            particle_layer[:] = 0
            canvas_layer[:] = 0
            print("reset")
        elif key == ord("s"):
            fname = os.path.join(SCREENSHOT_DIR, f"fireice_{int(time.time())}.png")
            cv2.imwrite(fname, output)
            screenshot_n += 1
            print(f"saved {fname}")
        elif key == ord("f"):
            fullscreen = not fullscreen
            flag = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
            cv2.setWindowProperty("Fire & Ice Magic", cv2.WND_PROP_FULLSCREEN, flag)
        elif key == ord("b"):
            show_stars = not show_stars
            print("stars on" if show_stars else "stars off")
        elif key in (ord("1"), ord("2"), ord("3")):
            theme = int(chr(key))
            for p in particles:
                p.theme = theme
                p.element = None
            print(f"theme {theme}")

    cap.release()
    hands_model.close()
    cv2.destroyAllWindows()
    print(f"done, {screenshot_n} screenshots")


if __name__ == "__main__":
    main()
