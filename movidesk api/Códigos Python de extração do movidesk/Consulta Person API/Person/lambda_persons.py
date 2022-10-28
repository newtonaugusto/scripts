import pandas as pd
import json 
import urllib3
from datetime import datetime, timedelta
import io
import boto3
import boto3.session
from codeguru_profiler_agent import with_lambda_profiler

class Request:
    def __init__(self, number_of_items):
        self.number_of_items = number_of_items
        self.number_to_skip = 0

    def request_persons(self):
        is_empty = False      
        persons = []
        while not is_empty:
            query = f"https://api.movidesk.com/public/v1/persons?token=&$top={self.number_of_items}&$skip={self.number_to_skip}"
            http = urllib3.PoolManager()
            resposta = http.request('GET', query)
            parcial_persons = None
            if resposta.status == 200:
                parcial_persons = json.loads(resposta.data.decode('utf-8'))
                if parcial_persons != []:
                    persons.extend(parcial_persons)
                else:
                    is_empty = True
            self.number_to_skip += self.number_of_items
        return persons

class Persons:
    def __init__(self, objs):
        self.obj_list = [Person(**item) for item in objs]
        
    @classmethod
    def obj_list(self):
        return self.__persons

    def get(self):
        all_lines = []
        [all_lines.extend(item.get()) for item in self.obj_list]
        return all_lines 

