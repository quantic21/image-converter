import boto3
import io
from PIL import Image, UnidentifiedImageError
from PIL import features
import os


print("WEBP support:", features.check("webp"))
print("Pillow version:", Image.__version__)

# Initialize S3 client
s3 = boto3.client('s3')

# Replace with your actual bucket names
OUTPUT_BUCKET_NAME = "619071325931-processed-files"

# Allowed image formats
VALID_FORMATS = ["JPEG", "PNG", "WEBP"]

def lambda_handler(event, context):
    try:
        # Get the uploaded file details from S3 event
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Extract file extension
        file_ext = object_key.split('.')[-1].lower()
        
        # Map extensions to PIL formats
        ext_to_format = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
        
        if file_ext not in ext_to_format:
            return {"statusCode": 400, "body": "Unsupported file type"}

        input_format = ext_to_format[file_ext]

        # Download the image from S3
        image_object = s3.get_object(Bucket=bucket_name, Key=object_key)
        image = Image.open(io.BytesIO(image_object['Body'].read()))
        
        # Convert RGBA to RGB when necessary
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Loop through all valid formats except the original format
        for target_format in VALID_FORMATS:
            if target_format == input_format:
                continue  # Skip if the target format is the same as the input format

            # Convert the image
            img_byte_arr = io.BytesIO()
            if target_format == "WEBP":
                image.save(img_byte_arr, format=target_format, lossless=True)  # Enable lossless WEBP
            else:
                image.save(img_byte_arr, format=target_format)
            img_byte_arr.seek(0)

            # Generate new filename
            base_name = os.path.splitext(object_key)[0].split("/")[-1]  # Remove directory path
            new_filename = f"converted/{base_name}.{target_format.lower()}" 

            # Upload converted image to output bucket
            content_type = f"image/{target_format.lower()}" if target_format.lower() != "jpeg" else "image/jpeg"
            s3.put_object(Bucket=OUTPUT_BUCKET_NAME, Key=new_filename, Body=img_byte_arr, ContentType=content_type)

        return {"statusCode": 200, "body": f"Image converted successfully and saved in {OUTPUT_BUCKET_NAME}"}

    except UnidentifiedImageError:
        return {"statusCode": 400, "body": "Unsupported or corrupted image format"}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}


