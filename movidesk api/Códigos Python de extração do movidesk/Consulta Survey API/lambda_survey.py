import pandas as pd
import json 
import urllib3
from datetime import datetime, timedelta
import io
import boto3
import boto3.session
from codeguru_profiler_agent import with_lambda_profiler

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

def alert_error_sns(client, text, is_failed):
    # Se der erro manda publica mensagem no SNS
    if is_failed:
        response = client.publish(
            TopicArn="arn:aws:sns:us-east-2:686836150544:dados-movidesk-topic",
            Message=text,
            Subject='Erro de atualização',
        )
    else:
        response = client.publish(
            TopicArn="arn:aws:sns:us-east-2:686836150544:dados-movidesk-topic",
            Message=text,
            Subject='Sucesso na atualização.',
        )

@with_lambda_profiler(profiling_group_name="aws-lambda-dados-movidesk")
def lambda_handler(event, context):

    buffer_report = io.BytesIO()
    aws_region = "us-east-2"   
    s3 = boto3.client('s3', region_name=aws_region)

    sns = boto3.client('sns',   region_name=aws_region) 

    cont_attempts = 0
    while True:
        cont_attempts += 1
        buffer_report.seek(0)
        update_report(s3)
        is_failed = False
        if cont_attempts > 5:
            break

    if is_failed:
        alert_error_sns(sns, f"Erro ao dar load no relatório de surveys do Movidash. Dia de referencia: {datetime.today() - timedelta(days=1)}", is_failed)
    else:
        alert_error_sns(sns, f"Sucesso na atualização do relatório de surveys.. Dia de referencia: {datetime.today() - timedelta(days=1)}", is_failed)
    return 0

def update_report(s3):

    dayli_buffer = io.BytesIO()
    dayli_buffer.write(json.dumps(Request().request_surveys()).encode())
    dayli_buffer.seek(0)
    arquivo = json.load(dayli_buffer)
    dayli_buffer.close()
    surveys = Survey(**arquivo)
    csv_buffer = io.StringIO()
    dataframe = pd.DataFrame([item.get() for item in surveys.items], columns=surveys.items[0].column)
    dataframe = dataframe.query('type == 3')
    pd.DataFrame(dataframe).to_csv(csv_buffer, index=False, header=dataframe.columns, sep=';', encoding="utf-8")
    content = csv_buffer.getvalue()
    csv_buffer.close()
    s3.put_object(Bucket='dados.datalake.movidesk', Body=content, Key="ticket-surveys/surveys.csv")