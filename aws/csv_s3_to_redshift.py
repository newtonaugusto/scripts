import boto3
import os
import sys
import psycopg2
from collections import defaultdict

# target_file = 'fakecsv.csv'

def redshift():
    co=psycopg2.connect(dbname= 'dev', host='redshift-cluster-1.cqhim65fktae.us-east-1.redshift.amazonaws.com', 
    port= '5439', user= '', password= '')
    curr = co.cursor()
    # curr.execute("""copy sample from 's3://ag-redshift-poc/testfile/json.txt'
    #             CREDENTIALS 'aws_access_key_id=;aws_secret_access_key='
    #             """)
    curr.execute("""
    COPY (uuid,type_s,company_id,meter_id,datetime_read,v_an,v_bn,v_cn,v_ab,v_bc,v_ca,i_an,i_bn,i_cn,frequency,q_a,q_b,q_c,q_total,p_a,p_b,p_c,p_total,pf_a,pf_b,pf_c,
    pf_total,previous_demand,previous_reactive,previous_pf_total) 
    FROM 's3://newtonmiotto-infomach-bucket-0001/fakecsv.csv' iam_role 'arn:aws:iam::048924572697:role/S3AcessForRedshift' DELIMITER ',' IGNOREHEADER 1 TIMEFORMAT 'auto';""")

redshift()