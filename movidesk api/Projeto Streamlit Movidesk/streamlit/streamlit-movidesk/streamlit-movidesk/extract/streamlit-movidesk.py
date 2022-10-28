import pandas as pd 
from pandas import ExcelWriter
from pandas import ExcelFile
import io
import os
import base64
import streamlit as st
import numpy as np # importa o numpy para usar as horas_clientes e arrays corretamente
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import time
import altair as alt
import matplotlib.pyplot as plt
# from boto3.session import Session

# ACCESS_KEY=''
# SECRET_KEY=''

# session = Session(aws_access_key_id=ACCESS_KEY,
#                   aws_secret_access_key=SECRET_KEY)
# s3 = session.resource('s3')
# your_bucket = s3.Bucket('streamlitmovidesk')

# for s3_file in your_bucket.objects.all():
#     print(s3_file.key)

URL = r"C:\Users\newton.miotto\Documents\movidesk api\Projeto Streamlit Movidesk\dados\agrupado\relatorio.csv"
DATE_COLUMN = "data da action"

### Carrega no cache
@st.cache 
def load_data(nrows):
    ### Carrega todos os dados se '-1' ou o número de linhas
    if (nrows == -1):
        df = pd.read_csv(URL, delimiter=";")
    else:
        df = pd.read_csv(URL, delimiter=";", nrows=nrows)

    ### Muda o nome das colunas para lowercase afim de evitar problemas
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    ### Converte o respectivo campo para datetime
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN],format="%Y/%m/%d")

    ### Converte coluna para timedelta
    workTime = []
    for t in pd.to_timedelta(df['tempo trabalhado']):
        hours = (t.total_seconds()/3600)
        hours = round(hours,2)
        workTime.append(hours)

    df['hours'] = workTime
    
    return df




# def clean_filter(list_to_clean):
#     list_to_clean = []
#     return list_to_clean

### Carrega os dados
st. set_page_config(layout="wide") 
df = load_data(-1)
df = df.sort_values(by=['data da action'])

### Sidebar
st.sidebar.header("Parâmetros")
info_sidebar = st.sidebar.empty() ### Place holder, para o filtro que acontecerá depois

if st.sidebar.checkbox("Exibir tabela completa?"):
    exibir_tabela = True
else:
    exibir_tabela = False

initial = datetime.strptime('01-03-2021', '%d-%m-%Y').date()
final = datetime.strptime('31-03-2021', '%d-%m-%Y').date()
today = date.today()
start_date = min(df[DATE_COLUMN]).date()
end_date = max(df[DATE_COLUMN]).date()

with st.sidebar.beta_expander("Filtros de data"):
    pre_filters = st.selectbox(
        'Filtros pré-definidos',
        ('Último Mês', 'Esse Mês', 'Ontem', 'Últimos 7 dias', 'Últimos 30 dias', 'Digite o intervalo...'))
    ### Se no futuro aumentar a frequência dos dados, é possível adicionar o filtro 'hoje'
    
    ### Filtros de data pré definidos
    if(pre_filters == 'Digite o intervalo...'):
        start_date = st.date_input('Data de início', initial,min_value=min(df[DATE_COLUMN]),max_value=max(df[DATE_COLUMN]))
        end_date = st.date_input('Data de fim', final,min_value=min(df[DATE_COLUMN]),max_value=max(df[DATE_COLUMN]))
        if start_date < end_date:
            st.sidebar.success('Sucesso! Intervalo: \n\n`%s` até `%s`' % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
        else:
            st.error('Erro: A data final deve ser maior que a data inicial.')
    elif(pre_filters == 'Último Mês'):
        end_date = date.today().replace(day=1) - timedelta(days=1) 
        start_date = end_date - relativedelta(months=1) + timedelta(days=1) 
        st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
    elif(pre_filters == 'Esse Mês'):
        start_date = date.today().replace(day=1)
        end_date = date.today()
        st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
    # elif(pre_filters == 'Hoje'):
    #     start_date = date.today()
    #     end_date = date.today()
    #     st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
    elif(pre_filters == 'Ontem'):
        start_date = date.today() - timedelta(days=1)
        end_date = start_date
        st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
    elif(pre_filters == 'Últimos 7 dias'):
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
    elif(pre_filters == 'Últimos 30 dias'):
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))

### Checkbox da tabela
tabela = st.sidebar.empty()

### Multiselect com os labels únicos
labels = df['tipo de hora'].unique().tolist()
with st.sidebar.beta_expander("Tipo de Hora"):
    label_to_filter = st.multiselect(
        label="Escolha o tipo de hora",
        options=labels,
        default=["Normal","Extra"]
    )

