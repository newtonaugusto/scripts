import boto3

ACCESS_KEY = ''
SECRET_KEY = ''
AWS_REGION = 'us-east-1'

athdb = 'fakedb'
athtable = 'fakecogni'
s3_bucket = 'newtonmiotto-infomach-bucket-0001'
s3_output = 's3://newtonmiotto-infomach-bucket-0001/fakedb/'
s3_output_draft = 's3://newtonmiotto-infomach-bucket-0001/fakedb/draft'

s3_resource = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

res = []
bucket=s3_resource.Bucket(s3_bucket)
for obj_version in bucket.object_versions.filter(Prefix='fakedb/'):
    res.append({'Key': obj_version.object_key,'VersionId': obj_version.id})
bucket.delete_objects(Delete={'Objects': res})
 
ath = boto3.client(
'athena',
aws_access_key_id=ACCESS_KEY,
aws_secret_access_key=SECRET_KEY,
region_name=AWS_REGION
)

queryDropTable="drop table if exists " + athdb + "." + athtable
ath.start_query_execution(
    QueryString=queryDropTable,
    QueryExecutionContext={'Database': athdb},
    ResultConfiguration={'OutputLocation': s3_output_draft})

queryDropDB="drop database if exists " + athdb
ath.start_query_execution(
    QueryString=queryDropDB,
    ResultConfiguration={'OutputLocation': s3_output_draft})

queryCreateDB="create database " + athdb
ath.start_query_execution(
    QueryString=queryCreateDB,
    ResultConfiguration={'OutputLocation': s3_output})

queryCreateTable="create external table " + athdb + "." + athtable + """(
                    `uuid` string,
                    `type_s` string,
                    `company_id` int,
                    `meter_id` int,
                    `datetime_read` date,
                    `v_an` float,
                    `v_bn` float,
                    `v_cn` float,
                    `v_ab` float,
                    `v_bc` float,
                    `v_ca` float,
                    `i_an` float,
                    `i_bn` float,
                    `i_cn` float,
                    `frequency` float,
                    `q_a` float,
                    `q_b` float,
                    `q_c` float,
                    `q_total` float,
                    `p_a` float,
                    `p_b` float,
                    `p_c` float,
                    `p_total` float,
                    `pf_a` float,
                    `pf_b` float,
                    `pf_c` float,
                    `pf_total` float,
                    `previous_demand` float,
                    `previous_reactive` float,
                    `previous_pf_total` float )"""" Location '" + s3_output + "';"

ath.start_query_execution(
    QueryString=queryCreateTable,
    QueryExecutionContext={'Database': athdb},
    ResultConfiguration={'OutputLocation': s3_output})