from time import sleep
from ..drive_system import DriveSystem
from .hexy.hexapod import Hexapod


class HexapodDrive(DriveSystem, Hexapod):

    def __init__(self):
        self.boot_up()

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
