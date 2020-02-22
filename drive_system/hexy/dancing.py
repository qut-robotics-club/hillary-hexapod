from .pro import HexapodPro
from asyncio import sleep, gather


class DancingHexapod(HexapodPro):
    async def prepare(
        self, offset=45, back_knee=0, middle_knee=50, front_knee=60, raised=-30, t=0.2
    ):
        """ brings the back legs even further to the back and the middle legs to the front
            and then brings his further to the front """

        await gather(
            self.left_back.replant(raised, back_knee, offset, t),
            self.right_back.replant(raised, back_knee, -offset, t),
            self.left_middle.replant(raised, middle_knee, -offset, t),
            self.right_middle.replant(raised, middle_knee, offset, t),
            self.left_front.replant(raised, front_knee, -offset, t),
            self.right_front.replant(raised, front_knee, offset, t),
        )

        await sleep(t)

    async def wave_right_arm_up(self):
        await gather(
            self.right_front.knee.pose(-60),
            self.right_front.ankle.pose(0),
            self.right_front.hip.pose(-45),
        )

    async def wave_right_arm_down(self):
        await gather(
            self.right_front.knee.pose(50),
            self.right_front.ankle.pose(-50),
            self.right_front.hip.pose(45),
        )

    async def dip_body(self, mid=50, back=0):
        await gather(
            self.left_middle.move(knee_angle=mid),
            self.right_middle.move(knee_angle=mid),
            self.left_back.move(knee_angle=-back),
            self.right_back.move(knee_angle=-back),
        )

    async def raise_body(self, mid=70, back=20):
        await gather(
            self.left_middle.move(knee_angle=mid),
            self.right_middle.move(knee_angle=mid),
            self.left_back.move(knee_angle=back),
            self.right_back.move(knee_angle=back),
        )

    async def night_fever(self):

        await self.prepare()

        for _ in range(4):
            await self.wave_right_arm_up()
            await self.left_front.move(knee_angle=40)
            await self.dip_body()
            await sleep(0.4)
            await self.wave_right_arm_down()
            await self.left_front.move(knee_angle=60)
            await self.raise_body()
            await sleep(0.4)

    async def arms_up_left(self):
        await gather(
            self.right_front.pose(knee_angle=-60, ankle_angle=-80, hip_angle=-45),
            self.left_front.pose(knee_angle=-60, ankle_angle=-80, hip_angle=-45),
        )

    async def arms_up_right(self):
        await gather(
            self.right_front.pose(knee_angle=-60, ankle_angle=-80, hip_angle=45),
            self.left_front.pose(knee_angle=-60, ankle_angle=-80, hip_angle=45),
        )

    async def arms_down_center(self):
        await gather(
            self.right_front.pose(knee_angle=30, ankle_angle=-60, hip_angle=0),
            self.left_front.pose(knee_angle=30, ankle_angle=-60, hip_angle=0),
        )

    async def thriller_routine0(self):
        await gather(self.arms_down_center(), self.raise_body())
        await sleep(0.3)

    async def thriller_routine1(self):
        await self.thriller_routine0()
        await gather(self.arms_up_left(), self.dip_body())
        await sleep(0.3)

    async def thriller_routine2(self):
        await self.thriller_routine0()
        await gather(self.arms_up_right(), self.dip_body())
        await sleep(0.3)

    async def thriller(self):

        await self.prepare()

        for _ in range(3):
            await self.thriller_routine1()
            await self.thriller_routine2()
