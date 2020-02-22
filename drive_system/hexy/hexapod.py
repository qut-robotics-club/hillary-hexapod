from .core import HexapodCore
from asyncio import sleep, gather


class Hexapod(HexapodCore):
    async def boot_up(self):

        await self.lie_down()
        await self.curl_up()
        await self.lie_flat()
        await self.get_up()

    async def shut_down(self):

        await self.lie_down()
        await self.lie_flat()
        await self.curl_up(die=True)

    async def curl_up(self, die=False, t=0.2):

        await gather(
            *[
                leg.pose(
                    hip_angle=0,
                    knee_angle=-(leg.knee.max + leg.knee.leeway),
                    ankle_angle=leg.ankle.max,
                )
                for leg in self.legs
            ]
        )

        await sleep(t)

        if die:
            self.off()

    async def lie_flat(self, t=0.15):

        await gather(*[leg.pose() for leg in self.legs])
        await sleep(t)

    async def lie_down(self, maxx=50, step=4, t=0.15):

        for angle in range(maxx, -(maxx + 1), -step):
            await self.squat(angle)

        await sleep(t)

    async def get_up(self, maxx=70, step=4):
        for angle in range(-maxx, maxx + 1, step):
            await self.squat(angle)

        await self.default()

    async def twist_hip(self, angle=0, t=0.1):
        await gather(*[hip.pose(angle) for hip in self.hips])
        await sleep(t)

    async def squat(self, angle, t=0):
        await gather(*[leg.move(knee_angle=angle) for leg in self.legs])
        await sleep(t)

    async def walk(
        self, offset=25, swing=25, raised=-30, floor=50, repetitions=4, t=0.2
    ):
        """ if swing > 0, hexy moves forward else backward """

        swings = [offset - swing, swing, -(offset + swing)]
        reverse_swings = [-x for x in swings]

        for _ in range(repetitions):
            await self.stride(self.tripod1, self.tripod2, swings, raised, floor, t)
            await self.stride(
                self.tripod2, self.tripod1, reverse_swings, raised, floor, t
            )

    async def rotate(self, offset=40, raised=-30, floor=50, repetitions=5, t=0.2):
        """ if offset > 0, hexy rotates left, else right """

        for _ in range(repetitions):

            # replant tripod2 with an offset
            await self.uniform_move(self.tripod2, None, raised, t)
            await self.uniform_move(self.tripod2, offset, floor, t)

            # raise tripod1
            await self.uniform_move(self.tripod1, -offset, raised)

            # swing tripod2's hips to an -offset
            await self.uniform_move(self.tripod2, -offset, None, t)

            # lower tripod1
            await self.uniform_move(self.tripod1, 0, floor, t)

    async def stride(self, first_tripod, second_tripod, swing, raised, floor, t):
        """ first_tripod's legs replant to propel towards a direction while
            second_tripod's legs retrack by swinging to the opposite direction """

        await self.simultaneous_move(first_tripod, knee_angle=raised)
        await sleep(t)

        await self.simultaneous_move(second_tripod, swing[::-1])
        await self.simultaneous_move(first_tripod, swing, floor)
        await sleep(t)

    async def tilt_side(self, left_angle=50, right_angle=0, t=0.2):
        """ if left_angle > right_angle, left side is higher than right side """

        await self.uniform_move(legs=self.left_legs, knee_angle=left_angle)
        await self.uniform_move(legs=self.right_legs, knee_angle=right_angle)
        await sleep(t)

    async def tilt(self, front_angle=50, middle_angle=25, back_angle=0, t=0.2):
        """ if front_angle > middle_angle > back_angle hexy's front is higher than his back """

        await gather(
            self.right_front.move(knee_angle=front_angle),
            self.left_front.move(knee_angle=front_angle),
            self.right_middle.move(knee_angle=middle_angle),
            self.left_middle.move(knee_angle=middle_angle),
            self.right_back.move(knee_angle=back_angle),
            self.left_back.move(knee_angle=back_angle),
        )

        await sleep(t)

    async def default(self, offset=45, floor=60, raised=-30, t=0.2):
        """ Hexy's default pose, offset > 0 brings the front and back legs to the side """

        swings = [offset, 0, -offset]

        await self.squat(floor, t)

        await self.simultaneous_move(self.tripod1, swings, raised, t)
        await self.simultaneous_move(self.tripod1, swings, floor, t)
        await self.simultaneous_move(self.tripod2, swings[::-1], raised, t)
        await self.simultaneous_move(self.tripod2, swings[::-1], floor, t)

    async def uniform_move(self, legs, hip_angle=None, knee_angle=None, t=0):
        """ moves all legs with hip_angle, knee_angle """

        await gather(*[leg.move(knee_angle, hip_angle) for leg in legs])
        await sleep(t)

    async def simultaneous_move(
        self, legs, swings=[None, None, None], knee_angle=None, t=0
    ):
        """ moves all legs with knee_angle to the respective hip angles at 'swing' """

        await gather(
            *[leg.move(knee_angle, hip_angle) for leg, hip_angle in zip(legs, swings)]
        )

        await sleep(t)
