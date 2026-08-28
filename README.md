[README.md](https://github.com/user-attachments/files/31564192/README.md)
# HAND-E: Hand Tracking Robotic Arm

A 6-DOF robotic arm controlled by real-time hand tracking. A webcam captures hand movement, MediaPipe extracts the hand pose, and a Raspberry Pi drives the servos to mirror it.

## Status

Work in progress. Wrist bend and claw are active and mapped to hand tracking. Base, shoulder, elbow, and wrist rotation are currently locked while the control mapping is tuned.

## Architecture

- **MacBook**: runs OpenCV + MediaPipe hand tracking on the built-in webcam, converts hand pose into 6 servo angles, and sends them over TCP.
- **Raspberry Pi 4**: runs a socket server that receives the angles and drives the servos through a PCA9685 servo driver over I2C.

The Mac sends 6 comma-separated angles per line to the Pi on port 5005.

## Hardware

- Noennull 6DOF arm kit
- Raspberry Pi 4
- PCA9685 servo driver (I2C)
- OV5647 camera (not used for tracking; MediaPipe runs on the Mac's webcam instead)

## Servo Map

| Servo | Joint | Status |
|-------|-------------|--------|
| S0 | Base | Locked |
| S1 | Shoulder | Locked |
| S2 | Elbow | Locked |
| S3 | Wrist Bend | Active |
| S4 | Wrist Rotation | Locked |
| S5 | Claw | Active |

## Control Mapping

- Palm left/right → base rotation
- Palm up/down → shoulder
- Palm depth/reach → elbow
- Palm tilt → wrist bend
- Thumb-index pinch → claw

## Setup

### Pi side (VS Code Remote-SSH)

1. `Cmd+Shift+P`
2. `Remote-SSH: Connect to Host`
3. `sova@arm.local` (or connect through the Pi's terminal directly if mDNS resolution fails)
4. Find the Pi's IP if needed: `hostname -I`
5. Confirm SSH is running: `sudo systemctl status ssh`
6. From the Mac: `ssh sovannak@<pi-ip>`

### Mac side

```
cd ~/roboticarm
source venv/bin/activate
open -e arm_hand.py
# make edits, then Cmd+S to save
python arm_hand.py
```

### Running the server on the Pi

```
~/arm-venv/bin/python /home/sova/arm_server.py
```

## Notes

- If `arm.local` doesn't resolve, SSH by IP address instead.
- The Pi's Python environment lives in `~/arm-venv` with system site packages enabled for Blinka/ServoKit.

Built by Sovannak, Nick, Anh
