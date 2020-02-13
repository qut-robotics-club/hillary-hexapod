import serial
import struct
from abc import ABC, abstractclassmethod


class ServoDriver(ABC):
    @abstractclassmethod
    def drive(channel, value):
        "sets the position value of a servo specified by 'channel' and its position on the board"


class UartMiniSsc(ServoDriver):

    # raspberry pi 3+ and zero w
    RASPI_WITH_INBUILT_WIFI_GPIO_SERIAL_DEV = "/dev/ttyS0"
    # all other raspberry Pi's
    RASPI_NO_INBUILT_WIFI_GPIO_SERIAL_DEV = "/dev/ttyACM0"

    def __init__(self, serial_device=RASPI_WITH_INBUILT_WIFI_GPIO_SERIAL_DEV):
        # no need to specify baud rate as the mini-maestro supports autodetect
        self.serial = serial.Serial(serial_device, baudrate=115200)

    def drive(self, channel, value):
        "MiniSSC protocol"
        SET_SERVO_POS_CMD_BYTE = b"\xFF"
        drive_servo_cmd = struct.pack("cBB", SET_SERVO_POS_CMD_BYTE, channel, value)
        self.serial.write(drive_servo_cmd)

    def __del__(self):
        self.serial.close()


class MockServoDriver(ServoDriver):
    def drive(self, channel, value):
        pass


class AdafruitPCA9685(ServoDriver):
    pass
