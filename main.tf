provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    iam    = "http://localhost:4566"
    lambda = "http://localhost:4566"
    s3     = "http://localhost:4566"
  }
}

# 1. S3 Bucket
resource "aws_s3_bucket" "image_bucket" {
  bucket = "my-local-bucket"
}

# 2. IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_s3_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# 3. Attach S3 Policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# 4. Zip the Python Code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambdas"
  output_path = "${path.module}/lambdas.zip"
}

# 5. Lambda 1 (Crop Image)
resource "aws_lambda_function" "crop_image_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "crop_image_function"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "crop_image.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_bucket.id
    }
  }
}

# 6. Lambda 2 (Get URL)
resource "aws_lambda_function" "get_url_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "get_url_function"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "get_url.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_bucket.id
    }
  }
}