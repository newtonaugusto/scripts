#encoding: utf-8

import requests
import json 
from datetime import datetime, timedelta
import pandas as pd
import csv

json_var = requests.get("https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge 2021-03-01 and t/date le 2021-03-31))&$top=100").text
valor = json.loads(json_var)
json_final = json.dumps(valor, indent=4)

with open("out5.json", "w") as f:
    print(json_final, file=f)