from time import sleep
from ..drive_system import DriveSystem
from .hexy.core import joint_properties
from .hexy.hexapod import Hexapod
from .hexy.servo_driver import UartMiniSsc


class HexapodDrive(DriveSystem, Hexapod):
    def __init__(self):
        Hexapod.__init__(self, UartMiniSsc(), {
            'LFH': (0, 0, 255), 'LFK': (1, 0, 255), 'LFA': (2, 0, 255),
            'RFH': (3, 0, 255), 'RFK': (4, 0, 255), 'RFA': (5, 0, 255),
            'LMH': (6, 0, 255), 'LMK': (7, 0, 255), 'LMA': (8, 0, 255),
            'RMH': (9, 0, 255), 'RMK': (10, 0, 255), 'RMA': (11, 0, 255),
            'LBH': (12, 0, 255), 'LBK': (13, 0, 255), 'LBA': (14, 0, 255),
            'RBH': (15, 0, 255), 'RBK': (16, 0, 255), 'RBA': (17, 0, 255),
            'N': (18, 0, 255)
        })

    def set_desired_motion(self, _x, y, omega):
        # TODO: use nice remap() function included in ./hexy/core instead of random rescalers
        if y != 0:
            self.walk(swing=10 * y)
        else:
            self.rotate(offset=-10 * omega)

        # TODO: add calibration routines to the hypercontroller
        # def calibrate_joint(joint, t, mn, mx, z):

        #     while True:
        #         for angle in [mn, z, mx, z]:
        #             joint.pose(angle)
        #             sleep(t)

        # hexy = HexapodCore()
        # calibrate_joint(hexy.right_back.knee, t=2, mn=-45, mx=45, z=0)
        # # hexy.off()
