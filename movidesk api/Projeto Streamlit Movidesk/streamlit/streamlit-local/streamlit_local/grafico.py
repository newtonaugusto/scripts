import altair as alt
import math
import pandas as pd
import numpy as np

class Grafico:
    def __init__(self, filtered_df, key, name):
        self.key = key
        self.name = name
        
        hours = filtered_df.groupby(self.key).apply(lambda x: (x['hours']).sum(numeric_only = False))
        self.hours_df = []
        for row_index, row in enumerate(hours.axes[0]):
            self.hours_df.append([row, hours[row_index], self.tip_hours_str(hours, row_index)])

        self.hours_df = pd.DataFrame(np.array(self.hours_df), columns = [self.key, 'horas', 'total de horas'])
        self.hours_df['horas'] = self.hours_df['horas'].astype(float)
        self.hours_df = self.hours_df.sort_values('horas',ascending=False).head(10)

    def tip_hours_str(self, df, row_index):
        hours = math.floor(df[row_index])
        minutes = (df[row_index]-int(df[row_index]))*60
        minutes = round(minutes)
        if minutes == 60:
            hours += 1
            minutes = 0
        return f'{hours}:{minutes:02}'

    def chart_generate(self, st):
        width = 700
        height = 400
        with st.beta_expander(f"Horas/{self.name}"):
            width = st.number_input(f'Largura {self.name}', value=width)
            height = st.number_input(f'Altura {self.name}', value=height)
        hours_char = alt.Chart(self.hours_df).transform_fold(
        ['horas'],
        as_=['column', 'horas']
        ).mark_bar().encode(
        x='horas:Q',
        y=alt.Y(f'{self.key}:N',sort=alt.EncodingSortField(field='horas', order='descending', op='sum')),
        tooltip=['total de horas']
        ).properties(
            width=width,
            height=height
        )
        st.altair_chart(hours_char)