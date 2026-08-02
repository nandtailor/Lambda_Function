import sys
import os
import base64
import json
import boto3
import webbrowser

LOCALSTACK_URL = "http://localhost:4566"
BUCKET_NAME = "my-local-bucket"
INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"

def process_image(image_name):
    
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    
    input_path = os.path.join(INPUT_DIR, image_name) if not os.path.isabs(image_name) and not image_name.startswith(INPUT_DIR) else image_name
    
    if not os.path.exists(input_path):
        print(f"Error: Image '{input_path}' nahi mili!")
        print(f"Tip: Image ko '{INPUT_DIR}/' folder me daalein.")
        return

    file_name = os.path.basename(input_path)
    output_filename = f"cropped_{file_name}"
    local_output_path = os.path.join(OUTPUT_DIR, output_filename)

    print(f"1. Reading image from '{input_path}'...")
    with open(input_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    lambda_client = boto3.client('lambda', endpoint_url=LOCALSTACK_URL, region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')
    s3_client = boto3.client('s3', endpoint_url=LOCALSTACK_URL, region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')

    payload = {
        "file_name": output_filename,
        "image_base64": img_base64
    }

    print("2. Invoking Lambda function...")
    response = lambda_client.invoke(
        FunctionName='crop_image_function',
        Payload=json.dumps(payload)
    )

    if response.get('StatusCode') == 200:
        cropped_url = f"{LOCALSTACK_URL}/{BUCKET_NAME}/{output_filename}"
        
        
        print("3. Downloading cropped image to outputs/ folder...")
        s3_client.download_file(BUCKET_NAME, output_filename, local_output_path)

        print("\nSUCCESS!")
        print(f"Input Image : {input_path}")
        print(f"Output Saved: {local_output_path}")
        print(f"S3 URL      : {cropped_url}\n")

        print("Opening in browser...")
        webbrowser.open(cropped_url)
    else:
        print("Processing failed!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process.py <image_name_in_inputs_folder>")
    else:
        process_image(sys.argv[1])
