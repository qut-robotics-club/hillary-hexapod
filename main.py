from hyper_controller.drive_system.hexapod import HexapodDrive
from hyper_controller.control_server import ControlServer

if __name__ == "__main__":
    def kicker_system():
        pass

    kicker_system.start_kicking = lambda: None
    kicker_system.stop_kicking = lambda: None
    kicker_system.is_kicking = False

    ControlServer(
        port=8000,
        drive_system=HexapodDrive(),
        kicker_system=kicker_system,
        autobuild=False
    ).run()
