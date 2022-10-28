import pandas as pd

class Filter:

    def __init__(self, df, fields_to_hide, key, is_sorted):
        
        self.fields = df[key].unique().tolist() # Valores únicos
        # Verifica se existem campos nulos e deleta-os
        for cont, eq in enumerate(self.fields):
            if not(isinstance(eq, str)):
                del(self.fields[cont])
        if is_sorted:
            self.fields = sorted(self.fields)
        self.default_fields = self.fields.copy()
        
        
        for f in fields_to_hide:
            if f in self.default_fields:
                self.default_fields.remove(f)

    def get(self):
        return self.label_to_filter

    def build_filter(self, st, name, warning = ""):
        with st.sidebar.beta_expander(name):
            if not (warning == ""):
                st.warning(warning)
            all_fields = st.checkbox(f"Selecione todos os {name.lower()}", value=True)
            container = st.beta_container()
            if all_fields:
                self.label_to_filter = container.multiselect(f"Selecione os {name.lower()}",
                    self.fields, self.default_fields)
            else:
                self.label_to_filter =  container.multiselect(f"Selecione os {name.lower()}",
                    self.fields)
            
            