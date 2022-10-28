from datetime import datetime, timedelta, date

class Intervalos:
    DATE_COLUMN = "reference_date"
    def __init__(self, st):
        self.st = st

        self.dict_functions = {
            'Último Mês' : self.last_month,
            'Esse Mês' : self.this_month, 
            'Ontem' : self.yesterday, 
            'Últimos 7 dias' : self.last_week, 
            'Últimos 30 dias' : self.last_thirty_days, 
            'Digite o intervalo...' : self.user_selection}
    
    def create_selectbox(self):
        self.pre_filter = self.st.selectbox('Filtros pré-definidos', tuple(self.dict_functions.keys()))


    def last_month(self, *args, **kwargs):
        self.end_date = date.today().replace(day=1) - timedelta(days=1)
        self.start_date = self.end_date.replace(day=1)

    def this_month(self, *args, **kwargs):
        self.start_date = date.today().replace(day=1)
        self.end_date = date.today()

    def yesterday(self, *args, **kwargs):
        self.start_date = date.today() - timedelta(days=1)
        self.end_date = self.start_date

    def last_week(self, *args, **kwargs):
        self.start_date = date.today() - timedelta(days=7)
        self.end_date = date.today()

    def last_thirty_days(self, *args, **kwargs):
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today() 

    def user_selection(self, df, *args, **kwargs):
        self.last_month()
        start_date = self.start_date
        end_date = self.end_date

        self.start_date = self.st.date_input('Data de início', start_date, min_value=min(df[self.DATE_COLUMN]),max_value=max(df[self.DATE_COLUMN]))
        self.end_date = self.st.date_input('Data de fim', end_date, min_value=min(df[self.DATE_COLUMN]),max_value=max(df[self.DATE_COLUMN]))


    def get(self, *args, **kwargs):
        self.dict_functions[self.pre_filter](**kwargs)
        if self.start_date <= self.end_date:
            self.st.success("Intervalo: `%s` até `%s`" % (datetime.strftime(self.start_date,format='%d/%m/%Y'), datetime.strftime(self.end_date,format='%d/%m/%Y')))
        else:
            self.st.error('Erro: A data final deve ser maior/igual à data inicial.')

        return self.start_date, self.end_date