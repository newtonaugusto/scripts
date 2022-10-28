import streamlit as st
import jwt
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import altair as alt
import matplotlib.pyplot as plt
import base64
from pandas import ExcelWriter
from pandas import ExcelFile
import io
import math
# import boto3
# import botocore
# import boto3.session
# from json import loads

# current_version = "1.0.6"

# conf_file = 'variables.json'
# with open(conf_file, 'r') as in_file:
#     conf = loads(in_file.read())
#     aws_access_key_id = conf.get('aws_access_key_id')
#     aws_secret_access_key = conf.get('aws_secret_access_key')
#     aws_region = conf.get('aws_region')    
# s3 = boto3.client('s3',
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
#     region_name=aws_region)
# s3.download_file('streamlitmovidesk', 'relatorio.csv', 'relatorio.csv') 
# s3.download_file('streamlitmovidesk', 'arquivo.csv', 'arquivo.csv')

URL = r"relatorio.csv"
# DATE_COLUMN = "periodstart"
DATE_COLUMN = "reference_date"

def tip_hours_str(df, row_index):
    hours = math.floor(df[row_index])
    minutes = (df[row_index]-int(df[row_index]))*60
    minutes = round(minutes)
    if minutes == 60:
        hours += 1
        minutes = 0
    return f'{hours}:{minutes:02}'

def login(user, password):
    # st.write("Cache Miss for n:",'hello')
    encoded = jwt.encode({"password": password}, "YrxZx8enQ9hXNQkknBDqEBgErresakW75yH6P51jVz12j", algorithm="HS256")
    with open("arquivo.csv",'r') as f:
        lines = f.readlines()
        if f'{user}:{encoded}' in lines[0]:
            return True
    return False   

# Carrega no cache
@st.cache 
def load_data(nrows):
    # Carrega todos os dados se '-1' ou o número de linhas
    if (nrows == -1):
        df = pd.read_csv(URL, delimiter=";")
    else:
        df = pd.read_csv(URL, delimiter=";", nrows=nrows)

    # Muda o nome das colunas para lowercase afim de evitar problemas
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    # Converte o respectivo campo para datetime
    df[DATE_COLUMN] = pd.to_datetime(df['periodstart']).dt.floor('d')
    df['periodstart'] = pd.to_datetime(df['periodstart'])

    # Converte coluna para timedelta
    workTime = []
    for t in pd.to_timedelta(df['worktime']):
        hours = (t.total_seconds()/3600)
        workTime.append(hours)

    df['hours'] = workTime
    
    return df

# df = load_data(-1)

