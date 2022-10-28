from datetime import timedelta
class PercentStatus:

    def __init__(self):
        self.count = 0
        self.sum_hours = timedelta()
        self.percent = ""

    def sum(self, hours):
        self.count += 1
        self.sum_hours += hours

class Status:

    def __init__(self, df, status, st):
        self.status = {}
        self.status = self.status.fromkeys(status)
        for s in self.status.keys():
            self.status[s] = PercentStatus()
        self.df = df
        self.st = st
        self.total_hours = timedelta()

    def calculate_percent(self):
        error = False
        for index, r in self.df.iterrows():
            try:
                self.status[r['status']].sum_hours += timedelta(hours=r['hours'])
            except:
                error = True
        for s in self.status.keys():
            self.status[s].percent = "{} %".format(round(self.status[s].count/len(self.df)*100, 2))
            self.total_hours += self.status[s].sum_hours
        if error:
            self.st.warning("Erro: O status não está entre os valores possíveis.")

    def st_print_percent(self):
        cols_total = self.st.beta_columns(4)

        cols_total[0].subheader("**Total de horas:**")
        cols_total[0].subheader(f'{self.total_hours.days*24 + (self.total_hours.seconds//3600)} h {(self.total_hours.seconds//60)%60} min')
        cols_total[1].subheader("**Total de chamados:**")
        cols_total[1].subheader(f'{len(self.df["ticket_id"].value_counts())} chamados')
        self.st.header(" ")

        cols = self.st.beta_columns(4)
        for index, c in enumerate(cols):
            c.subheader(list(self.status.keys())[index])
            hours = list(self.status.values())[index].sum_hours
            percent = list(self.status.values())[index].percent
            c.subheader(f'{hours.days*24 + (hours.seconds//3600)} h {(hours.seconds//60)%60} min \n {percent}')

            # c.subheader(f'{self.status.values()[index].sum_hours.days*24 + (self.status.values()[index].sum_hours.seconds//3600)} h {(self.status.values()[index].sum_hours.seconds//60)%60} min \n {self.status.values()[index].percent}')
        
        for c in cols:
            c.title("")

        cols2 = self.st.beta_columns(4)
        for index, c in enumerate(cols2):
            c.subheader(list(self.status.keys())[index+4])
            hours = list(self.status.values())[index+4].sum_hours
            percent = list(self.status.values())[index+4].percent
            c.subheader(f'{hours.days*24 + (hours.seconds//3600)} h {(hours.seconds//60)%60} min \n {percent}')
     
        self.st.title("")
        self.st.title("")
            
        

    