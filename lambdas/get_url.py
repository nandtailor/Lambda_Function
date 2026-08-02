import boto3
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'my-local-bucket')

def lambda_handler(event, context):
    try:
        file_name = event['file_name']
        
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_name},
            ExpiresIn=3600
        )
        
        return {
            "statusCode": 200,
            "url": presigned_url
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}