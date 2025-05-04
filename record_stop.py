# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import time
import boto3

pid_file = "/home/avinash/iot-camera/vlc_pid.txt"
bucket_name = "pro-23072024"

def kill_camera_users():
    try:
        output = subprocess.check_output(["lsof", "/dev/video0"]).decode()
        lines = output.strip().split("\n")[1:]  # Skip header
        for line in lines:
            parts = line.split()
            pid = int(parts[1])
            os.kill(pid, signal.SIGKILL)
            print(f"[INFO] Force-killed process using /dev/video0: PID {pid}")
    except subprocess.CalledProcessError:
        print("✅ No active process using /dev/video0")

def upload_to_s3(filepath):
    try:
        s3 = boto3.client("s3")
        s3.upload_file(filepath, bucket_name, os.path.basename(filepath))
        print("✅ Video uploaded to S3.")
    except Exception as e:
        print(f"❌ Failed to upload to S3: {e}")

if os.path.exists(pid_file):
    with open(pid_file, "r") as f:
        data = f.read().strip()
        pid, filename = data.split("|")
        pid = int(pid)

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"[INFO] Sent SIGTERM to PID {pid}")
        time.sleep(2)
        os.kill(pid, signal.SIGKILL)  # Force if still alive
        print(f"[INFO] Force killed PID {pid}")
    except ProcessLookupError:
        print("⚠️ Process already terminated.")

    # Extra protection to ensure camera is released
    kill_camera_users()

    if os.path.exists(filename):
        upload_to_s3(filename)
    else:
        print("⚠️ Video file not found.")

    os.remove(pid_file)
else:
    print("⚠️ No recording process found to stop.")