class Person:
    class Address:
        column = ("address_type", "address_contry", "address_postal_code", "address_state", "addres_district", 
        "address_city", "address_street", "address_number", "address_complement",
        "address_reference", "address_is_default", "address_country_id")
        def __init__(self, addressType, country, postalCode, state, district, city, street, number, complement, reference, isDefault, countryId, *args, **kwargs):
            self.address_type = addressType
            self.address_contry = country
            self.address_postal_code = postalCode
            self.address_state = state
            self.address_district = district
            self.address_city = city
            self.address_street = street
            self.address_number = number
            self.address_complement = complement
            self.address_reference = reference
            self.address_is_default = isDefault
            self.country_id = countryId
        
        def get(self):
            return [(self.address_type, self.address_contry, self.address_postal_code, self.address_state,
            self.address_district, self.address_city, self.address_street, self.address_number, self.address_complement,
            self.address_reference, self.address_is_default, self.country_id)]

        def __str__(self):
            return f"{self.address_type} {self.address_contry} {self.address_postal_code} {self.address_state} {self.address_city} {self.address_district} {self.address_street} {self.address_number} {self.address_complement} {self.address_reference} {self.address_is_default}"

        def __repr__(self):
            return self.__str__()

    class Contact:
        column = ("contact_type", "contact", "contact_is_default")
        def __init__(self, contactType, contact, isDefault, *args, **kwargs):
            self.contact_type = contactType
            self.contact = contact
            self.contact_is_default = isDefault   
        
        def get(self):
            return [(self.contact_type, self.contact, self.contact_is_default)]
        
        def __str__(self):
            return f"{self.contact_type} {self.contact} {self.contact_is_default}"

        def __repr__(self):
            return self.__str__()

    class Email:
        column = ("email_type", "email", "email_is_default")
        def __init__(self, emailType, email, isDefault, *args, **kwargs):
            self.email_type = emailType
            self.email = email
            self.email_is_default = isDefault
        
        def get(self):
            return [(self.email_type, self.email, self.email_is_default)]

        def __str__(self):
            return f"{self.email}"

        def __repr__(self):
            return self.__str__()

    class Relationship:
        class Service:
            column = ("service_id", "service_name", "service_copy_to_children")
            def __init__(self, id, name, copyToChildren, *args, **kwargs):
                self.service_id = id
                self.service_name = name
                self.service_copy_to_children = copyToChildren

            def get(self):
                return [(self.service_id, self.service_name, self.service_copy_to_children)]
            
        column = ("relationship_id", "relationship_name", "relationship_sla_agreement", "relationship_force_children_to_have_some_agreement", 
        "relationship_allow_all_services", "relationship_include_in_parents", "relationship_load_child_organizations", 
        "relationship_id_to_delete", "relationship_is_get_method", *Service.column, )
        def __init__(self, id, name, slaAgreement, forceChildrenToHaveSomeAgreement, allowAllServices, includeInParents, loadChildOrganizations, services, idToDelete, isGetMethod, *args, **kwargs):
            self.id = id
            self.name = name
            self.sla_agreement = slaAgreement
            self.force_children_to_have_some_agreement = forceChildrenToHaveSomeAgreement
            self.allow_all_services = allowAllServices
            self.include_in_parents = includeInParents
            self.load_child_organizations = loadChildOrganizations
            self.services = [self.Service(**item) for item in services if item != [] or item is not None]
            self.id_to_delete = idToDelete
            self.is_get_method = isGetMethod

        def get(self):
            return [(self.id, self.name, self.sla_agreement, self.force_children_to_have_some_agreement, 
            self.allow_all_services, self.include_in_parents, self.load_child_organizations, 
            self.id_to_delete, self.is_get_method, 
            *service.get()) 
            for service in self.services]

        def __str__(self):
            return f"{self.id} {self.name}"

        def __repr__(self):
            return self.__str__()

    column = ("id", "code_reference_additional", "is_active", "person_type", "profile_type", 
    "access_profile", "business_name", "business_branch", "corporate_name", "cpf_cnpj", 
    "culture_id", "time_zone", "created_date", "created_by", "changed_date", 
    "changed_by", "observations", "cep", "state", "city", "contact", "email", "relationships")

    def __init__(self, id, codeReferenceAdditional, isActive, personType, profileType, accessProfile, businessName, businessBranch, corporateName, cpfCnpj, userName, password, role, bossId, bossName, classification, cultureId, timeZoneId, createdDate, createdBy, changedDate, changedBy, observations, authenticateOn, addresses, contacts, emails, teams, relationships, *args, **kwargs):
        self.id = id
        self.code_reference_additional = codeReferenceAdditional
        self.is_active = isActive
        self.person_type = personType
        self.profile_type = profileType
        self.access_profile = accessProfile
        self.business_name = businessName
        self.business_branch = businessBranch
        self.corporate_name = corporateName
        self.cpf_cnpj = cpfCnpj
        self.culture_id = cultureId
        self.time_zone = timeZoneId
        self.created_date = datetime.strptime(createdDate[0:18], "%Y-%m-%dT%H:%M:%S") if createdDate is not None else createdDate
        self.created_by = createdBy
        self.changed_date = datetime.strptime(changedDate[0:18], "%Y-%m-%dT%H:%M:%S") if changedDate is not None else changedDate
        self.changed_by = changedBy
        self.observations = observations
        self.addresses = [self.Address(**item) for item in addresses if item != [] or item is not None]
        if self.addresses != [] and self.addresses is not None:
            self.cep = self.addresses[0].address_postal_code 
            self.state = self.addresses[0].address_state
            self.city = self.addresses[0].address_city
        else:
            self.cep = ""
            self.state = ""
            self.city = ""

        self.contacts = [self.Contact(**item) for item in contacts if item != [] or item is not None]
        self.emails = [self.Email(**item) for item in emails if item != [] or item is not None]
        self.relationships = [self.Relationship(**item) for item in relationships if item != [] or item is not None]
        
    def __str__(self):
        return f"{self.id} {self.business_name} {self.cpf_cnpj}"

    def __repr__(self):
        return self.__str__()

    def get(self):

        return [(self.id, self.code_reference_additional, self.is_active, self.person_type, 
        self.profile_type, self.access_profile, self.business_name, self.business_branch, 
        self.corporate_name, self.cpf_cnpj, self.culture_id, self.time_zone, self.created_date, 
        self.created_by, self.changed_date, self.changed_by, self.observations, 
        self.cep, self.state, self.city, self.contacts, self.emails, self.relationships)]

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
        alert_error_sns(sns, f"Erro ao dar load no relatório de persons do Movidash. Dia de referencia: {datetime.today() - timedelta(days=1)}", is_failed)
    else:
        alert_error_sns(sns, f"Sucesso na atualização do relatório de persons.. Dia de referencia: {datetime.today() - timedelta(days=1)}", is_failed)
    return 0

def update_report(s3):
    
    dayli_buffer = io.BytesIO()
    dayli_buffer.write(json.dumps(Request(100).request_persons()).encode())
    dayli_buffer.seek(0)
    arquivo = json.load(dayli_buffer)
    dayli_buffer.close()
    persons = Persons(arquivo)
    dataframe = pd.DataFrame(persons.get(), columns=Person.column)
    dataframe = dataframe.query('person_type == 2')
    csv_buffer=io.StringIO()
    dataframe.to_csv(csv_buffer, index=False, header=dataframe.columns, sep=';', encoding="utf-8")
    content = csv_buffer.getvalue()
    csv_buffer.close()
    s3.put_object(Bucket='dados.datalake.movidesk', Body=content, Key="ticket-pessoas/persons.csv")