import cv2
import socket
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# =========================================================
# RASPBERRY PI CONNECTION
# =========================================================

PI_HOST = "192.168.1.229"
PI_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to arm...")
sock.connect((PI_HOST, PI_PORT))
print("Connected.")


# =========================================================
# SERVO SETTINGS
# =========================================================

SERVO_0_LOCK = 95
SERVO_1_LOCK = 90
SERVO_2_LOCK = 100
SERVO_4_LOCK = 50

SERVO_3_MIN = 45
SERVO_3_MAX = 135

SMOOTHING = 0.15


# =========================================================
# MEDIAPIPE SETUP
# =========================================================

base_options = python.BaseOptions(
    model_asset_path="hand_landmarker.task"
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(options)


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)

time.sleep(2)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def to_angle(value, in_min, in_max, out_min, out_max):
    value = (value - in_min) / (in_max - in_min)
    value = max(0.0, min(1.0, value))
    return out_min + value * (out_max - out_min)


def dist(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


# =========================================================
# STARTING SERVO POSITIONS
#
# S0 = LOCKED
# S1 = LOCKED
# S2 = LOCKED
# S3 = ACTIVE — HAND FRONT / BACK
# S4 = LOCKED
# S5 = ACTIVE — THUMB / INDEX PINCH
# =========================================================

angles = [
    SERVO_0_LOCK,
    SERVO_1_LOCK,
    SERVO_2_LOCK,
    90,
    SERVO_4_LOCK,
    90
]

last_send = 0


# =========================================================
# MAIN LOOP
# =========================================================

try:

    while True:

        ok, frame = cap.read()

        if not ok:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = detector.detect(mp_image)

        angles[0] = SERVO_0_LOCK
        angles[1] = SERVO_1_LOCK
        angles[2] = SERVO_2_LOCK
        angles[4] = SERVO_4_LOCK

        if result.hand_landmarks:

            pts = result.hand_landmarks[0]

            middle_mcp = pts[9]
            thumb_tip = pts[4]
            index_tip = pts[8]

            for p in pts:
                cx = int(p.x * w)
                cy = int(p.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

            palm_z = middle_mcp.z
            pinch = dist(thumb_tip, index_tip)

            # =============================================
            # SERVO 3 — WRIST BEND
            #
            # Hand pushed toward camera: SERVO_3_MIN
            # Hand pulled back: SERVO_3_MAX
            # =============================================

            target_servo_3 = to_angle(
                palm_z,
                -0.10,
                0.10,
                SERVO_3_MIN,
                SERVO_3_MAX
            )
