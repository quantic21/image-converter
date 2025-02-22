import json
import boto3
import os

s3 = boto3.client("s3")
BUCKET_NAME = os.getenv("RAW_BUCKET")

def lambda_handler(event, context):
    try:
        # Since event is already a dictionary, use it directly
        body = event  # No need to parse it

        file_name = body.get("fileName")
        file_size = body.get("fileSize")
        content_type = body.get("contentType")
        output_format = body.get("format")

        # Validate required fields
        if not file_name or not file_size or not content_type:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields."})}

        if int(file_size) > 50 * 1024 * 1024:  # Enforce 50MB size limit
            return {"statusCode": 400, "body": json.dumps({"error": "File too large."})}

        # Store files inside an "uploads/" directory in S3
        s3_key = f"uploads/{file_name}"

        # Generate a presigned PUT URL for the S3 bucket
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": s3_key,
                "ContentType": content_type,
                "ContentLength": int(file_size)
            },
            ExpiresIn=900  # URL expires in 15 minutes
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "presignedUrl": presigned_url,
                "s3Key": s3_key,
                "format": output_format
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
