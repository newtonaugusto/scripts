import pandas as pd
import json 
import urllib3
from datetime import datetime, timedelta

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
        # for i, item in enumerate(self.obj_list):
        #     print(f"{i} item {item.get()}")
        #     # print(f"{i} item: {item.get()['id']}")
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

    # column = ("id", "code_reference_additional", "is_active", "person_type", "profile_type", 
    # "access_profile", "business_name", "business_branch", "corporate_name", "cpf_cnpj", 
    # "culture_id", "time_zone", "created_date", "created_by", "changed_date", 
    # "changed_by", "observations", "address", "contact", "email")
    column = ("id", "code_reference_additional", "is_active", "person_type", "profile_type", 
    "access_profile", "business_name", "business_branch", "corporate_name", "cpf_cnpj", 
    "culture_id", "time_zone", "created_date", "created_by", "changed_date", 
    "changed_by", "observations", "cep", "state", "city", "contact", "email", "relationships")
    #  *Address.column, *Contact.column, *Email.column, *Relationship.column
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
        # self.state = [item.address_state for item in self.addresses if item != [] or item is not None]
        # self.city = [item.address_city for item in self.addresses if item != [] or item is not None]
        
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
    # def get(self):
    #     return [(self.id, self.code_reference_additional, self.is_active, self.person_type, 
    #     self.profile_type, self.access_profile, self.business_name, self.business_branch, 
    #     self.corporate_name, self.cpf_cnpj, self.culture_id, self.time_zone, self.created_date, 
    #     self.created_by, self.changed_date, self.changed_by, self.observations, 
    #     *address.get(), *contact.get(), *email.get(), *relationship.get()) 
    #     for address in self.addresses for contact in self.contacts 
    #     for email in self.emails for relationship in self.relationships]

def main():

    URL_JSON = f"persons-{datetime.today().day:02}-{datetime.today().month:02}-{datetime.today().year}.json"
    persons = Request(100).request_persons()
    with open(URL_JSON, "w") as f:
        f.write(json.dumps(persons))


    URL_CSV = f"persons-{datetime.today().day:02}-{datetime.today().month:02}-{datetime.today().year}.csv"
    
    file = open(URL_JSON, 'r', encoding="utf8")
    persons_json = json.load(file)
    persons = Persons(persons_json)
    print(f"len: {len(persons.get())}")

    dataframe = pd.DataFrame(persons.get(), columns=Person.column)
    dataframe = dataframe.query('person_type == 2')
    pd.DataFrame(dataframe).to_csv(URL_CSV, index=False, header=dataframe.columns, sep=';', encoding="utf-8")

if __name__ == "__main__":
    main()