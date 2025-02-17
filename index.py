import json, boto3, os

s3 = boto3.client("s3")
BUCKET_NAME = os.getenv("RAW_BUCKET")

def lambda_handler(event, context):
    try:
        # Parse the request body
        if not event.get("body"):
            return {"statusCode": 400, "body": json.dumps({"error": "Request body is missing."})}

        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON format in request body."})}

        file_name = body.get("fileName")
        file_size = body.get("fileSize")

        # Validate file name and size
        if not file_name:
            return {"statusCode": 400, "body": json.dumps({"error": "File name is required."})}
        if not file_size or int(file_size) <= 0:
            return {"statusCode": 400, "body": json.dumps({"error": "File size must be greater than 0."})}

        # Enforce size limit (e.g., 50MB max)
        if int(file_size) > 50 * 1024 * 1024:
            return {"statusCode": 400, "body": json.dumps({"error": "File too large."})}

        # Generate presigned URL for uploading to S3
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_name, "ContentLength": int(file_size)},
            ExpiresIn=900  # URL expires in 15 minutes
        )

        # Return the presigned URL
        return {
            "statusCode": 200,
            "body": json.dumps({"presignedUrl": presigned_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }