import os

file_out = r'C:\Users\newton.miotto\Documents\movidesk api\Consulta Ticket API\extract pronto\csv\csv correcao date\agrupado\relatorio.csv'
pasta = r'C:\Users\newton.miotto\Documents\movidesk api\Consulta Ticket API\extract pronto\csv\csv correcao date'
caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv = [arq for arq in arquivos if arq.lower().endswith(".csv")]

with open(file_out, 'w', encoding='utf8') as saida:
    for c in csv:
        print(c)
        with open(c, 'r', encoding='utf8') as arq:
            for line in arq.readlines():
                saida.write(line)
            arq.close()
