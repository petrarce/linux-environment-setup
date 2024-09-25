#!/usr/bin/python3
import argparse
import os
import subprocess
from flask import Flask, Response, send_from_directory


parser = argparse.ArgumentParser(prog=__name__, description="HTTP Live Streaming")
parser.add_argument("-p", "--http-port", help="http port on which stream will served", required=False, default=8080)
parser.add_argument("--stream-location", help="stream metadata output location", required=False, default=os.path.realpath(os.path.curdir))
parser.add_argument("--host", help="ip4 address on which the stream should be published", required=False, default="0.0.0.0")
parser.add_argument("--playlist-file-name", help="the name of the playlist file", required=False, default="stream")
parser.add_argument("--capture-stream-from-device", help="if true will capture stream from device provided in option --device", required=False, action="store_true")
parser.add_argument("--device", help="device location, where the stream will be taken from", required=False, default="/dev/video0")

args = parser.parse_args()

# Directory where HLS segments and playlists are stored
hlsDir = args.stream_location
playlistFile = args.playlist_file_name
host = args.host
httpPort = args.http_port
captureFromDev = args.capture_stream_from_device
device = args.device

#start gstreamer and capture video stream
gstVideoSource = f"v4l2src device={device}" if captureFromDev else "videotestsrc is-live=true"
subprocess.Popen(f'gst-launch-1.0 -v   {gstVideoSource} '
               f' !   videoconvert '
               f' !   x264enc '
               f' !   hlssink2 location={hlsDir}/segment%05d.ts target-duration=5   playlist-location={hlsDir + "/" + playlistFile}',
               shell=True)

#define http responces and start flusk http server
app = Flask(__name__)

@app.route('/' + playlistFile)
def playlist():
    # Serve the playlist file
    return send_from_directory(hlsDir, playlistFile)

@app.route('/<segment_name>.ts')
def segments(segment_name):
    # Serve the segment files
    return send_from_directory(hlsDir, f'{segment_name}.ts')

if __name__ == '__main__':
    # Flask app runs on localhost:5000 by default
    app.run(host=host, port=httpPort)