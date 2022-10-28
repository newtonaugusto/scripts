import random
with open('auditoria.csv','r', encoding='utf-8') as f:
    linhas = f.readlines()
    f.close()

x = random.randrange(0,len(linhas)-1)
y = random.randrange(0,len(linhas)-1)
z = random.randrange(0,len(linhas)-1)

print('x: {}  y: {}  z:{}'.format(x,y,z))

with open('random.csv','w') as f:
    f.write(linhas[x])
    f.write(linhas[y])
    f.write(linhas[z])
    f.close()


