from ..drive_system import DriveSystem
from .hexy.core import joint_properties
from .hexy.dancing import DancingHexapod
from .hexy.servo_driver import UartMiniSsc, MockServoDriver
from threading import Thread
from asyncio import get_event_loop


class HexapodDrive(DriveSystem, DancingHexapod):
    def __init__(self, simulated=False):
        DancingHexapod.__init__(
            self,
            MockServoDriver() if simulated else UartMiniSsc(),
            {
                "LFH": (0, 0, 255),
                "LFK": (1, 0, 255),
                "LFA": (2, 0, 255),
                "RFH": (3, 0, 255),
                "RFK": (4, 0, 255),
                "RFA": (5, 0, 255),
                "LMH": (6, 0, 255),
                "LMK": (7, 0, 255),
                "LMA": (8, 0, 255),
                "RMH": (9, 0, 255),
                "RMK": (10, 0, 255),
                "RMA": (11, 0, 255),
                "LBH": (12, 0, 255),
                "LBK": (13, 0, 255),
                "LBA": (14, 0, 255),
                "RBH": (15, 0, 255),
                "RBK": (16, 0, 255),
                "RBA": (17, 0, 255),
                "N": (18, 0, 255),
            },
        )
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
            self.state_task.cancel()
            self.begin_state(desired_state)
