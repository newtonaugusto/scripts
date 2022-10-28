import boto3

ACCESS_KEY = ''
SECRET_KEY = ''

s3folder = 'textract-console-us-east-2-77f945c8-4c5b-4db1-820e-7285510a562f'
s3file = 'nf_009.209.565___energisa.pdf'
localfile = 'myfile0.pdf'

s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

s3.download_file(s3folder,s3file, localfile)