clientes = df['clientes'].unique().tolist()
clientes = sorted(clientes)
default_clientes = clientes.copy()
default_clientes.remove('Infomach')
default_clientes.remove('Infomach - Comercial')
default_clientes.remove('Infomach - Comercial,Infomach')
default_clientes.remove('Infomach,Infomach')
default_clientes.remove('Infomach,Infomach,Infomach')
with st.sidebar.beta_expander("Clientes"):
    st.warning("Infomach não é selecionada por padrão")
    all_c = st.checkbox("Selecione todos os clientes",value=True)
    container = st.beta_container()
    if all_c:
        label_to_filter2 = container.multiselect("Selecione os clientes",
            clientes,default_clientes)
    else:
        label_to_filter2 =  container.multiselect("Selecione os clientes",
            clientes)

equipes = df['ownerteam'].unique().tolist()
for cont, eq in enumerate(equipes):
    if not(isinstance(eq, str)):
        del(equipes[cont])
equipes = sorted(equipes)
# ss1 = SessionState.get(x=equipes)
with st.sidebar.beta_expander("Equipes"):
    all_e = st.checkbox("Selecione todas as equipes",value=True)
    container1 = st.beta_container()
    if all_e:
        label_to_filter3 = container1.multiselect("Selecione as equipes",
            equipes,equipes)
    else:
        label_to_filter3 =  container1.multiselect("Selecione as equipes",
            equipes)

categorias = df['category'].unique().tolist()
with st.sidebar.beta_expander("Categorias"):
    all_cat = st.checkbox("Selecione todas as categorias",value=True)
    container2 = st.beta_container()
    if all_cat:
        label_to_filter4 = container2.multiselect("Selecione as categorias",
            categorias,categorias)
    else:
        label_to_filter4 =  container2.multiselect("Selecione as categorias",
            categorias)

filtered_df = df[(df[DATE_COLUMN] >= pd.to_datetime(start_date)) & (df[DATE_COLUMN] <= pd.to_datetime(end_date)) & (df['tipo de hora'].isin(label_to_filter)) & (df['clientes'].isin(label_to_filter2)) & (df['ownerteam'].isin(label_to_filter3)) & (df['category'].isin(label_to_filter4))]

### Atualiza placeholder
info_sidebar.info("Foram carregados {} registros".format(filtered_df.shape[0]))

### Tela Principal
st.header("Indicadores do Movidesk")

if exibir_tabela:
    cols_export = st.beta_columns(4)    
    try:
        csv = filtered_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        linko= f'<a href="data:file/csv;base64,{b64}" download="relatorio.csv">Download csv file</a>'
        cols_export[2].markdown(linko, unsafe_allow_html=True)
    except:
        cols_export[2].warning("Erro")

    try:
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        xlsx = filtered_df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        xlsx = output.getvalue()
        b64a = base64.b64encode(xlsx).decode('UTF-8')  # some strings
        
        linkou= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64a}" download="relatorio.xlsx">Download excel file</a>'
        cols_export[3].markdown(linkou, unsafe_allow_html=True)
    except:
        cols_export[3].warning("Erro")


    st.write(filtered_df)

if filtered_df.empty:
    st.warning("Os filtros não retornam resultados")
    if not label_to_filter2:
        st.warning("Selecione pelo menos um cliente")
    elif not label_to_filter:
        st.warning("Selecione pelo menos um tipo de hora")
    elif not label_to_filter3:
        st.warning("Selecione pelo menos uma equipe")
    elif not label_to_filter4:
        st.warning("Selecione pelo menos uma categoria")
