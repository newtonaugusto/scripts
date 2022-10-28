import pandas as pd
import random as rd
import json
import uuid
import datetime
import boto3

ACCESS_KEY = ''
SECRET_KEY = ''
AWS_REGION = 'us-east-1'

athdb = 'fakedb'
athtable = 'fakecogni'
localfile = 'fakecogni.json'
s3_bucket = 'newtonmiotto-infomach-bucket-0001'
s3_output = 's3://newtonmiotto-infomach-bucket-0001/fakedb/'
s3_output_draft = 's3://newtonmiotto-infomach-bucket-0001/fakedb/draft'

s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION
)

dicionario=[]
qtderegistros = 20 # qtde de registros a serem gerados neste simulador (qtde de medicoes)
type_s = ['oil','energy','general'] # categoria de servicos monitorados pela ferramenta
company_id = [12,23,49,56] # codigo das empresas clientes da Cogni

for x in range(qtderegistros):
    object_uuid = [str(uuid.uuid4())] # hash AWS gerado aleatoriamente para exemplificar consultoria INFOMACH
    object_types = [type_s[rd.randint(0,2)]] # categoria de servicos monitorados pela ferramenta
    object_companyid = [company_id[rd.randint(0,3)]] # codigo das empresas clientes da Cogni
    object_meterid = [rd.randint(1,15)] #numero de equipamentos monitorados
    object_datetimeread = [str(datetime.datetime.fromtimestamp(rd.randint(1577847600,1615258800)))] # datas de coleta aleatorias de jan/2020 a mar/2021
    objects_floatv = ["{:.3f}".format(rd.uniform(60, 120)) for x in range(6)] # valores de leitura float obtidos dos equipamentos
    objects_floati = ["{:.3f}".format(rd.uniform(7, 11)) for x in range(3)] # valores de leitura float obtidos dos equipamentos
    objects_freq = [60] # valores de leitura float obtidos dos equipamentos
    objects_floatqp = ["{:.3f}".format(rd.uniform(0, 3)) for x in range(15)] # valores de leitura float obtidos dos equipamentos

    objects = object_uuid + object_types + object_companyid + object_meterid + object_datetimeread + objects_floatv + objects_floati + objects_freq + objects_floatqp
    categories = ["uuid", "type_s", "company_id", "meter_id", "datetime_read", "v_an", "v_bn", "v_cn", "v_ab", "v_bc", "v_ca", "i_an", "i_bn", "i_cn", "frequency", "q_a", "q_b", "q_c", "q_total", "p_a", "p_b", "p_c", "p_total", "pf_a", "pf_b", "pf_c", "pf_total", "previous_demand", "previous_reactive", "previous_pf_total"]
 
    dicaux = {key: value for key, value in zip(categories, objects)}
    dicionario.append(dicaux)

with open(localfile, 'w') as f:
    json.dump(dicionario, f,indent=2)


# traz o arquivo do S3
# s3.download_file(s3_bucket, localfile)

# envia o arquivo para o S3
s3.upload_file(localfile, s3_bucket,localfile)