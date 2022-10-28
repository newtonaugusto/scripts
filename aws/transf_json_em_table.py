import boto3
import json
import os
import sys
import psycopg2
import csv
from collections import defaultdict

ACCESS_KEY = ''
SECRET_KEY = ''
AWS_REGION = 'us-east-1'

# def jsonfile(path):
#     session = boto3.Session(
#         aws_access_key_id=ACCESS_KEY,
#         aws_secret_access_key=SECRET_KEY,
#         region_name=AWS_REGION)
#     s3 = session.resource('s3')
#     bucket= s3.Bucket('newtonmiotto-infomach-bucket-0001')
#     with open(path, 'rb') as data:
#         res=json.load(data)

def jsonfile(path):
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws__access_key=SECRET_KEY,
        region_name=AWS_REGION)
    s3 = session.resource('s3')
    bucket= s3.Bucket('newtonmiotto-infomach-bucket-0001')
    with open(path, 'rb') as data:
        res=json.load(data)
        f = open('data.csv','wb')
        output = csv.writer(f) 
        output.writerow(res[0].keys())
        for row in res:
           output.writerow(row.values()) 


    bucket.put_object(Key=(r'C:\Users\newton.miotto\Documents\Script\aws\data.csv'),Body=res)
    print ('success')

def redshift():
    co=psycopg2.connect(dbname= 'dev', host='redshift-cluster-1.cqhim65fktae.us-east-1.redshift.amazonaws.com', 
    port= '5439', user= '', password= '')
    curr = co.cursor()
    # curr.execute("""copy sample from 's3://ag-redshift-poc/testfile/json.txt'
    #             CREDENTIALS 'aws_access_key_id=;aws_secret_access_key='
    #             """)
    curr.execute("""
    COPY fakedb FROM 's3://newtonmiotto-infomach-bucket-0001/fakecogni.json'
CREDENTIALS 'aws_access_key_id=;aws_secret_access_key='
REGION 'us-east-1'
JSON 'auto'
""")

    co.commit()
    print ('success')
    curr.close()
    co.close()

# jsonfile('fakecogni.json')
redshift()


       


  
# def redshift():
#     co=psycopg2.connect(dbname= 'redshiftpoc', host='shdjf', 
#     port= '5439', user= 'admin', password= 'snd')
#     curr = co.cursor()
#     curr.execute("""copy sample from 's3://ag-redshift-poc/testfile/json.txt'
#                 CREDENTIALS 'aws_access_key_id=;aws_secret_access_key='
#                 """)
#     co.commit()
#     print 'success'
#     curr.close()
#     co.close()





# redshift()