import socket
from adafruit_servokit import ServoKit

# =========================================================
# SERVO CONTROLLER
# =========================================================

kit = ServoKit(channels=16)

# =========================================================
# LOCKED POSITIONS
# =========================================================

SERVO_0_LOCK = 95
SERVO_1_LOCK = 90
SERVO_2_LOCK = 100
SERVO_4_LOCK = 50

# =========================================================
# SERVO 3 SAFE RANGE
# =========================================================

SERVO_3_MIN = 45
SERVO_3_MAX = 135
SERVO_3_START = 90
SERVO_3_MAX_STEP = 3.0

# =========================================================
# SET STARTING ARM POSITION
# =========================================================

kit.servo[0].angle = SERVO_0_LOCK
kit.servo[1].angle = SERVO_1_LOCK
kit.servo[2].angle = SERVO_2_LOCK
kit.servo[3].angle = SERVO_3_START
kit.servo[4].angle = SERVO_4_LOCK
kit.servo[5].angle = 90

print("Arm initialized.")
print(f"S0 = {SERVO_0_LOCK} LOCKED")
print(f"S1 = {SERVO_1_LOCK} LOCKED")
print(f"S2 = {SERVO_2_LOCK} LOCKED")
print("S3 = ACTIVE")
print(f"S4 = {SERVO_4_LOCK} LOCKED")
print("S5 = ACTIVE")

# =========================================================
# NETWORK SERVER
# =========================================================

HOST = "0.0.0.0"
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print()
print(f"Arm server listening on port {PORT}.")
print("Waiting for Mac...")

conn, addr = server.accept()
print(f"Connected by {addr}")

buffer = ""
current_servo_3 = float(SERVO_3_START)

# =========================================================
# RECEIVE COMMANDS
# =========================================================

try:
    while True:
        data = conn.recv(1024)

        if not data:
            print("Mac disconnected.")
            break

        buffer += data.decode()

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue

            try:
                angles = [float(x) for x in line.split(",")]

                if len(angles) != 6:
                    continue

                # =========================================
                # SERVO 3 — WRIST BEND
                # Step-limited to prevent sudden jumps
                # =========================================

                raw_3 = max(SERVO_3_MIN, min(SERVO_3_MAX, angles[3]))
                step = max(-SERVO_3_MAX_STEP, min(SERVO_3_MAX_STEP, raw_3 - current_servo_3))
                current_servo_3 += step
                kit.servo[3].angle = current_servo_3

                # =========================================
                # SERVO 5 — CLAW
                # =========================================

                claw_angle = max(0, min(180, angles[5]))
                kit.servo[5].angle = claw_angle

            except ValueError:
                print(f"Bad command: {line}")

except KeyboardInterrupt:
    print("\nStopping arm server.")

finally:
    conn.close()
    server.close()
    print("Server closed.")
