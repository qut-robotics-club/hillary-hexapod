from sanic import Blueprint, Sanic, response
from sanic_cors import CORS
from pathlib import Path
from threading import Thread
import subprocess
import os
import sys
import io
import logging
import socketserver
from threading import Condition
from http import server
from sanic.websocket import WebSocketProtocol
import json
from inspect import cleandoc
import cv2
import asyncio
from ffmpy3 import FFmpeg
import string
import random
from concurrent.futures import TimeoutError
import select

try:
    from VisionSystem import ColorSpaces
except:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from VisionSystem import ColorSpaces


SERVER_BASE_DIR = Path(__file__).parents[0].absolute()
CLIENT_STATICS_DIR = SERVER_BASE_DIR / 'out'
SERVER_STATICS_DIR = SERVER_BASE_DIR / 'static'

app = Blueprint("ControlServer")


app.static('/', str(CLIENT_STATICS_DIR))

# helper


def relpath(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


@app.route('/')
async def index(req):
    return await response.file(CLIENT_STATICS_DIR / 'index.html')


class ControlServer(Sanic):

    def __init__(self, port, drive_system, kicker_system, video_stream=None, vision_system=None, autobuild=False):
        super().__init__()

        self.blueprint(app)
        self.add_route(self.live_stream_mjpg, '/live_stream.mjpg')
        self.add_websocket_route(self.live_stream_ws_x264, '/live_stream')
        self.add_websocket_route(self.remote_control, '/remote_control')
        CORS(self)
        self.port = port
        self.video_stream = video_stream
        self.vision_system = vision_system
        self.drive_system = drive_system
        self.kicker_system = kicker_system
        self.recording = False

        # eject the nextjs frontend to static files for serving
        if autobuild:
            prev_wd = os.getcwd()
            os.chdir(SERVER_BASE_DIR)
            subprocess.call("npm run export".split(" "))
            os.chdir(prev_wd)

    async def live_stream_ws_x264(self, req, ws):
        # implements a x264 livestream that works with the WSAvcPlayer used by the LiveStream component
        # I assume this is the thing in a x264 livestream that specifies the beginning of a new frame
        NALSeparator = b'\x00\x00\x00\x01'

        vid_width, vid_height = self.video_stream.resolution

        await ws.send(json.dumps({
            'action': 'initalize',
            'payload': {
                'width': vid_width,
                'height': vid_height,
                'stream_active': True
            }
        }))

        await ws.send(json.dumps({
            'action': 'stream_active',
            'payload': True
        }))

        # create linux-only named FIFO pipes (pipes that dont send an EOF) as live-input mechanism for ffmpeg subprocess
        jpeg_input_fifo_path = f'/tmp/{random_string(10)}.fifo'
        h264_output_fifo_path = f'/tmp/{random_string(11)}.fifo'
        os.mkfifo(jpeg_input_fifo_path)
        os.mkfifo(h264_output_fifo_path)

        jpeg_fd = os.open(jpeg_input_fifo_path, os.O_RDWR)
        h264_fd = os.open(h264_output_fifo_path, os.O_RDWR)

        with os.fdopen(jpeg_fd, 'wb') as input_mpeg_stream,\
                os.fdopen(h264_fd, 'rb', buffering=0) as output_h264_stream:

            notiv = select.poll()
            notiv.register(output_h264_stream, select.POLLIN)

            await FFmpeg(
                # executable="/home/cal/berryconda3/bin/ffmpeg",
                global_options=['-y'],
                inputs={
                    jpeg_input_fifo_path: '-f image2pipe -vcodec mjpeg'},
                outputs={
                    h264_output_fifo_path: f'-c:v h264 -f h264 -s:v {vid_width}x{vid_height} -movflags +faststart -profile:v baseline -level 3.0 -r 10 -vprofile baseline -b:v 500k -bufsize 600k -tune zerolatency -pix_fmt yuv420p'}
            ).run_async()

            buffer = b''

            for frame in self.video_stream:
                bgr = frame.get(ColorSpaces.BGR)
                jpeg = cv2.imencode('.jpg', bgr)[1].tobytes()

                input_mpeg_stream.write(jpeg)

                any_frame = notiv.poll(0)
                if any_frame:
                    while(notiv.poll(0)):
                        buffer += output_h264_stream.read(1)
                        if len(buffer) > len(NALSeparator) and NALSeparator in buffer[-4:]:
                            await ws.send(buffer[:-4])
                            buffer = buffer[-4:]

                await asyncio.sleep(0)

    async def live_stream_mjpg(self, req):
        async def stream(res):
            for frame in self.video_stream:
                bgr = frame.get(ColorSpaces.BGR)
                jpeg = cv2.imencode('.jpg', bgr)[1].tostring()
                packet = cleandoc(f"""\
                --frame\r
                Content-Type: image/jpeg\r
                Content-Length: {len(jpeg)}\r
                \r
                """).encode('utf8')
                packet += jpeg + b"\r\n"
                await res.write(packet)

        return response.stream(
            stream,
            headers={
                'Age': 0,
                'Cache-Control': 'no-cache, private',
                'Pragma': 'no-cache',
                'Content-Type': 'multipart/x-mixed-replace; boundary=frame',
            }
        )

    async def remote_control(self, req, ws):
        global doing_frame
        # loop = asyncio.get_event_loop()

        doing_frame = False

        # def on_new_frame(frame):
        # pass
        # global doing_frame

        # if not doing_frame:
        #     doing_frame = True
        #     self.vision_system.update_with_frame(frame)
        #     msg = {
        #         name: [(det_result.coords, *bearings_distance) for det_result,
        #                bearings_distance in zip(det_results, bearings_distances)]
        #         for name, (det_results, bearings_distances) in self.vision_system.current_results.items()
        #     }
        #     loop.create_task(ws.send(json.dumps(msg)))
        #     doing_frame = False

        # self.video_stream.new_frame_cbs.append(on_new_frame)

        try:
            while True:
                cmd_json = await ws.recv()
                cmd = json.loads(cmd_json)
                if cmd['act'] == 'drive':
                    self.drive_system.set_desired_motion(
                        cmd['x'], cmd['y'], cmd['omega'] / 3)
                elif cmd['act'] == 'kick':
                    if self.kicker_system.is_kicking:
                        self.kicker_system.stop_kicking()
                    else:
                        self.kicker_system.start_kicking()
                elif cmd['act'] == 'dribble':
                    if cmd['enable']:
                        self.kicker_system.start_dribbling()
                    else:
                        self.kicker_system.stop_dribbling()
                elif cmd['act'] == 'set_recording':
                    self.set_recording(cmd['recording'])
                else:
                    print('unknown command recieved', cmd)

        except:
            self.recording = False
            pass
            # self.video_stream.new_frame_cbs.remove(on_new_frame)

    def set_recording(self, recording):
        RECORDINGS_DIR = './data/recordings'
        try:
            os.makedirs(RECORDINGS_DIR)
        except:
            pass

        dset_idx = 0

        if recording and not self.recording:
            filepath = f'{RECORDINGS_DIR}/{dset_idx}.mp4'
            while(os.path.exists(filepath)):
                dset_idx += 1
                filepath = f'{RECORDINGS_DIR}/{dset_idx}.mp4'

            Thread(target=self.record, args=[filepath]).start()

        self.recording = recording

    def record(self, filepath):
        jpeg_input_fifo_path = f'/tmp/{random_string(10)}.fifo'
        os.mkfifo(jpeg_input_fifo_path)
        jpeg_fd = os.open(jpeg_input_fifo_path, os.O_RDWR)
        vid_width, vid_height = self.video_stream.resolution

        # once this file is closed by this process (at the end of the with block)
        # the ffmpeg process will stop
        with os.fdopen(jpeg_fd, 'wb') as input_mpeg_stream:
            # run ffmpeg until we close the fifo
            ffmpeg = subprocess.Popen(FFmpeg(
                # executable="/home/cal/berryconda3/bin/ffmpeg",
                global_options=['-y'],
                inputs={
                    jpeg_input_fifo_path: '-f image2pipe -vcodec mjpeg'},
                outputs={
                    filepath: f'-c:v h264 -f mp4 -s:v {vid_width + vid_width % 2}x{vid_height + vid_height % 2}'}
            ).cmd, shell=True)

            for frame in self.video_stream:
                if not self.recording:
                    break
                bgr = frame.get(ColorSpaces.BGR)
                jpeg = cv2.imencode('.jpg', bgr)[1].tobytes()

                input_mpeg_stream.write(jpeg)

            ffmpeg.kill()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs, host='0.0.0.0', port=self.port)


