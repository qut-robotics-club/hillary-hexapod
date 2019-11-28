from hyper_controller.drive_system.hexapod import HexapodDrive

if __name__ == "__main__":
    hexy = HexapodDrive()
    hexy.boot_up()
