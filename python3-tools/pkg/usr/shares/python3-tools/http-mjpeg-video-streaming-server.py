#!/usr/bin/python3
import argparse
import os
import subprocess
from flask import Flask, Response

parser = argparse.ArgumentParser(prog=__name__, description="HTTP MJPEG Streaming")
parser.add_argument("-p", "--http-port", help="http port on which stream will served", required=False, default=8080)
parser.add_argument("--host", help="ip4 address on which the stream should be published", required=False, default="0.0.0.0")
parser.add_argument("--capture-stream-from-device", help="if true will capture stream from device provided in option --device", required=False, action="store_true")
parser.add_argument("--device", help="device location, where the stream will be taken from", required=False, default="/dev/video0")

args = parser.parse_args()
host = args.host
httpPort = args.http_port
captureFromDev = args.capture_stream_from_device
device = args.device

# Create GStreamer pipeline for MJPEG
gstVideoSource = f"v4l2src device={device}" if captureFromDev else "videotestsrc is-live=true"
pipeline = f"{gstVideoSource} ! videoconvert ! jpegenc ! appsink name=appsink emit-signals=true"

# Start Flask server
app = Flask(__name__)

@app.route('/stream.mjpg')
def mjpeg_stream():
    def generate():
        # Create GStreamer pipeline
        gst = Gst.parse_launch(pipeline)
        appsink = gst.get_by_name('appsink')
        gst.set_state(Gst.State.PLAYING)
        
        # Stream frames continuously
        while True:
            sample = appsink.emit('pull-sample')
            if sample:
                buffer = sample.get_buffer()
                _, map_info = buffer.map(Gst.MapFlags.READ)
                if map_info:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + 
                           bytes(map_info.data) + b'\r\n')
                    buffer.unmap(map_info)
    
    return Response(generate(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Import GStreamer inside main to ensure proper initialization
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    
    print(f"MJPG stream available at: http://{host}:{httpPort}/stream.mjpg")
    print("Press Ctrl+C to stop the server")
    app.run(host=host, port=httpPort)
