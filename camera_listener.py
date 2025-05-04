import ssl
import json
import subprocess
from paho.mqtt.client import Client

THING_NAME = "raspberrypi-cam"
ENDPOINT = "AWS_IOT_CORE_ENDPOINT"
TOPIC = "raspi/camera"

# Replace with your cert/key paths
CA_PATH = "AmazonRootCA1.pem"
CERT_PATH = "certificate.pem.crt"
KEY_PATH = "private.pem.key"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")

    if action == "capture":
        subprocess.run(["python3", "capture_image.py"])
    elif action == "record":
        subprocess.run(["python3", "record_video.py", "start"])
    elif action == "stop":
        subprocess.run(["python3", "record_stop.py"])  # Call record_stop.py directly
    else:
        print(f"⚠️ Unknown action: {action}")

client = Client()
client.tls_set(ca_certs=CA_PATH,
               certfile=CERT_PATH,
               keyfile=KEY_PATH,
               tls_version=ssl.PROTOCOL_TLSv1_2)

client.on_connect = on_connect
client.on_message = on_message

client.connect(ENDPOINT, 8883, 60)

client.loop_forever()
