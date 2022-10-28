import boto3

ACCESS_KEY = ''
SECRET_KEY = ''
AWS_REGION = 'us-east-1'

S3_KEY = 'fakecogni.json'
TARGET_FILE = 'fakefake.json'
S3_BUCKET = 'datalaketeste1090'

s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

query = """SELECT * FROM S3Object WHERE `type_s` <> 'oil'"""

result = s3.select_object_content(Bucket=S3_BUCKET,
                                    Key=S3_KEY,
                                    ExpressionType='SQL',
                                    Expression=query,
                                    InputSerialization={'JSON': {'Type': 'LINES'}},
                                    OutputSerialization={'JSON': {}})

with open(TARGET_FILE, 'w') as filtered_file:
    for record in result['Payload']:
        if 'Records' in record:
            res = record['Records']['Payload'].decode('utf-8')
            filtered_file.write(res)