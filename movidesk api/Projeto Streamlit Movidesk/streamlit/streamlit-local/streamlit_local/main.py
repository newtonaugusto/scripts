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
from modules import Intervalos 
from filter import Filter
from grafico import Grafico
from percent_status import Status

URL = r"C:\Users\newton.miotto\Documents\movidesk api\Projeto Streamlit Movidesk\streamlit\streamlit-local\streamlit_local\files\relatorio.csv"
URL_LOGIN = r"C:\Users\newton.miotto\Documents\movidesk api\Projeto Streamlit Movidesk\streamlit\streamlit-local\streamlit_local\files\arquivo.csv"
DATE_COLUMN = "reference_date"

# Função que converte o campo de soma de horas para string, utilizado para gerar etiquetas dos gráficos
# Recebe o dataframe e a linha como paramêtro
def tip_hours_str(df, row_index):
    hours = math.floor(df[row_index])
    minutes = (df[row_index]-int(df[row_index]))*60
    minutes = round(minutes)
    if minutes == 60:
        hours += 1
        minutes = 0
    return f'{hours}:{minutes:02}'

# A função cria uma coluna de horas no formato numérico que será usada na construção dos gráficos no altair
# Recebe o dataframe como parâmetro e retorna esse mesmo df com a coluna hours em decimal
def worktime_convert(df):
    workTime = []
    for t in pd.to_timedelta(df['worktime']):
        hours = (t.total_seconds()/3600)
        workTime.append(hours)

    df['hours'] = workTime
    return df

def time_to_str(df):
    tabela_worktime = []
    for t in df['hours']:
        hours = int(t)
        minutes = (t - hours) * 60
        minutes = round(minutes)
        if minutes == 60:
            hours += 1
            minutes = 0
        tabela_worktime.append(f'{hours:02}:{minutes:02}:00')
    return tabela_worktime

# Função responsável por pegar as credenciais e comparar para realizar o login, o hash da senha foi gerado anteriormente
def login(user, password):
    encoded = jwt.encode({"password": password}, "YrxZx8enQ9hXNQkknBDqEBgErresakW75yH6P51jVz12j", algorithm="HS256")
    with open(URL_LOGIN,'r') as f:
        lines = f.readlines()
        if f'{user}:{encoded}' in lines[0]:
            return True
    return False   

# Carrega os dados para construção do dashboard
@st.cache 
def load_data(file_path = URL):
    df = pd.read_csv(file_path, delimiter=";")
    # Muda o nome das colunas para lowercase afim de evitar problemas
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    # Converte o respectivo campo para datetime
    df[DATE_COLUMN] = pd.to_datetime(df['periodstart']).dt.floor('d')
    df['periodstart'] = pd.to_datetime(df['periodstart'])
    df = worktime_convert(df)
    return df

