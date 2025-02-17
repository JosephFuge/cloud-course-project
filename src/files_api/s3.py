import boto3

BUCKET_NAME = "josephf-cloud-course-bucket"

# session = boto3.Session(profile_name="cloud-course")
session = boto3.Session()
s3_client = session.client("s3")

s3_client.put_object(Bucket=BUCKET_NAME, Key="folder/hello.txt", Body="Hello, World!", ContentType="text/plain",)