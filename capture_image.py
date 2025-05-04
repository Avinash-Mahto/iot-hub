import os
from datetime import datetime
import boto3
import time

# AWS S3 setup
s3 = boto3.client('s3')
bucket_name = 'YOUR-S3-BUCKET'

# Delay to allow camera to adjust
time.sleep(3)

# Create filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"/home/avinash/iot-camera/image_{timestamp}.jpg"

# Capture image using fswebcam
os.system(f"fswebcam -r 1280x720 --jpeg 85 -D 5 {filename}")

# Upload to S3
if os.path.exists(filename):
    s3.upload_file(filename, bucket_name, os.path.basename(filename))
    print("Image uploaded successfully.")
else:
    print("Failed to capture image.")
