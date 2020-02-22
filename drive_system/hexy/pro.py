from .hexapod import Hexapod
from asyncio import sleep, gather


class HexapodPro(Hexapod):
    async def point(self, t=0.75):
        await gather(
            self.left_front.hip.pose(-45),
            self.left_front.knee.pose(-50),
            self.left_front.ankle.pose(-55),
        )

        await sleep(t)

    async def wave(self, repetitions=5, t=0.2):

        await gather(self.left_front.ankle.pose(), self.left_front.knee.pose(-50))

        for _ in range(repetitions):
            await self.left_front.hip.pose(-45)
            await sleep(t)
            await self.left_front.hip.pose(45)
            await sleep(t)

    async def dance_twist(self, maxx=45, step=5, repetitions=3, t=0.01):

        await self.squat(60, t)

        for _ in range(repetitions):

            for angle in range(-maxx, maxx, step):
                await self.twist_hip(angle, t)

            for angle in range(maxx, -maxx, -step):
                await self.twist_hip(angle, t)

        await self.twist_hip()
        await self.squat(60, t)

    async def lean_back(
        self, offset=45, back_knee=0, middle_knee=40, raised=-30, t=0.2
    ):
        """ brings the back legs even further to the back and the middle legs to the front
            and then brings his front legs up in the air """

        await self.left_back.replant(raised, back_knee, offset, t)
        await self.right_back.replant(raised, back_knee, -offset, t)
        await self.left_middle.replant(raised, middle_knee, -offset, t)
        await self.right_middle.replant(raised, middle_knee, offset, t)

        await self.left_front.pose(-offset, 0, 0)
        await self.right_front.pose(offset, 0, 0)

        await sleep(t)

    async def type_stuff(self, up=-40, down=40, repetitions=5, t=0.2):

        await self.lean_back()

        for _ in range(repetitions):

            await self.left_front.knee.pose(up)
            await self.right_front.knee.pose(down)
            await sleep(t)

            await self.right_front.knee.pose(up)
            await self.left_front.knee.pose(down)
            await sleep(t)

    async def tilt_left_and_right(self, raised=60, floor=20, repetitions=5, t=0.15):

        for _ in range(repetitions):
            await self.tilt_side(left_angle=floor, right_angle=raised)
            await self.tilt_side(left_angle=raised, right_angle=floor)

        await self.squat(raised, t)

    async def tilt_front_and_back(self, up=60, mid=40, down=20, repetitions=5, t=0.15):

        for _ in range(repetitions):
            await self.tilt(up, mid, down)
            await self.tilt(down, mid, up)

        await self.squat(up, t)

    async def dance_tilt(self, raised=60, mid=40, floor=20, repetitions=3, t=0.15):

        for _ in range(repetitions):

            await self.tilt(floor, mid, raised, t)  # front
            await self.tilt_side(raised, floor, t)  # right
            await self.tilt(raised, mid, floor, t)  # back
            await self.tilt_side(floor, raised, t)  # left

        await self.squat(raised, t)

    async def rock_body(self, offset=45, floor=50, repetitions=7):

        for _ in range(repetitions):
            await self.uniform_move(self.left_legs, offset, floor, 0)
            await self.uniform_move(self.right_legs, -offset, floor, 0.2)
            await self.uniform_move(self.left_legs, -offset, floor, 0)
            await self.uniform_move(self.right_legs, offset, floor, 0.2)
