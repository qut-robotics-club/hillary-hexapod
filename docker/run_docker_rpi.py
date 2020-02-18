from subprocess import check_call
from pathlib import Path
from sys import platform

THIS_DIR = Path(__file__).parent.absolute()

PLATFORM = "linux/arm/v7"

if __name__ == "__main__":
    # unix systems require bin_fmt from qemu in order to emulate other architectures
    # in windows only (for some reason, as of 19/02/2020), this functionality is provided with docker desktop
    if platform != "windows":
        check_call(
            "docker run --rm --privileged docker/binfmt:a7996909642ee92942dcd6cff44b9b95f08dad64".split()
        )

    check_call(
        (f"docker build {THIS_DIR} --platform {PLATFORM} -t hyper-controller").split()
    )
    check_call(
        (
            f"docker run -v {THIS_DIR.parent}:/home/pi/workspace/hyper-controller --platform {PLATFORM} hyper-controller"
        ).split()
    )
