import serial
import struct
from abc import ABC, abstractclassmethod


class ServoDriver(ABC):
    @abstractclassmethod
    def drive(channel, value):
        "sets the position value of a servo specified by 'channel' and its position on the board"


# class SparkfunPiServoHat(ServoDriver):
#     def __init__(self):
#         from smbus2 import SMBus

#         self.bus = SMBus(1)
#         self.addr = 0x40
#         # Next, we want to enable the PWM chip and tell it to automatically increment
#         # addresses after a write (that lets us do single-operation multi-byte writes).
#         self.bus.write_byte_data(self.addr, 0, 0x20)
#         self.bus.write_byte_data(self.addr, 0xFE, 0x1E)

#         # set servo pulse start times to 0
#         for channel in range(16):
#             self.bus.write_word_data(0x06 + channel * 4, 0)

#     def drive(channel, value):
#         self.bus.write_word_data(0x08 + channel * 4, remap(value, (0, 255), (0, 4095)))


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
