
from abc import ABC, abstractclassmethod


class DriveSystem(ABC):

    @abstractclassmethod
    def set_desired_motion(self, x, y, omega):
        pass
