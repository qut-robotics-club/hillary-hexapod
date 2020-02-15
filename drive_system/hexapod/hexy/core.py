import json
import asyncio
from asyncio import sleep
from math import pi

""" joint_key convention:
    R - right, L - left
    F - front, M - middle, B - back
    H - hip, K - knee, A - Ankle
    key : (channel, minimum_pulse_length[0-254], maximum_pulse_length[0-254]) """

joint_properties = {
    "LFH": (0, 248, 398),
    "LFK": (1, 188, 476),
    "LFA": (2, 131, 600),
    "RFH": (3, 275, 425),
    "RFK": (4, 227, 507),
    "RFA": (5, 160, 625),
    "LMH": (6, 312, 457),
    "LMK": (7, 251, 531),
    "LMA": (8, 138, 598),
    "RMH": (9, 240, 390),
    "RMK": (10, 230, 514),
    "RMA": (11, 150, 620),
    "LBH": (12, 315, 465),
    "LBK": (13, 166, 466),
    "LBA": (14, 140, 620),
    "RBH": (15, 320, 480),
    "RBK": (16, 209, 499),
    "RBA": (17, 150, 676),
}


def joint_deg_to_crab_urdf_rad(joint_name, deg):

    crab_urdf_joint_name = (
        {"H": "coxa", "K": "femur", "A": "tibia"}[joint_name[2]]
        + "_joint_"
        + joint_name[0].lower()
        + {"F": "1", "M": "2", "B": "3"}[joint_name[1]]
    )

    crab_urdf_joint_rad = (
        (deg + {"H": 0, "K": -30, "A": 90}[joint_name[2]]) * pi / 180  # offset
    )

    return {crab_urdf_joint_name: crab_urdf_joint_rad}


class HexapodCore:
    def __init__(self, servo_driver, joint_properties):
        self.left_front = Leg(
            "left front", "LFH", "LFK", "LFA", servo_driver, joint_properties
        )
        self.right_front = Leg(
            "right front", "RFH", "RFK", "RFA", servo_driver, joint_properties
        )

        self.left_middle = Leg(
            "left middle", "LMH", "LMK", "LMA", servo_driver, joint_properties
        )
        self.right_middle = Leg(
            "right middle", "RMH", "RMK", "RMA", servo_driver, joint_properties
        )

        self.left_back = Leg(
            "left back", "LBH", "LBK", "LBA", servo_driver, joint_properties
        )
        self.right_back = Leg(
            "right back", "RBH", "RBK", "RBA", servo_driver, joint_properties
        )

        self.legs = [
            self.left_front,
            self.right_front,
            self.left_middle,
            self.right_middle,
            self.left_back,
            self.right_back,
        ]

        self.right_legs = [self.right_front, self.right_middle, self.right_back]
        self.left_legs = [self.left_front, self.left_middle, self.left_back]

        self.tripod1 = [self.left_front, self.right_middle, self.left_back]
        self.tripod2 = [self.right_front, self.left_middle, self.right_back]

        self.hips, self.knees, self.ankles = [], [], []

        for leg in self.legs:
            self.hips.append(leg.hip)
            self.knees.append(leg.knee)
            self.ankles.append(leg.ankle)

    def off(self):
        for leg in self.legs:
            leg.off()

    def link_ws(self, ws):
        for leg in self.legs:
            leg.link_ws(ws)


class Leg:
    def __init__(
        self,
        name,
        hip_key,
        knee_key,
        ankle_key,
        servo_driver,
        joint_properties,
        max_hip=45,
        max_knee=50,
        knee_leeway=10,
    ):

        self.hip = Joint("hip", hip_key, servo_driver, joint_properties, maxx=max_hip)
        self.knee = Joint(
            "knee",
            knee_key,
            servo_driver,
            joint_properties,
            maxx=max_knee,
            leeway=knee_leeway,
        )
        self.ankle = Joint("ankle", ankle_key, servo_driver, joint_properties)

        self.name = name
        self.joints = [self.hip, self.knee, self.ankle]

    def link_ws(self, ws):
        for joint in self.joints:
            joint.link_ws(ws)

    async def pose(self, hip_angle=0, knee_angle=0, ankle_angle=0):
        await asyncio.gather(
            self.hip.pose(hip_angle),
            self.knee.pose(knee_angle),
            self.ankle.pose(ankle_angle),
        )

    async def move(self, knee_angle=None, hip_angle=None, offset=100):
        """ knee_angle < 0 means thigh is raised, ankle's angle will be set to the specified 
            knee angle minus the offset. offset best between 80 and 110 """

        if knee_angle == None:
            knee_angle = self.knee.angle
        if hip_angle == None:
            hip_angle = self.hip.angle or 0

        await self.pose(hip_angle, knee_angle, knee_angle - offset)

    async def replant(self, raised, floor, offset, t=0.1):

        await self.move(raised)
        await sleep(t)

        await self.move(floor, offset)
        await sleep(t)

    def off(self):
        for joint in self.joints:
            joint.off()

    def __repr__(self):
        return "leg: " + self.name


class Joint:
    def __init__(
        self, joint_type, jkey, servo_driver, joint_properties, maxx=90, leeway=0
    ):
        self.servo_driver = servo_driver
        self.joint_type, self.name = joint_type, jkey
        self.channel, self.min_pulse, self.max_pulse = joint_properties[jkey]
        self.max, self.leeway = maxx, leeway
        self.ws = None
        self.angle = 0

    def link_ws(self, ws):
        self.ws = ws

    async def pose(self, angle=0):

        angle = constrain(angle, -(self.max + self.leeway), self.max + self.leeway)

        if self.ws is not None:
            # create_task so that we can kickstart the coroutine without needing await
            await self.ws.send(json.dumps(joint_deg_to_crab_urdf_rad(self.name, angle)))

        pulse = remap(angle, (-self.max, self.max), (self.min_pulse, self.max_pulse))

        self.servo_driver.drive(self.channel, pulse)
        self.angle = angle

        # print repr(self), ':', 'pulse', pulse

    def off(self):
        self.servo_driver.drive(self.channel, 0)
        self.angle = None

    def __repr__(self):
        return (
            "joint: "
            + self.joint_type
            + " : "
            + self.name
            + " angle: "
            + str(self.angle)
        )


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def remap(old_val, old, new):
    (old_min, old_max) = old
    (new_min, new_max) = new
    new_diff = (new_max - new_min) * (old_val - old_min) / float((old_max - old_min))
    return int(round(new_diff)) + new_min
