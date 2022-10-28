from pyvidesk import Pyvidesk
from datetime import date, timedelta

tickets = Pyvidesk(token = "").tickets
tickets_properties = tickets.get_properties()
# my_query = (
#     tickets.query.filter(tickets_properties["actions"].timeAppointments.date >= date.today() - timedelta(days=31))
#     .expand(tickets_properties["clients"])
#     .select(tickets_properties["id"])
# )
# print(my_query.as_url())
print('break')

# for data in my_query:
#     print(data)

    # https://api.movidesk.com/public/v1/tickets?token=
    # &$select=id,subject,createdDate&$filter=createdDate ge 2021-03-01T00:00:00.00z and createdDate le 2021-03-31T00:00:00.00z
    # &$expand=clients($select=id, businessName),clients($expand=organization($select=id, businessName))
    # ,owner,actions($select=origin,id),actions($expand=timeAppointments($expand=createdBy))&$top=100