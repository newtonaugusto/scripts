import os
import pandas as pd

file_out = r'C:\Users\newton.miotto\Documents\movidesk api\Códigos Python de extração do movidesk\Consulta Ticket API\extract pronto\csv\com sla\relatorio.csv'
# pasta = r'C:\Users\newton.miotto\Documents\movidesk api\Códigos Python de extração do movidesk\Consulta Ticket API\extract pronto\csv\com sla'
# caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
# arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
# csv = [arq for arq in arquivos if arq.lower().endswith(".csv")]

# with open(file_out, 'w', encoding='utf8') as saida:
#     for c in csv:
#         print(c)
#         with open(c, 'r', encoding='utf8') as arq:
#             for line in arq.readlines():
#                 saida.write(line)
#             arq.close()

tickets = pd.read_csv(file_out, delimiter=";")
tickets = tickets.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
pd.DataFrame(tickets).to_csv(f'tickets.csv', index=False, header=tickets.columns, sep=';', encoding="utf-8")
