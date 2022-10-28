import boto3
import random as rd
import json
import uuid
import datetime

##############################################
#######  variaveis para uso do script  #######
##############################################
athdb = 'fakedb'
athtable = 'faketable'
s3bucket = 'fakebucket'
s3bucket_ = 's3://fakebucket/'
s3bucketoutput = 'fakebucketoutput'
s3bucketoutput_ = 's3://fakebucketoutput/'
localfile = 'faketable.json'

dicionario=[]
qtderegistros = 50 #qtde de medicoes
type_s = ['oil','energy','general'] #categorias
subtype_s = ['sub1','sub2','sub3'] #subcategorias
company_id = [12,23,49,56] #clientes Cogni


##############################################
####### credenciais para uso do script #######
##############################################
ACCESS_KEY = ''
SECRET_KEY = ''
AWS_REGION = 'us-east-1'

ath = boto3.client(
    'athena',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

s3_resource = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)


##############################################
####### comando para limpeza do bucket #######
##############################################
s3_resource.Bucket(s3bucket)\
    .object_versions.filter(Prefix="").delete()

s3_resource.Bucket(s3bucketoutput)\
    .object_versions.filter(Prefix="").delete()


##############################################
####### FAKEGENERATOR conteudos random #######
##############################################
for x in range(qtderegistros):
    object_uuid = [str(uuid.uuid4())] #hash AWS
    object_types = [type_s[rd.randint(0,2)]] #categorias
    object_subtypes = [subtype_s[rd.randint(0,2)]] #subcategorias
    object_companyid = [company_id[rd.randint(0,3)]] #clientes Cogni
    object_meterid = [rd.randint(1,15)] #equipamentos monitorados
    object_datetimeread = [str(datetime.datetime.fromtimestamp(rd.randint(1577847600,1615258800)))] #jan/2020_mar/2021
    objects_floatv = [round(rd.uniform(60, 120),3) for x in range(6)] #leituras_float
    objects_floati = [round(rd.uniform(7, 11),3) for x in range(3)] #leituras_float
    objects_freq = [60] #leituras_int
    objects_floatqp = [round(rd.uniform(0, 3),3) for x in range(15)] #leituras_float
    objects = object_uuid + object_types + object_subtypes + object_companyid + \
        object_meterid + object_datetimeread + objects_floatv + objects_floati + \
            objects_freq + objects_floatqp
    categories = ["uuid", "type_s", "subtype_s", "company_id", "meter_id", \
        "datetime_read", "v_an", "v_bn", "v_cn", "v_ab", "v_bc", "v_ca", "i_an", \
            "i_bn", "i_cn", "frequency", "q_a", "q_b", "q_c", "q_total", "p_a", "p_b", \
                "p_c", "p_total", "pf_a", "pf_b", "pf_c", "pf_total", "previous_demand", \
                    "previous_reactive", "previous_pf_total"]
    dicaux = {key: value for key, value in zip(categories, objects)}
    dicionario.append(dicaux)


##############################################
####### conversor string txt >>>> JSON #######
##############################################
with open(localfile, 'w') as f:
    json.dump(dicionario, f, separators=(',', ':'))

with open(localfile,'r') as f:
    c = f.read()
    d=c.replace(',{','\n{').replace('[','').replace(']','')
    with open(localfile,'w+') as g:
        g.write(d)


##############################################
####### conversor string txt >>>> JSON #######
##############################################
s3.upload_file(localfile, s3bucket,localfile)


##############################################
####### comando para criacao DB/Tables #######
##############################################
queryDropTable="drop table if exists " + athdb + "." + athtable
ath.start_query_execution(
    QueryString=queryDropTable,
    QueryExecutionContext={'Database': athdb},
    ResultConfiguration={'OutputLocation': s3bucketoutput_})

queryDropDB="drop database if exists " + athdb
ath.start_query_execution(
    QueryString=queryDropDB,
    ResultConfiguration={'OutputLocation': s3bucketoutput_})

queryCreateDB="create database " + athdb
ath.start_query_execution(
    QueryString=queryCreateDB,
    ResultConfiguration={'OutputLocation': s3bucketoutput_})

queryCreateTable="CREATE EXTERNAL TABLE IF NOT EXISTS " + athdb + "." + athtable + """(
                    `uuid` string,
                    `type_s` string,
                    `subtype_s` string,
                    `company_id` int,
                    `meter_id` int,
                    `datetime_read` string,
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
                    `previous_pf_total` float )"""\
                        "ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe' \
                        WITH SERDEPROPERTIES ('serialization.format' = '1') \
                        LOCATION '" + s3bucket_ + "' \
                        TBLPROPERTIES ('has_encrypted_data'='false');"

ath.start_query_execution(
    QueryString=queryCreateTable,
    QueryExecutionContext={'Database': athdb},
    ResultConfiguration={'OutputLocation': s3bucketoutput_})