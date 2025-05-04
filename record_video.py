# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import signal
from datetime import datetime
import boto3

# AWS S3 setup
s3 = boto3.client('s3')
bucket_name = 'YOUR-S3-BUCKET-NAME'  # Replace with your S3 bucket name

# File paths
pid_file = "/home/avinash/iot-camera/vlc_pid.txt"
record_dir = "/home/avinash/iot-camera"

def start_recording():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{record_dir}/video_{timestamp}.avi"

    cmd = (
        f"cvlc v4l2:///dev/video0 "
        f"--v4l2-width=640 --v4l2-height=480 "
        f"--sout=\"#transcode{{vcodec=DIV3,acodec=none}}:"
        f"standard{{access=file,mux=avi,dst='{filename}'}}\" vlc://quit"
    )

    process = subprocess.Popen(cmd, shell=True)
    with open(pid_file, "w") as f:
        f.write(f"{process.pid}|{filename}")

    print(f"[INFO] Recording started with PID: {process.pid}")

def stop_recording():
    if not os.path.exists(pid_file):
        print("⚠️ No recording process found.")
        return

    with open(pid_file, "r") as f:
        data = f.read().strip()
        pid, filename = data.split("|")
        pid = int(pid)

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"[INFO] Stopped recording process: {pid}")

        # Upload video to S3 if exists
        if os.path.exists(filename):
            s3.upload_file(filename, bucket_name, os.path.basename(filename))
            print("✅ Video uploaded to S3.")
        else:
            print("⚠️ Video file not found.")
    except ProcessLookupError:
        print("⚠️ Process was already terminated.")
    finally:
        os.remove(pid_file)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["start", "stop"]:
        print("Usage: python3 record_video.py <start|stop>")
        sys.exit(1)

    action = sys.argv[1]
    if action == "start":
        start_recording()
    elif action == "stop":
        stop_recording()