def random_string(length): return ''.join(
    random.choice(string.ascii_lowercase) for _ in range(length))


if __name__ == "__main__":

    # from VisionSystem.DetectionModel import ThreshBlob
    # from VisionSystem import VideoStream, VisionSystem, VisualObject

    # use any available live feed device such as a webcam
    #     video_stream = VideoStream(downsample_scale=8, crop=((0.13, 0), (.9, 1)))

    #     objects_to_size_and_result_limit = {
    #         "ball": ((0.043, 0.043, 0.043), 1),
    #         "obstacle": ((0.18, 0.18, 0.2), None),
    #         # 30 centimetres long, 10 cm high? i guess
    #         # "blue_goal": ((0.3, 0.3, 0.1), 1),
    #         # "yellow_goal": ((0.3, 0.3, 0.1), 1)
    #     }

    #     vision_system = VisionSystem(resolution=video_stream.resolution, objects_to_track={
    #         name: VisualObject(
    #             real_size=size,
    #             detection_model=ThreshBlob.load(
    #                 relpath("..", "models", f"{name}.threshblob.pkl")),
    #             result_limit=result_limit
    #         ) for name, (size, result_limit) in objects_to_size_and_result_limit.items()
    #     })

    try:
        from drive_system import DriveSystem
        drive_system = DriveSystem()

    except ModuleNotFoundError:
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
