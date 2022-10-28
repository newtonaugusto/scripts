import pandas as pd
from datetime import datetime, timedelta

df2 = pd.read_csv("tickets.csv", delimiter=";")
df2['created_date'] = pd.to_datetime(df2['created_date']) - timedelta(hours=3)
df2['sla_response_date'] = pd.to_datetime(df2['sla_response_date']) - timedelta(hours=3)
df2['sla_real_response_date'] = pd.to_datetime(df2['sla_real_response_date']) - timedelta(hours=3)
df2['sla_solution_date'] = pd.to_datetime(df2['sla_solution_date']) - timedelta(hours=3)
df2.to_csv('tickets_new_date.csv', index=False, header=df2.columns, sep=';', encoding='utf-8')