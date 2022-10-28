import streamlit as st # importa streamlit para gerar a página web com os dados
import pandas as pd # importa o pandas para trabalhar com os arquivos '.csv'
import numpy as np # importa o numpy para usar as listas e arrays corretamente
from datetime import datetime

# Constantes
DATA_COLUMN = "birthday"
DATA_URL = r"C:\Users\newton.miotto\Documents\dados teste\fakenamegenerator.csv"


@st.cache #carrega no cache
def load_data(nrows):
    # Carrega os dados do csv e muda o nome das colunas para lowercase afim de evitar problemas
    dados = pd.read_csv(DATA_URL, delimiter=";", nrows=nrows)
    lowercase = lambda x: str(x).lower()
    dados.rename(lowercase, axis="columns", inplace=True)
    
    dados[DATA_COLUMN] = pd.to_datetime(dados[DATA_COLUMN],format='%m/%d/%Y', infer_datetime_format=True)
    for x in dados[DATA_COLUMN]:
        print(x)

    # Convertendo em date para trabalhar com os filtros
    # dados[DATA_COLUMN] = pd.to_datetime(dados[DATA_COLUMN], format="%m/%d/%Y")
    # dados[DATA_COLUMN].head()
    # dados[DATA_COLUMN] = datetime.datetime.strptime(dados[DATA_COLUMN], "%m/%d/%Y").strftime("%d/%m/%Y")
    

    # print(type(dados.iloc[:21]))
    # dados[DATA_COLUMN] = dados.iloc[:,21].apply(lambda x: datetime.strptime(x, "%m/%d/%Y").strftime("%d/%m/%Y")) #Arruma a exibição das datas
    # dados[DATA_COLUMN] = pd.to_datetime(dados[DATA_COLUMN])
    # dados = dados.iloc[:,21].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))

    # for i, x in enumerate(dados[DATA_COLUMN]):
    #     # dados[DATA_COLUMN][i] = datetime.strptime(x, "%m/%d/%Y").strftime("%d/%m/%Y")
    #     dados[DATA_COLUMN][i] = datetime.strptime(x, "%m/%d/%Y")
    #     print(type(dados[DATA_COLUMN][i]))
    
    # print(type(dados[DATA_COLUMN]))
    # for x in dados[DATA_COLUMN]:
    #     # x = pd.to_datetime(x,format('%d/%m/%Y')).date()
    #     x = datetime.strptime(x,'%m/%d/%Y')
    #     x = datetime.strptime(x.strftime('%d/%m/%Y'),"%d/%m/%Y")
    #     landslides['date_parsed'] = pd.to_datetime(landslides['date'], format="%m/%d/%y")
    #     print(x)
    return dados

def main(): # função principal
    dados = load_data(3000)
    st.title("Dashboard Pessoas")
    st.markdown("""Dados gerados no site [**fake name generator**](https://www.fakenamegenerator.com/).""")

    if st.sidebar.checkbox("Mostrar tabela?"):
        st.header("Dados")
        st.write(dados)
    
    ano = st.sidebar.slider("Selecione o intervalo do ano de nascimento")
    # ano_max = dados[DATA_COLUMN]
    # ano_min = dados[DATA_COLUMN]
    # print("Este é o ano maximo: {}",ano_max.dtypes)
    # print("Este é o ano minimo: {}",ano_min.dtypes)
    # hist_values = np.histogram(dados[DATA_COLUMN].dt.year, bins=(int(ano_max) - int(ano_min)), 
    # range=(0, int(ano_max) - int(ano_min)))
    # st.bar_chart(hist_values)

    st.sidebar.info("Foram carregadas {} linhas".format(dados.shape[0]))

if __name__ == '__main__':
    main()