else:

    ### Elabora gráfico soma de horas
    horas_cliente = filtered_df.groupby('clientes').apply(lambda x: (x['hours']).sum())


    tmp = filtered_df['clientes'].map(horas_cliente)
    horas_cliente_df = []
    for row_index, row in enumerate(horas_cliente.axes[0]):
        horas_cliente_df.append([row, horas_cliente[row_index]])

    horas_cliente_df = pd.DataFrame(np.array(horas_cliente_df), columns = ['clientes', 'horas'])
    horas_cliente_df['horas'] = horas_cliente_df['horas'].astype(float)
    horas_cliente_df = horas_cliente_df.sort_values('horas',ascending=False).head(10)
    width_cliente = 700
    height_cliente = 400
    with st.beta_expander("Horas/Cliente"):
        width_cliente = st.number_input('Largura', value=width_cliente)
        height_cliente = st.number_input('Altura', value=height_cliente)
    hours_cliente_char = alt.Chart(horas_cliente_df).transform_fold(
    ['horas'],
    as_=['column', 'horas']
    ).mark_bar().encode(
    x='horas:Q',
    y=alt.Y('clientes:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum'))
    ).properties(
        width=width_cliente,
        height=height_cliente
    )
    st.altair_chart(hours_cliente_char)

    ### Elabora gráfico horas por equipe
    horas_equipe = filtered_df.groupby('ownerteam').apply(lambda x: (x['hours']).sum())
    tmp = filtered_df['ownerteam'].map(horas_equipe)
    horas_equipe_df = []

    for row_index, row in enumerate(horas_equipe.axes[0]):
        horas_equipe_df.append([row, horas_equipe[row_index]])

    horas_equipe_df = pd.DataFrame(np.array(horas_equipe_df), columns = ['ownerteam', 'horas'])
    horas_equipe_df['horas'] = horas_equipe_df['horas'].astype(float)
    horas_equipe_df = horas_equipe_df.sort_values('horas',ascending=False).head(10)
    width_equipe = 700
    height_equipe = 400
    with st.beta_expander("Horas/Equipe"):
        width_equipe = st.number_input('Largura Eq.', value=width_equipe)
        height_equipe = st.number_input('Altura Eq.', value=height_equipe)
    hours_equipe_char = alt.Chart(horas_equipe_df).transform_fold(
    ['horas'],
    as_=['column', 'horas']
    ).mark_bar().encode(
    x='horas:Q',
    y=alt.Y('ownerteam:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum'))
    ).properties(
        width=width_equipe,
        height=height_equipe
    )
    st.altair_chart(hours_equipe_char)



    ### Elabora gráfico horas por categoria
    horas_categoria = filtered_df.groupby('category').apply(lambda x: (x['hours']).sum())
    tmp = filtered_df['category'].map(horas_categoria)
    horas_categoria_df = []

    for row_index, row in enumerate(horas_categoria.axes[0]):
        horas_categoria_df.append([row, horas_categoria[row_index]])

    horas_categoria_df = pd.DataFrame(np.array(horas_categoria_df), columns = ['category', 'horas'])
    horas_categoria_df['horas'] = horas_categoria_df['horas'].astype(float)
    horas_categoria_df = horas_categoria_df.sort_values('horas',ascending=False).head(10)
    width_categoria = 700
    height_categoria = 400
    with st.beta_expander("Horas/Categoria"):
        width_categoria = st.number_input('Largura Cat.', value=width_categoria)
        height_categoria = st.number_input('Altura Cat.', value=height_categoria)
    hours_categoria_char = alt.Chart(horas_categoria_df).transform_fold(
    ['horas'],
    as_=['column', 'horas']
    ).mark_bar().encode(
    x='horas:Q',
    y=alt.Y('category:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum'))
    ).properties(
        width=width_categoria,
        height=height_categoria
    )
    st.altair_chart(hours_categoria_char)
    
    st.header("Percentual geral de chamados")

    ### Ferramentas de Layout e Gráficos de percentual
    # st.beta_container ### <- Layout
    cols = st.beta_columns(4)
    cols[0].subheader("Aguardando")
    # cols[1].subheader("Fechados")
    cols[1].subheader("Em Atendimento")
    cols[2].subheader("Novo")
    cols[3].subheader("Fila do Operador")

    cols2 = st.beta_columns(4)
    cols2[0].subheader("Agendamento")
    # cols[1].subheader("Fechados")
    cols2[1].subheader("Fechados")
    cols2[2].subheader("Resolvido")
    cols2[3].subheader("Cancelado")

    cont_aguardando = 0
    cont_fechados = 0
    cont_atendimento = 0
    cont_novos = 0
    cont_fila = 0
    cont_fechados = 0
    cont_agendamento = 0
    cont_resolvidos = 0
    cont_cancelados = 0
    for r in filtered_df['status']:
        if (r == 'Em atendimento'):
            cont_atendimento += 1
        elif (r == 'Aguardando'):
            cont_aguardando += 1
        elif (r == 'Fechado'): 
            cont_fechados += 1
        elif (r == 'Novo'):
            cont_novos += 1
        elif (r == 'Fila Operador'): 
            cont_fila += 1
        elif (r == 'Agendamento'):
            cont_agendamento += 1
        elif (r == 'Resolvido'): 
            cont_resolvidos += 1
        elif (r == 'Cancelados'):
            cont_cancelados += 1
    
    str_aguardando = "{} %".format(round(cont_aguardando/len(filtered_df)*100, 2))
    str_atendimento = "{} %".format(round(cont_atendimento/len(filtered_df)*100, 2))
    str_novos = "{} %".format(round(cont_novos/len(filtered_df)*100, 2))
    str_fila = "{} %".format(round(cont_fila/len(filtered_df)*100, 2))
    str_agendamento = "{} %".format(round(cont_agendamento/len(filtered_df)*100, 2))
    str_fechados = "{} %".format(round(cont_fechados/len(filtered_df)*100, 2))
    str_resolvidos = "{} %".format(round(cont_resolvidos/len(filtered_df)*100, 2))
    str_cancelados = "{} %".format(round(cont_cancelados/len(filtered_df)*100, 2))
    cols[0].subheader(str_aguardando)
    cols[1].subheader(str_atendimento)
    cols[2].subheader(str_novos)
    cols[3].subheader(str_fila)

    cols[0].title("")
    cols[1].title("")
    cols[2].title("")
    cols[3].title("")

    cols2[0].subheader(str_agendamento)
    cols2[1].subheader(str_fechados)
    cols2[2].subheader(str_resolvidos)
    cols2[3].subheader(str_cancelados)

    st.title("")
    st.title("")

    st.markdown("""
    Painel de indicadores de **chamados** da Infomach. Qualquer dúvida, entre em contato através do e-mail **newton.miotto@infomach.com.br**
    """)


    