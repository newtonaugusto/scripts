import pandas as pd
import json 
import urllib3
from datetime import datetime, timedelta

class Request:

    def request_surveys(self):
        is_empty = False
        id = ""
        surveys = {'hasMore':False, 'items':[]}
        while not is_empty:        
            query = f"https://api.movidesk.com/public/v1/survey/responses?token=&startingAfter={id}"
            http = urllib3.PoolManager()
            response = http.request('GET', query)
            if response.status == 200:
                
                parcial_survey = json.loads(response.data.decode('utf-8'))
                if parcial_survey["items"] == []: 
                    is_empty = True
                else:                
                    id = parcial_survey["items"][-1]["id"]
                    print(id)
                    surveys["items"].extend(parcial_survey["items"])
        return surveys

class Survey:
    class Item:
        column = ("id", "question_id", "type", "client_id", "ticket_id", "response_data", "commentary", "value")
        def __init__(self, id, questionId, type , clientId, ticketId, responseDate, commentary, value, *args, **kwargs):
            self.id = id
            self.question_id = questionId
            self.type = type
            self.client_id = clientId
            self.ticket_id = ticketId
            self.response_data = responseDate
            self.commentary = commentary
            self.value = value

        def get(self):
            return (self.id, self.question_id, self.type, self.client_id, self.ticket_id, self.response_data, self.commentary, self.value)
        def __str__(self):
            return f"{self.id} {self.question_id} {self.response_data} {self.value}"
        def __repr__(self):
            return self.__str__()

    column = ("has_more")
    def __init__(self, hasMore, items, *args, **kwargs):
        self.has_more = hasMore
        self.items = [self.Item(**item) for item in items if item != [] or item is not None]

    def get(self):
        return [(self.has_more, *item.get()) for item in self.items]
    def __str__(self):
        return f"{self.has_more}"
    def __repr__(self):
        return self.__str__()

def main():
    URL_JSON = f"surveys-{datetime.today().day:02}-{datetime.today().month:02}-{datetime.today().year}.json"
    URL_CSV = f"surveys-{datetime.today().day:02}-{datetime.today().month:02}-{datetime.today().year}.csv"

    surveys = Request().request_surveys()
    with open(URL_JSON, "w") as f:
        f.write(json.dumps(surveys))
    
    
    file = open(URL_JSON, 'r', encoding="utf8")
    surveys_json = json.load(file)
    surveys = Survey(**surveys_json)

    dataframe = pd.DataFrame([item.get() for item in surveys.items], columns=surveys.items[0].column)
    dataframe = dataframe.query('type == 3')
    pd.DataFrame(dataframe).to_csv(URL_CSV, index=False, header=dataframe.columns, sep=';', encoding="utf-8")


if __name__ == "__main__":
    main()