def main():
    with st.sidebar.beta_expander("Login"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type='password')
    if st.sidebar.checkbox("Entrar"):
        result = login(username, password)
        if result:               
            # st.success("Logado como {}".format(username))
            # Carrega os dados
            df = load_data(-1)
            df = df.sort_values(by=[DATE_COLUMN])
            task = st.selectbox("Tarefas", ["Dashboard", "Tabela"])

            # Sidebar
            st.sidebar.header("Parâmetros")
            info_sidebar = st.sidebar.empty() ### Place holder, para o filtro que acontecerá depois
            # initial = datetime.strptime('01-03-2021', '%d-%m-%Y').date()
            # final = datetime.strptime('31-03-2021', '%d-%m-%Y').date()
            possible_end_date = max(df[DATE_COLUMN]).date()
            possible_initial_date = min(df[DATE_COLUMN]).date()            
            end_date = date.today().replace(day=1) - timedelta(seconds=1)
            start_date = end_date.replace(day=1)
            true_initial_movidesk_date = datetime.strptime("16/06/2020", '%d/%m/%Y')

            with st.sidebar.beta_expander("Filtros de data"):
                pre_filters = st.selectbox(
                    'Filtros pré-definidos',
                    ('Último Mês', 'Esse Mês', 'Ontem', 'Últimos 7 dias', 'Últimos 30 dias', 'Digite o intervalo...'))
                # Se no futuro aumentar a frequência dos dados, é possível adicionar o filtro 'hoje'
                
                # Filtros de data pré definidos
                if(pre_filters == 'Digite o intervalo...'):
                    start_date = st.date_input('Data de início', start_date,min_value=min(df[DATE_COLUMN]),max_value=max(df[DATE_COLUMN]))
                    end_date = st.date_input('Data de fim', end_date,min_value=min(df[DATE_COLUMN]),max_value=max(df[DATE_COLUMN]))
                    if start_date <= end_date:
                        st.sidebar.success('Sucesso! Intervalo: \n\n`%s` até `%s`' % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
                    else:
                        st.error('Erro: A data final deve ser maior/igual à data inicial.')
                elif(pre_filters == 'Último Mês'):
                    end_date = date.today().replace(day=1) - timedelta(days=1)
                    start_date = end_date.replace(day=1)
                    st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
                elif(pre_filters == 'Esse Mês'):
                    start_date = date.today().replace(day=1)
                    end_date = date.today()
                    st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(start_date,format='%d/%m/%Y'), datetime.strftime(end_date,format='%d/%m/%Y')))
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
    
            # Multiselect com os labels únicos
            labels = df['worktypename'].unique().tolist()
            with st.sidebar.beta_expander("Tipo de Hora"):
                label_to_filter = st.multiselect(
                    label="Escolha o tipo de hora",
                    options=labels,
                    default=["Normal","Extra"]
                )

            clientes = df['business_name'].unique().tolist()
            clientes = sorted(clientes)
            default_clientes = clientes.copy()
            default_clientes.remove('Infomach')
            default_clientes.remove('Infomach - Comercial')
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
            filtered_df = df[(df[DATE_COLUMN] >= pd.to_datetime(start_date)) & (df[DATE_COLUMN] <= pd.to_datetime(end_date)) & (df['worktypename'].isin(label_to_filter)) & (df['business_name'].isin(label_to_filter2)) & (df['ownerteam'].isin(label_to_filter3)) & (df['category'].isin(label_to_filter4))]

            # Atualiza placeholder
            info_sidebar.info("Foram carregados {} registros".format(filtered_df.shape[0]))

            if task == "Dashboard":
                st.header("Indicadores do Movidesk")
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
                    # Elabora gráfico soma de horas
                    horas_cliente = filtered_df.groupby('business_name').apply(lambda x: (x['hours']).sum())
                    horas_cliente_df = []
                    for row_index, row in enumerate(horas_cliente.axes[0]):
                        horas_cliente_df.append([row, horas_cliente[row_index], tip_hours_str(horas_cliente,row_index)])

                    horas_cliente_df = pd.DataFrame(np.array(horas_cliente_df), columns = ['business_name', 'horas', 'total_horas'])
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
                    y=alt.Y('business_name:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum')),
                    tooltip=['total_horas']
                    ).properties(
                        width=width_cliente,
                        height=height_cliente
                    )
                    st.altair_chart(hours_cliente_char)

                    # Elabora gráfico horas por equipe
                    horas_equipe = filtered_df.groupby('ownerteam').apply(lambda x: (x['hours']).sum())
                    horas_equipe_df = []

                    for row_index, row in enumerate(horas_equipe.axes[0]):
                        horas_equipe_df.append([row, horas_equipe[row_index], tip_hours_str(horas_equipe,row_index)])

                    horas_equipe_df = pd.DataFrame(np.array(horas_equipe_df), columns = ['ownerteam', 'horas', 'total_horas'])
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
                    y=alt.Y('ownerteam:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum')),
                    tooltip=['total_horas']
                    ).properties(
                        width=width_equipe,
                        height=height_equipe
                    )
                    st.altair_chart(hours_equipe_char)

                    # Elabora gráfico horas por categoria
                    horas_categoria = filtered_df.groupby('category').apply(lambda x: (x['hours']).sum())
                    horas_categoria_df = []

                    for row_index, row in enumerate(horas_categoria.axes[0]):
                        horas_categoria_df.append([row, horas_categoria[row_index], tip_hours_str(horas_categoria,row_index)])

                    horas_categoria_df = pd.DataFrame(np.array(horas_categoria_df), columns = ['category', 'horas', 'total_horas'])
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
                    y=alt.Y('category:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum')),
                    tooltip=['total_horas']
                    ).properties(
                        width=width_categoria,
                        height=height_categoria
                    )
                    st.altair_chart(hours_categoria_char)

                    st.header("Percentual geral de chamados")
                    
                    # Ferramentas de Layout e Gráficos de percentual
                    # st.beta_container ### <- Layout
                    

                    cont_aguardando = 0
                    hours_aguardando = timedelta()
                    cont_fechados = 0
                    hours_fechados = timedelta()
                    cont_atendimento = 0
                    hours_atendimento = timedelta()
                    cont_novos = 0
                    hours_novos = timedelta()
                    cont_fila = 0
                    hours_fila = timedelta()
                    cont_agendamento = 0
                    hours_agendamento = timedelta()
                    cont_resolvidos = 0
                    hours_resolvidos = timedelta()
                    cont_cancelados = 0
                    hours_cancelados = timedelta()

                    for index, r in filtered_df.iterrows():
                        if (r['status'] == 'Em atendimento'):
                            cont_atendimento += 1
                            hours_atendimento += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Aguardando'):
                            cont_aguardando += 1
                            hours_aguardando += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Fechado'): 
                            cont_fechados += 1
                            hours_fechados += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Novo'):
                            cont_novos += 1
                            hours_novos += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Fila Operador'): 
                            cont_fila += 1
                            hours_fila += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Agendamento'):
                            cont_agendamento += 1
                            hours_agendamento += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Resolvido'): 
                            cont_resolvidos += 1
                            hours_resolvidos += timedelta(hours=r['hours'])
                        elif (r['status'] == 'Cancelado'):
                            cont_cancelados += 1
                            hours_cancelados += timedelta(hours=r['hours'])

                    str_aguardando = "{} %".format(round(cont_aguardando/len(filtered_df)*100, 2))
                    str_atendimento = "{} %".format(round(cont_atendimento/len(filtered_df)*100, 2))
                    str_novos = "{} %".format(round(cont_novos/len(filtered_df)*100, 2))
                    str_fila = "{} %".format(round(cont_fila/len(filtered_df)*100, 2))
                    str_agendamento = "{} %".format(round(cont_agendamento/len(filtered_df)*100, 2))
                    str_fechados = "{} %".format(round(cont_fechados/len(filtered_df)*100, 2))
                    str_resolvidos = "{} %".format(round(cont_resolvidos/len(filtered_df)*100, 2))
                    str_cancelados = "{} %".format(round(cont_cancelados/len(filtered_df)*100, 2))

                    total_hours = hours_aguardando + hours_atendimento + hours_fechados + hours_novos + hours_fila + hours_agendamento + hours_resolvidos + hours_cancelados
                    
                    cols_total = st.beta_columns(4)

                    cols_total[0].subheader("**Total de horas:**")
                    cols_total[0].subheader(f'{total_hours.days*24 + (total_hours.seconds//3600)} h {(total_hours.seconds//60)%60} min')
                    cols_total[1].subheader("**Total de chamados:**")
                    cols_total[1].subheader(f'{len(filtered_df["ticket_id"].value_counts())} chamados')
                    st.header(" ")
                    
                    cols = st.beta_columns(4)
                    cols[0].subheader("Aguardando")
                    cols[1].subheader("Em Atendimento")
                    cols[2].subheader("Novo")
                    cols[3].subheader("Fila do Operador")

                    cols2 = st.beta_columns(4)
                    cols2[0].subheader("Agendamento")
                    cols2[1].subheader("Fechados")
                    cols2[2].subheader("Resolvido")
                    cols2[3].subheader("Cancelado")

                    cols[0].subheader(f'{hours_aguardando.days*24 + (hours_aguardando.seconds//3600)} h {(hours_aguardando.seconds//60)%60} min \n {str_aguardando}')
                    cols[1].subheader(f'{hours_atendimento.days*24 + (hours_atendimento.seconds//3600)} h {(hours_atendimento.seconds//60)%60} min \n {str_atendimento}')
                    cols[2].subheader(f'{hours_novos.days*24 + (hours_novos.seconds//3600)} h {(hours_novos.seconds//60)%60} min \n {str_novos}')
                    cols[3].subheader(f'{hours_fila.days*24 + (hours_fila.seconds//3600)} h {(hours_fila.seconds//60)%60} min \n {str_fila}')

                    cols2[0].subheader(f'{hours_agendamento.days*24 + (hours_agendamento.seconds//3600)} h {(hours_agendamento.seconds//60)%60} min \n {str_agendamento}')
                    cols2[1].subheader(f'{hours_fechados.days*24 + (hours_fechados.seconds//3600)} h {(hours_fechados.seconds//60)%60} min \n {str_fechados}')
                    cols2[2].subheader(f'{hours_resolvidos.days*24 + (hours_resolvidos.seconds//3600)} h {(hours_resolvidos.seconds//60)%60} min \n {str_resolvidos}')
                    cols2[3].subheader(f'{hours_cancelados.days*24 + (hours_cancelados.seconds//3600)} h {(hours_cancelados.seconds//60)%60} min \n {str_cancelados}')

                    st.title("")
                    st.title("")

                    st.markdown("""
                    Painel de indicadores de **chamados** da Infomach. Qualquer dúvida, entre em contato através do e-mail **newton.miotto@infomach.com.br**
                    """)
            elif task == "Tabela":
                # Checkbox da tabela
                tabela = st.sidebar.empty()
                exibir_tabela = False
                if st.checkbox("Exibir tabela completa?"):
                    exibir_tabela = True
                else:
                    exibir_tabela = False

                if exibir_tabela:
                    cols_export = st.beta_columns(4)	
                    tabela_df = filtered_df.drop(['hours','reference_date'], 1)
                    tabela_workTime = []
                    for t in filtered_df['hours']:
                        hours = int(t)
                        minutes = (t - hours) * 60
                        minutes = round(minutes)
                        if minutes == 60:
                            hours += 1
                            minutes = 0
                        tabela_workTime.append(f'{hours:02}:{minutes:02}:00')

                    tabela_df['worktime'] = tabela_workTime 
                    try:
                        csv = tabela_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()  # some strings
                        linko= f'<a href="data:file/csv;base64,{b64}" download="relatorio.csv">Download csv file</a>'
                        cols_export[2].markdown(linko, unsafe_allow_html=True)
                    except:
                        cols_export[2].warning("Erro")

                    try:
                        output = io.BytesIO()
                        writer = pd.ExcelWriter(output, engine='xlsxwriter')
                        xlsx = tabela_df.to_excel(writer, sheet_name='Sheet1')
                        writer.save()
                        xlsx = output.getvalue()
                        b64a = base64.b64encode(xlsx).decode('UTF-8')  # some strings
                        
                        linkou= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64a}" download="relatorio.xlsx">Download excel file</a>'
                        cols_export[3].markdown(linkou, unsafe_allow_html=True)
                    except:
                        cols_export[3].warning("Erro")

                    st.write(tabela_df)

                possible_months = []
                current_date_filtered_df = true_initial_movidesk_date.date().replace(day=2)
                end_date_filtered_df = date.today().replace(day=1)
                while current_date_filtered_df <= end_date_filtered_df:
                    possible_months.append(f'{current_date_filtered_df.strftime("%b")}/{current_date_filtered_df.year}') 
                    current_date_filtered_df += relativedelta(months=1) 
                
                
                st.header("Relatório Mensal")
                selected_month_to_report = st.selectbox("Selecione o mês de referênca", list(reversed(possible_months)))
                selected_month_to_report = datetime.strptime(selected_month_to_report, "%b/%Y")
                cols_mensal_report= st.beta_columns(4)
                selected_month_to_report = selected_month_to_report.replace(day=1)
                selected_month_to_report_end_day = selected_month_to_report + relativedelta(months=1) - timedelta(seconds=1)
                mensal_report_df = df[(df[DATE_COLUMN] >= selected_month_to_report) & (df[DATE_COLUMN] <= selected_month_to_report_end_day)]
                mensal_report_df = mensal_report_df[['business_name','hours']].groupby(['business_name']).sum()
                
                workTime = []
                for t in mensal_report_df['hours']:
                    hours = int(t)
                    minutes = (t - hours) * 60
                    minutes = round(minutes)
                    if minutes == 60:
                        hours += 1
                        minutes = 0
                    workTime.append(f'{hours:02}:{minutes:02}:00')

                mensal_report_df['hours'] = workTime
                
                try:
                    # csv_mensal_report = mensal_report_df.to_csv(index=False)
                    csv_mensal_report = mensal_report_df.reset_index().to_csv(index=False)
                    b64_mensal_report = base64.b64encode(csv_mensal_report.encode()).decode()  # some strings
                    link_mensal_report= f'<a href="data:file/csv;base64,{b64_mensal_report}" download="relatorio-mensal-{selected_month_to_report.strftime("%b")}{selected_month_to_report.year}.csv">Download csv file</a>'
                    cols_mensal_report[2].markdown(link_mensal_report, unsafe_allow_html=True)
                except:
                    csv_mensal_report = mensal_report_df.to_csv(index=False)
                    b64_mensal_report = base64.b64encode(csv_mensal_report.encode()).decode()  # some strings
                    link_mensal_report= f'<a href="data:file/csv;base64,{b64_mensal_report}" download="relatorio-mensal-{selected_month_to_report.strftime("%b")}{selected_month_to_report.year}.csv">Download csv file</a>'
                    cols_mensal_report[2].markdown(link_mensal_report, unsafe_allow_html=True)

                    cols_mensal_report[2].warning("Erro")

                try:
                    output_mensal_report = io.BytesIO()
                    writer_mensal_report = pd.ExcelWriter(output_mensal_report, engine='xlsxwriter')
                    xlsx = mensal_report_df.to_excel(writer_mensal_report, sheet_name='Sheet1')
                    writer_mensal_report.save()
                    xlsx = output_mensal_report.getvalue()
                    b64a_mensal_report = base64.b64encode(xlsx).decode('UTF-8')  # some strings
                    
                    linkou_mensal_report= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64a_mensal_report}" download="relatorio-mensal-{selected_month_to_report.strftime("%b")}{selected_month_to_report.year}.xlsx">Download excel file</a>'
                    cols_mensal_report[3].markdown(linkou_mensal_report, unsafe_allow_html=True)
                except:
                    output_mensal_report = io.BytesIO()
                    writer_mensal_report = pd.ExcelWriter(output_mensal_report, engine='xlsxwriter')
                    xlsx = mensal_report_df.to_excel(writer_mensal_report, sheet_name='Sheet1')
                    writer_mensal_report.save()
                    xlsx = output_mensal_report.getvalue()
                    b64a_mensal_report = base64.b64encode(xlsx).decode('UTF-8')  # some strings
                    
                    linkou_mensal_report= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64a_mensal_report}" download="relatorio-mensal-{selected_month_to_report.strftime("%b")}{selected_month_to_report.year}.xlsx">Download excel file</a>'
                    cols_mensal_report[3].markdown(linkou_mensal_report, unsafe_allow_html=True)

                    cols_mensal_report[3].warning("Erro")

        else:
            st.warning("Senha e/ou Usuário incorretos!")
    

if __name__ == "__main__":
    main()


