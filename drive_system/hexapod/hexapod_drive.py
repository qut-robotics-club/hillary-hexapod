from ..drive_system import DriveSystem
from .hexy.dancing import DancingHexapod
from .hexy.servo_driver import UartMiniSsc, MockServoDriver
from threading import Thread
from asyncio import get_event_loop
import json
from pathlib import Path
import pickle

CALIBRATION_FILEPATH = (
    Path(__file__).parent.parent.parent / "data" / "hillary_calibration.pkl"
)


class HexapodDrive(DriveSystem, DancingHexapod):
    def __init__(self, simulated=False):
        try:
            with open(CALIBRATION_FILEPATH, "rb") as f:
                joint_properties = pickle.load(f)
        except FileNotFoundError:
            joint_properties = {  # default
                "LFH": (0, 0, 255, False),
                "LFK": (1, 0, 255, True),
                "LFA": (2, 0, 255, True),
                "RFH": (3, 0, 255, False),
                "RFK": (4, 0, 255, True),
                "RFA": (5, 0, 255, True),
                "LMH": (6, 0, 255, False),
                "LMK": (7, 0, 255, True),
                "LMA": (8, 0, 255, True),
                "RMH": (9, 0, 255, False),
                "RMK": (10, 0, 255, True),
                "RMA": (11, 0, 255, True),
                "LBH": (12, 0, 255, False),
                "LBK": (13, 0, 255, True),
                "LBA": (14, 0, 255, True),
                "RBH": (15, 0, 255, False),
                "RBK": (16, 0, 255, True),
                "RBA": (17, 0, 255, True),
            }

        DancingHexapod.__init__(
            self, MockServoDriver() if simulated else UartMiniSsc(), joint_properties
        )
        self.joints = [joint for leg in self.legs for joint in leg.joints]
        self.begin_state("stand")

    def begin_state(self, state):
        self.state = state
        self.state_task = get_event_loop().create_task(
            self.squat(40)
            if state is "stand"
            else self.walk()
            if state is "walk_forward"
            else self.walk(swing=-25)
            if state is "walk_backward"
            else self.rotate(offset=40)
            if state is "rotate_clockwise"
            else self.rotate(offset=-40)
            if state is "rotate_anti-clockwise"
            else None
        )

    async def calibrate(self, joint_name, pulse, is_min_pulse, is_reversed):
        if self.state == "calibration":
            joint = next(joint for joint in self.joints if joint_name == joint.name)
            props = self.joint_properties[joint_name]
            self.joint_properties[joint_name] = (
                props[0],
                pulse if is_min_pulse else props[1],
                pulse if not is_min_pulse else props[2],
                is_reversed,
            )

            joint.is_reversed = is_reversed

            if is_min_pulse:
                joint.min_pulse = pulse
            else:
                joint.max_pulse = pulse

            await joint.pose(-joint.max if is_min_pulse != is_reversed else joint.max)

        with open(CALIBRATION_FILEPATH, "wb") as calibration_file:
            pickle.dump(self.joint_properties, calibration_file)

    def set_desired_motion(self, _x, y, omega):
        desired_state = (
            "stand"
            if y == 0 and omega == 0
            else "walk_forward"
            if y > 0
            else "walk_backward"
            if y < 0
            else "rotate_clockwise"
            if omega > 0
            else "rotate_anti-clockwise"
            if omega < 0
            else None
        )

        if self.state != desired_state:
            if self.state_task is not None:
                self.state_task.cancel()
            self.begin_state(desired_state)
