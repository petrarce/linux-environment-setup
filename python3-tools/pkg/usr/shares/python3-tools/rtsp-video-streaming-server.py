#!/usr/bin/env python3
import argparse
import gi
import sys
import os

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class VideoStreamServer:
    def __init__(self, args):
        self.args = args
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()
        
    def build_pipeline(self):
        if self.args.command == 'file':
            if not os.path.isfile(self.args.file):
                sys.exit(f"Error: File {self.args.file} not found")
                
            return f'( filesrc location={self.args.file} ! clockoverlay time-format="%Y-%m-%d %H:%M:%S" shaded-background=true !  parsebin ! rtph264pay name=pay0 pt=96 )'
            
        elif self.args.command == 'dev':
            if not os.path.exists(self.args.device):
                sys.exit(f"Error: Device {self.args.device} not found")
                
            return (f'( v4l2src device={self.args.device} '
                    f'! video/x-raw,width=640,height=480'
                        f',format=YUY2'
                        f',framerate=30/1 '
                    f'! videoconvert '
                    f'! queue max-size-buffers=1 leaky=downstream '
                    f'! clockoverlay time-format="%Y-%m-%d %H:%M:%S" shaded-background=true '
                    f'! x264enc '
                        f'speed-preset=ultrafast '
                        f'tune=zerolatency '
                        f'byte-stream=true '
                        f'threads=4 '
                        f'key-int-max=30 '
                        # f'intra-refresh=true' -> this for some reason breaks the gstreamer stream on the client side
                    f'! h264parse'
                    f'! rtph264pay '
                        f'config-interval=-1 '
                        f'name=pay0 '
                        f'pt=96 )')
            
        elif self.args.command == 'gen':
            return ('( videotestsrc is-live=true ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 '
                    '! timeoverlay ! clockoverlay time-format="%Y-%m-%d %H:%M:%S" shaded-background=true ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 )')

    def run(self):
        Gst.init(None)
        
        self.server.set_service(str(self.args.port))
        self.server.set_address(self.args.ip)

        pipeline = self.build_pipeline()
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/stream", self.factory)
        
        self.server.attach()
        
        print(f"RTSP server running on rtsp://{self.args.ip}:{self.args.port}/stream")
        print(f"pipeline: {pipeline}")
        GLib.MainLoop().run()

def parse_args():
    parser = argparse.ArgumentParser(prog=f"rtsp-video-streaming-server",
                                   description=f"RTSP Video Streaming Server using GStreamer.\n"
                                               f"To test the server run this on clinet side:\n"
                                               f"gst-launch-1.0 -v rtspsrc "
                                                f"location=rtsp://<server_ip>:<server_port>/stream "
                                                f"latency=0 "
                                                f"drop-on-latency=true "
                                               f"! rtph264depay "
                                               f"! avdec_h264 "
                                               f"! videoconvert "
                                               f"! queue "
                                               f"! autovideosink sync=false")
    
    # Main server arguments
    parser.add_argument('--port', type=int, default=10108,
                       help="Port to listen on (default: %(default)s)")
    parser.add_argument('--ip', default='0.0.0.0',
                       help="IP address to bind to (default: %(default)s)")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # File source
    file_parser = subparsers.add_parser('file', help='Stream from video file')
    file_parser.add_argument('file', help='Path to video file (mp4/mkv)')
    
    # Device source
    dev_parser = subparsers.add_parser('dev', help='Stream from video device')
    dev_parser.add_argument('device', help='Path to video device (e.g. /dev/video0)')
    
    # Generated stream
    subparsers.add_parser('gen', help='Generate test video stream')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    server = VideoStreamServer(args)
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped")
