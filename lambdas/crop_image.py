import base64
import boto3
import io
import os
from PIL import Image

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'my-local-bucket')

def lambda_handler(event, context):
    try:
        file_name = event['file_name']
        img_data = base64.b64decode(event['image_base64'])
        
        image = Image.open(io.BytesIO(img_data))
        
        width, height = image.size
        target_w = 255
        target_h = 255
        
        left = int((width - target_w) / 2)
        top = int((height - target_h) / 2)
        right = left + target_w
        bottom = top + target_h
        
        cropped_image = image.crop((left, top, right, bottom))
        
        buffer = io.BytesIO()
        cropped_image.save(buffer, format="JPEG")
        buffer.seek(0)
        
        s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=buffer.getvalue())
        
        return {
            "statusCode": 200,
            "body": f"Image {file_name} successfully cropped and uploaded to {BUCKET_NAME}!"
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}