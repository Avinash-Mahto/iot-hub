import boto3
import json

client = boto3.client('iot-data', region_name='ap-southeast-1')

def lambda_handler(event, context):
    # Determine the action based on the API Gateway path
    path = event.get('rawPath', '')
    if path.endswith('/record'):
        action = 'record'
    elif path.endswith('/stop'):
        action = 'stop'
    elif path.endswith('/capture'):
        action = 'capture'
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid action')
        }

    # Publish to the IoT topic with the selected action
    response = client.publish(
        topic='raspi/camera',  # This must match the topic your Pi subscribes to
        qos=1,
        payload=json.dumps({
            "action": action
        })
    )

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        'body': json.dumps(f'Command "{action}" sent to Raspberry Pi.')
    }

