import pandas as pd

file_name = 'fakecogni.csv'
path_json = 'fakecogni.json'
df = pd.read_json(path_json)
csv = df.to_csv(file_name, encoding='utf-8', index=False)

