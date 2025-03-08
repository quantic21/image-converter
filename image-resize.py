import boto3
import io
from PIL import Image, UnidentifiedImageError
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Resizes an image from one S3 bucket and uploads it to another."""

    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        target_bucket = os.environ['TARGET_BUCKET']

        # Get dimensions from environment variables, with defaults and error handling
        try:
            width = int(os.environ.get('RESIZE_WIDTH', 300))
        except ValueError:
            width = 300  # Default if invalid value or not set

        try:
            height = int(os.environ.get('RESIZE_HEIGHT', 300))
        except ValueError:
            height = 300  # Default if invalid value or not set


        obj = s3.get_object(Bucket=source_bucket, Key=source_key)
        image_bytes = obj['Body'].read()

        try:
            image = Image.open(io.BytesIO(image_bytes))
        except UnidentifiedImageError:
            return {
                'statusCode': 400,
                'body': f'Error: Could not open or identify image: {source_key}'
            }

        image.thumbnail((width, height))

        resized_image_bytes = io.BytesIO()
        format = image.format or "JPEG"
        image.save(resized_image_bytes, format=format)
        resized_image_bytes.seek(0)

        target_key = f"resized_{width}x{height}_{os.path.splitext(source_key)[0]}.{format.lower()}"
        content_type = f"image/{format.lower()}" if format.lower() != "jpeg" else "image/jpeg"

        s3.put_object(
            Bucket=target_bucket,
            Key=target_key,
            Body=resized_image_bytes,
            ContentType=content_type
        )

        return {
            'statusCode': 200,
            'body': f'Image resized to {width}x{height} and uploaded to {target_bucket}/{target_key}'
        }

    except Exception as e:
        print(f"Error: {e}")  # Print for CloudWatch logs
        return {
            'statusCode': 500,
            'body': f'Error resizing image: {e}'
        }