def main():
    with st.sidebar.beta_expander("Login"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type='password')
    if st.sidebar.checkbox("Entrar"):
        # result = login(username, password)
        result = True # trocar quando subir no servidor
        if result:               
            # Carrega os dados e inicializa variáveis
            df = load_data()
            df = df.sort_values(by=[DATE_COLUMN])
            true_initial_movidesk_date = datetime.strptime("16/06/2020", '%d/%m/%Y')

            # Define as duas telas (Dashboard e Tabela)
            task = st.selectbox("Tarefas", ["Dashboard", "Tabela"])

            # Sidebar
            st.sidebar.header("Parâmetros")
            info_sidebar = st.sidebar.empty() ### Place holder, para o filtro que acontecerá depois
                      
            with st.sidebar.beta_expander("Filtros de data"):
                intervalos = Intervalos(st)
                intervalos.create_selectbox()
                # Filtros de data pré definidos
                start_date, end_date = intervalos.get(df=df)
                         
            # Cria o filtro de tipo de hora, com os campos default e warning
            tipo_hora_filter = Filter(df = df, fields_to_hide = "", key = 'worktypename', is_sorted = False)
            tipo_hora_filter.build_filter(st = st, name = "Tipo de Hora", warning = "Infomach não é selecionada por padrão")
            label_to_filter = tipo_hora_filter.get()

            # Cria o filtro de cliente, com os campos default e warning
            fields_to_hide = ['Infomach', 'Infomach - Comercial']
            clients_filter = Filter(df = df, fields_to_hide = fields_to_hide, key = 'business_name', is_sorted = True)
            clients_filter.build_filter(st = st, name = "Clientes", warning = "Infomach não é selecionada por padrão")
            clients_to_filter = clients_filter.get()
            
            # Cria o filtro de equipes, com os campos default e warning
            teams_filter = Filter(df = df, fields_to_hide = "", key = 'ownerteam', is_sorted = True)
            teams_filter.build_filter(st = st, name = "Equipes")
            teams_to_filter = teams_filter.get()

            # Cria o filtro de categorias, com os campos default e warning
            categories_filter = Filter(df = df, fields_to_hide = "", key = 'category', is_sorted = True)
            categories_filter.build_filter(st = st, name = "Categorias")
            categories_to_filter = categories_filter.get()

            filtered_df = df[(df[DATE_COLUMN] >= pd.to_datetime(start_date)) & (df[DATE_COLUMN] <= pd.to_datetime(end_date)) & (df['worktypename'].isin(label_to_filter)) & (df['business_name'].isin(clients_to_filter)) & (df['ownerteam'].isin(teams_to_filter)) & (df['category'].isin(categories_to_filter))]

            # Atualiza placeholder
            info_sidebar.info("Foram carregados {} registros".format(filtered_df.shape[0]))

            if task == "Dashboard":
                st.header("Indicadores do Movidesk")
                if filtered_df.empty:
                    st.warning("Os filtros não retornam resultados")
                    if not clients_to_filter:
                        st.warning("Selecione pelo menos um cliente")
                    elif not label_to_filter:
                        st.warning("Selecione pelo menos um tipo de hora")
                    elif not teams_to_filter:
                        st.warning("Selecione pelo menos uma equipe")
                    elif not categories_to_filter:
                        st.warning("Selecione pelo menos uma categoria")
                else:
                    # Elabora gráfico soma de horas por cliente
                    chart_horas_cliente = Grafico(filtered_df = filtered_df, key = 'business_name', name = "Cliente")
                    chart_horas_cliente.chart_generate(st=st)

                    # Elabora gráfico soma de horas por equipe
                    chart_horas_equipe = Grafico(filtered_df = filtered_df, key = 'ownerteam', name = "Equipe")
                    chart_horas_equipe.chart_generate(st=st)

                    # Elabora gráfico soma de horas por categoria
                    chart_horas_categoria = Grafico(filtered_df = filtered_df, key = 'category', name = "Categoria")
                    chart_horas_categoria.chart_generate(st = st)

                    st.header("Percentual geral de chamados")
                    
                    possibles_status = [ 'Aguardando', 'Em atendimento', 'Novo', 'Fila Operador', 'Agendamento', 'Fechado', 'Resolvido', 'Cancelado']
                    status = Status(df = filtered_df, status = possibles_status, st = st)
                    status.calculate_percent()
                    status.st_print_percent()

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
                    tabela_workTime = time_to_str(filtered_df)
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
                mensal_report_df['hours'] = round(mensal_report_df['hours'],2)
                
                # Converte coluna para timedelta
                workTime = time_to_str(mensal_report_df)
                mensal_report_df['hours'] = workTime

                try:
                    csv_mensal_report = mensal_report_df.reset_index().to_csv(index=False)
                    b64_mensal_report = base64.b64encode(csv_mensal_report.encode()).decode()  # some strings
                    link_mensal_report= f'<a href="data:file/csv;base64,{b64_mensal_report}" download="relatorio-mensal-{selected_month_to_report.strftime("%b")}{selected_month_to_report.year}.csv">Download csv file</a>'
                    cols_mensal_report[2].markdown(link_mensal_report, unsafe_allow_html=True)
                except:
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
                    cols_mensal_report[3].warning("Erro")

        else:
            st.warning("Senha e/ou Usuário incorretos!")
    
if __name__ == "__main__":
    main()