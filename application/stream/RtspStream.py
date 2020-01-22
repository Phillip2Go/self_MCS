#!/usr/bin/env python3
import time
from multiprocessing import Process
from threading import Thread
import subprocess
import gi

import resources.settings

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib


# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, camerakey, **properties):
        super(SensorFactory, self).__init__(**properties)
        self.source = camerakey if camerakey else 0
        self.number_frames = 0
        self.fps = 25
        self.set_shared(True)
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width=1920,height=1080,framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=YV12 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96'.format(self.fps)

    def on_need_data(self, src, length):
        try:
            ret, frame = resources.settings.rootFrameDict[self.source]
            if ret:
                data = frame.tostring()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.number_frames * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.number_frames += 1
                retval = src.emit('push-buffer', buf)
                print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames, self.duration, self.duration / Gst.SECOND))
                if retval != Gst.FlowReturn.OK:
                    print(retval)
        except TypeError as te:
            pass

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)


# class SessionPool(GstRtspServer.RTSPSessionPool):
#     def __init__(self, **properties):
#         super(SessionPool, self).__init__(**properties)
#         self.set_max_sessions(0)


class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, camerakey=None, name="stream", port=8554, **properties):
        super(GstServer, self).__init__(**properties)

        # self.get_thread_pool().set_max_threads(10)
        # self.set_backlog(10)
        self.factory = SensorFactory(camerakey=camerakey)
        self.set_service(str(port))
        self.get_mount_points().add_factory("/" + name, self.factory)
        self.attach(None)


class RtspStreamer(Thread):
    def __init__(self, camerakey, name, port):
        super().__init__()
        Gst.init(None)
        self.name = name
        self.port = port
        self.camerakey = camerakey

    def run(self):
        server = GstServer(self.camerakey, self.name, self.port)
        print("--- Restream for {} initialized ({}:{}) ---".format(self.camerakey, self.port, self.name))
        loop = GLib.MainLoop()
        loop.run()
