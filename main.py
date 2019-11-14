from control_server import ControlServer

if __name__ == "__main__":
    # not on the raspberry pi, just mock it
    def drive_system():
        pass

    drive_system.set_desired_motion = lambda x, y, omega: print(
        'mock drive', x, y, omega)

    def kicker_system():
        pass

    kicker_system.start_kicking = lambda: None
    kicker_system.stop_kicking = lambda: None
    kicker_system.is_kicking = False

    ControlServer(
        port=8000,
        drive_system=drive_system,
        kicker_system=kicker_system,
        autobuild=True
    ).run()
