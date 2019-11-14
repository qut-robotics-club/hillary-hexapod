"""
This file is wrong on so many levels.., just... kill me
"""


import RPi.GPIO
from RPi.GPIO import OUT, IN
from gpiozero import PWMOutputDevice, LED, Button, GPIODevice as GPIOZDev, OutputDevice
from inspect import getframeinfo, stack
import atexit
from abc import ABC
import os


def dynamic_config(func):
    def inner(self, *args, **kwargs):
        global devices, config

        # copy the list so that we don't use the same reference
        before = config.copy()
        func(self, *args, **kwargs)

        print('before', before)
        print('after', config)

        # define the dynamic config based on what pins have been added
        self.dynamic_config = {k: config[k] for k in set(config) - set(before)}
    return inner


class GPIODevice(ABC):

    # static config
    config = {}

    # dynamic configs can be done by calling GPIO.setup() within a GPIODevice method
    # decorated with the @GPIO.dynamic_config decorator (typically in __init__)

    def setup(self):
        devices[self] = []

        if not hasattr(self, 'dynamic_config'):
            self.dynamic_config = {}

        if len(self.config) == 0 and len(self.dynamic_config) == 0:
            raise NotImplementedError(
                "GPIO Device object has an empty config (both static and dynamic)")

        for pin, cfg in {**self.config, **self.dynamic_config}.items():
            if isinstance(cfg, GPIODevice):
                cfg.setup()
            elif isinstance(cfg, int):  # direction type
                setup(pin, cfg)
                devices[self].append((pin, cfg))
            elif isinstance(cfg, GPIOZDev):
                setup(pin, isinstance(cfg, OutputDevice))
                devices[self].append((pin, cfg))
            else:
                raise Exception(f"config variable of type {type(cfg)}: {cfg}")


def setmode(cls):
    raise NotImplementedError("Only use BCM Mode Pin Numbering")


# for GPIO -related errors; just extend the standard Exception but let people know it came from this module
class Error(Exception):
    pass


# this is our static global config variable. it'll help make sure
# we don't step on eachothers' toes.
config = {}


# keep track of the mapping between devices and the pins they actually end up using.
# this way devices can clean up their pins automagically with a device.cleanup() function.
# with this you can have two devices plugged into the same pins with one being deactivated
devices = {}


class PWM(RPi.GPIO.PWM, GPIODevice):

    def __init__(self, pin, frequency=1, dutycycle=0):
        assert frequency > 0
        self.pin = pin
        self.frequency = frequency
        self.dutycycle = dutycycle

        self.pwm = PWMOutputDevice(self.pin, initial_value=True)
        self.ChangeDutyCycle(dutycycle)
        self.ChangeFrequency(frequency)

    def ChangeDutyCycle(self, dutycycle):
        assert 0 <= dutycycle and dutycycle <= 100
        self.dutycycle = dutycycle
        self.pwm.value = self.dutycycle / 100

    def ChangeFrequency(self, frequency):
        self.frequency = frequency
        self.pwm.frequency = frequency

    def start(self, dutycycle):
        self.ChangeDutyCycle(dutycycle)

    def stop(self):
        self.ChangeDutyCycle(0)

    def cleanup(self):
        super().cleanup()
        self.pwm.off()


def setup(pin, direction):
    global config

    if pin in config:
        raise Error(
            f"pin {pin} already in use. (check its declaration at {config[pin][0]})")

    device = LED(pin) if direction == OUT else Button(pin)

    caller = getframeinfo(stack()[1][0])

    config[pin] = (
        f"{os.path.abspath(caller.filename)}, line {caller.lineno}",
        device
    )


def _handle_misuse(ExpectedDevice):
    def wrapper(read_or_write_func):
        def result(pin, state=None):
            global config
            if pin not in config:
                raise Error(f"pin {pin} has not yet been setup()'d")
            declaration, device = config[pin]
            if not isinstance(device, ExpectedDevice):
                raise Error(f"""\
                    pin {pin} is attempting to output but has not been setup()'d with direction=OUTPUT. \
                    Expected {ExpectedDevice}, got {device}. Refer to declaration: {declaration}""")
            read_or_write_func(pin, state)

        return result
    return wrapper


@_handle_misuse(ExpectedDevice=LED)
def output(pin, state):
    _, led = config[pin]
    assert isinstance(led, LED)
    if state:
        led.on()
    else:
        led.off()


@_handle_misuse(ExpectedDevice=Button)
def input(pin, state=None):
    _, button = config[pin]
    assert isinstance(button, Button)
    return button.is_held
