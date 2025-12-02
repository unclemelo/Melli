import time
from time import sleep
import math
from pythonosc.udp_client import SimpleUDPClient


# --------------------------------------------------------
# Smooth Utility
# --------------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t


# --------------------------------------------------------
# EXPRESSIONS UTILS
# --------------------------------------------------------
class Expressions:

    @staticmethod
    def smile(vmc):
        vmc.set_blendshape("Joy", 1.0)
        sleep(0.25)
        vmc.set_blendshape("Joy", 0.0)

    @staticmethod
    def angry(vmc):
        vmc.set_blendshape("Angry", 1.0)
        sleep(0.25)
        vmc.set_blendshape("Angry", 0.0)

    @staticmethod
    def neutral(vmc):
        vmc.set_blendshape("Neutral", 1.0)
        sleep(0.1)
        vmc.set_blendshape("Neutral", 0.0)

    @staticmethod
    def sad(vmc):
        vmc.set_blendshape("Sad", 1.0)
        sleep(0.25)
        vmc.set_blendshape("Sad", 0.0)

    @staticmethod
    def mouth_open(vmc, amount: float):
        vmc.set_blendshape("A", float(amount))


# --------------------------------------------------------
# BONE UTILS
# --------------------------------------------------------
class Bones:

    @staticmethod
    def nod_head(vmc):
        vmc.rotate_bone("Head", 0.0, 0.2, 0.0, 0.98)


# --------------------------------------------------------
# VMC CLIENT
# --------------------------------------------------------
class VMCClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 39539):
        print(f"[INIT] Connecting to VMC at {host}:{port}")
        self.client = SimpleUDPClient(host, port)
        print(f"[SUCCESS] You've succesfully conntected to {host}:{port}")
        self.idle_animation(duration=8)

    # Smooth blendshape over duration
    def smooth_blendshape(self, name: str, start: float, end: float, duration: float = 0.4, steps: int = 20):
        print(f"[SMOOTH] {name}: {start} → {end}")
        for i in range(steps + 1):
            t = i / steps
            value = lerp(start, end, t)
            self.set_blendshape(name, value)
            sleep(duration / steps)

    def set_blendshape(self, name: str, value: float):
        self.client.send_message("/VMC/Ext/Blend/Val", [name, float(value)])
        self.client.send_message("/VMC/Ext/Blend/Apply", 1)

    # Smooth bone rotation using quaternion lerp (simple version)
    def smooth_bone_rotation(self, bone: str, start_q, end_q, duration=0.4, steps=20):
        print(f"[SMOOTH BONE] {bone}")
        for i in range(steps + 1):
            t = i / steps
            q = [lerp(start_q[j], end_q[j], t) for j in range(4)]
            self.rotate_bone(bone, *q)
            sleep(duration / steps)

    def rotate_bone(self, bone: str, qx, qy, qz, qw):
        self.client.send_message("/VMC/Ext/Bone/Pos", [
            bone,
            0.0, 0.0, 0.0,
            float(qx), float(qy), float(qz), float(qw)
        ])

    # --------------------------------------------------------
    # Idle Animation (Enhanced)
    # --------------------------------------------------------
    def idle_animation(self, duration=10):
        print("[IDLE] Enhanced body idle animation...")
        t = 0

        while t < duration:

            # BREATHING
            breath = (math.sin(t * 1.5) + 1) / 2
            chest_up = breath * 0.12
            self.rotate_bone("Chest", chest_up, 0.0, 0.0, 1.0)
            self.set_blendshape("Breath", breath * 0.4)

            # BODY SWAY
            sway = math.sin(t * 0.8) * 0.15
            forward_back = math.sin(t * 0.5) * 0.1

            self.rotate_bone("Spine", 0.0, sway, forward_back, 1.0)
            self.rotate_bone("Chest", 0.0, sway * 0.5, forward_back * 0.3, 1.0)

            # SHOULDERS
            shoulder_wave = math.sin(t * 1.2) * 0.08
            self.rotate_bone("LeftShoulder",  shoulder_wave, 0.0, 0.0, 1.0)
            self.rotate_bone("RightShoulder", -shoulder_wave, 0.0, 0.0, 1.0)

            # HIP SHIFT
            hip_shift = math.sin(t * 0.6) * 0.1
            self.rotate_bone("Hips", 0.0, hip_shift, 0.0, 1.0)

            # HEAD FOLLOWTHROUGH
            head_sway = -sway * 0.6
            head_nod = -forward_back * 0.4
            self.rotate_bone("Head", head_nod, head_sway, 0.0, 1.0)

            sleep(0.04)
            t += 0.04


# --------------------------------------------------------
# TESTING
# --------------------------------------------------------
if __name__ == "__main__":
    vmc = VMCClient()

    print("\n=== Smooth Blink ===")
    vmc.smooth_blendshape("Blink", 0.0, 1.0, duration=0.25)
    vmc.smooth_blendshape("Blink", 1.0, 0.0, duration=0.25)

    print("\n=== Smooth Smile ===")
    vmc.smooth_blendshape("Smile", 0.0, 1.0, duration=0.4)
    vmc.smooth_blendshape("Smile", 1.0, 0.0, duration=0.4)

    print("\n=== Smooth Head Tilt ===")
    start_q = (0.0, 0.0, 0.0, 1.0)
    end_q = (0.0, 0.25, 0.0, 1.0)
    vmc.smooth_bone_rotation("Head", start_q, end_q, duration=0.5)
    vmc.smooth_bone_rotation("Head", end_q, start_q, duration=0.5)

    print("\n=== Idle Animation Test ===")
    vmc.idle_animation(duration=8)

    print("\n[DEBUG COMPLETE]")
