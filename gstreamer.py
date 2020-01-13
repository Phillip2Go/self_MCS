#!/usr/bin/env python3

import cv2
import gi
from threading import Thread

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib


class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(SensorFactory, self).__init__(**properties)
        #######################
        # SET RTSP STREAM URL #
        #######################
        self.cap = cv2.VideoCapture('rtsp://192.168.0.11:554/MediaInput/h264/stream_1')
        # self.cap = cv2.VideoCapture(0)
        print("cap.isOpened() Status:", self.cap.isOpened())
        self.number_frames = 0
        self.fps = 25
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width=1920,height=1080,framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420' \
                             '! x264enc speed-preset=3 tune=zerolatency ' \
                             '! rtph264pay config-interval=0 name=pay0 pt=96'.format(self.fps)

    def on_need_data(self, src, lenght):
        # print("In def: on_need_data")
        if self.cap.isOpened():
            ret, frame = self.cap.read()
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
                print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
                                                                                       self.duration,
                                                                                       self.duration / Gst.SECOND))
                if retval != Gst.FlowReturn.OK:
                    print(retval)

    def do_create_element(self, url):
        print("In def: do_create_element")
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        print("In def: do_configure")
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)


class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, **properties):
        super(GstServer, self).__init__(**properties)

        ###############
        # SET ADDRESS #
        ###############
        self.set_address('192.168.0.248')

        ##########
        # SET IP #
        ##########
        self.set_service("8554")

        self.factory = SensorFactory()
        self.factory.set_shared(True)
        self.get_mount_points().add_factory("/open1", self.factory)
        self.attach(None)


if __name__ == '__main__':
    # GObject.threads_init()
    Gst.init(None)

    cs = Thread(target=GstServer, args=())
    cs.start()

    server = GstServer()

    loop = GLib.MainLoop()
    loop.run()
