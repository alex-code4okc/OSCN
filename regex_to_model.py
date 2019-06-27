import re
import pickle
import os
import django
from datetime import datetime

date_format_string = "%m/%d/%Y"
docket_date_format = "%m-%d-%Y"

os.sys.path.append('/Users/Alex/Sites/OSCN/ProtectiveOrders/')
# script must be inside OSCN project folder
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OSCN.settings")

django.setup()

from ProtectiveOrders.models import party, judge, attorney, event, issue, DocketEntry, ProtectiveOrder

f = open('/Users/Alex/Desktop/Programming Projects/2019/2019_3.txt.p','rb')

po = pickle.load(f)
f.close()

protective_order = ProtectiveOrder()

case_details = po['case_details']

case_match = r"No. PO-\d{4}-\d{1,}"

po_number = re.findall(case_match,case_details)
if(po_number):
    protective_order.po_number = po_number[0].split('.')[1].strip()

date_match = r"\d{2}\/\d{2}\/\d{4}"

filed_on_match = r"Filed:\s{0,}\d{2}\/\d{2}\/\d{4}"
filed_date = re.findall(filed_on_match,case_details)
if(filed_date):
    filed = re.findall(date_match, filed_date[0])
    protective_order.filed_date = datetime.strptime(filed[0],date_format_string)

closed_on_match = r"Closed:\s{0,}\d{2}\/\d{2}\/\d{4}"
closed_date = re.findall(closed_on_match,case_details)
if(closed_date):
    closed = re.findall(date_match, closed_date[0])
    protective_order.closed_date = datetime.strptime(closed[0],date_format_string)

judge_match = r"Judge:\s{0,}\w{1,}"
new_judge = re.findall(judge_match,case_details)
if(new_judge):
    j = new_judge[0].split(':')[1].strip()
    n_judge = judge(name=j)
    n_judge.save()
    protective_order.judge = n_judge

plaintiff_match = r"[\w']{0,}[\w\s]{0,}\w{1,}[\w']{0,},\s{0,}Plaintiff"
plaintiffs = re.findall(plaintiff_match,case_details)

if(plaintiffs):
    if(len(plaintiffs)>1):
        children = True
    else:
        children = False
    p = plaintiffs[0].split(',')[0].strip()
    party_p = party(name=p,children=children,plaintiff=True,defendant=False)
    party_p.save()
    # assign a plaintiff using a query object (ensures object is already in the database)
    protective_order.plaintiffs.set(party.objects.filter(id__exact=party_p.id) )

defendant_match = r"[\w']{0,}[\w\s]{0,}\w{1,}[\w']{0,},\s{0,}Defendant"
defendant = re.findall(defendant_match,case_details)

if(defendant):
    d = defendant[0].split(',')[0].strip()
    party_d = party(name=d,children=False,plaintiff=False,defendant=True)
    party_d.save()
    protective_order.defendants.set( party.objects.filter(id__exact=party_d.id) )

attorney_data = ''
if(po['attorneys']):
    attorney_str, client = po['attorneys'][:-1].split(';') # accounting for last ';'
    first_paren = attorney_str.find('(')
    last_paren = attorney_str.find(')')
    laywer = attorney_str[:first_paren].strip()
    bar_number = attorney_str[first_paren+1:last_paren].split('#')[1].strip()
    address = attorney_str[last_paren+1:].strip()

    attorney_m = attorney(name=laywer,bar_number=bar_number,address=address)
    attorney_m.save()
    protective_order.save()
    # using a query set object
    protective_order.attorneys.set(attorney.objects.filter(id__exact=attorney_m.id))

    last_name, first_name = client.split(',')
    client_full_name = first_name.strip()+' '+last_name

    client_att_connection = party.objects.filter(name__exact = client_full_name)

    client_att_connection[0].attorney_str = attorney_m

    #client_att_connection.save()


event_list = ''
if(po['events']):
    event_list = po['events'][:-1].split(';')
    for e_index in range(0,len(event_list),4):
        e = event()
        e.event = event_list[e_index]
        e.party = event_list[e_index+1]
        e.docket = event_list[e_index+2]
        e.reporter = event_list[e_index+3]
        e.save()
        protective_order.save()
        # using add here prevents overriding of the other events added
        protective_order.events.add(e)

issues = ''
if(po['issues']):
    issues = po['issues'].split(';')

disposition = ''
if(po['disposition']):
    disposition = po['disposition'][1:-1].split(';')


clerks_office_match = r"Document Available at Court Clerk's Office"
dockets = ''
if(po['dockets']):
    dockets_list = po['dockets'][:-1].split(';')
    for d_index in range(0,len(dockets_list),6):
        d = DocketEntry()

        d.date = datetime.strptime(dockets_list[d_index],date_format_string)
        d.code = dockets_list[d_index+1]
        d.description = dockets_list[d_index+2]
        available_at_court = re.findall(clerks_office_match,dockets_list[d_index+2])
        if(available_at_court):
            d.available_at_court_clerk_office = True
        else:
            d.available_at_court_clerk_office = False
        d.count = dockets_list[d_index+3]
        party_docket = dockets_list[d_index+4]
        if(party_docket):
            last_name, first_name = party_docket.split(',')
            client_full_name = first_name.strip()+' '+last_name

            party_docket_connection = party.objects.filter(name__exact = client_full_name)

            if(party_docket_connection):
                d.party = party_docket_connection[0]
        dollar_amount = dockets_list[d_index+5]
        if(dollar_amount):
            d_amount = float(dollar_amount.split('$')[1].strip())
            d.amount = d_amount

        d.save()
        protective_order.save()
        protective_order.docket.add(d)