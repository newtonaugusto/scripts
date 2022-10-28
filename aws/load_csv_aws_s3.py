import boto3
acess_key = ''
secret_key = ''
aws_region = 'us-east-1'

s3_bucket = 'newtonmiotto-infomach-bucket-0001'

csv_path = 'fakecogni.csv'
target_file = 'fakecsv.csv'


# s3 = boto3.client(
#     's3',
#     aws_access_key_id=acess_key,
#     aws_secret_access_key=secret_key,
#     region_name=aws_region
# )

session = boto3.Session(
    aws_access_key_id=acess_key,
    aws_secret_access_key=secret_key,
    region_name=aws_region
)
s3 = session.resource('s3')
bucket = s3.Bucket(s3_bucket)
with open(csv_path, 'rb') as data:
    bucket.put_object(Key=target_file, Body=data)
# //your s3 path will be /some/path/to-s3/test-x.csv

# s3.meta.client.upload_file(csv_path, s3_bucket, target_file)

