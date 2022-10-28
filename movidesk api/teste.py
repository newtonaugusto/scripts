from datetime import datetime, timedelta

date_text = "40:10:01"
x = date_text.split(":")
hours = timedelta(hours=int(x[0]), minutes=int(x[1]), seconds=int(x[2]))
print(hours)