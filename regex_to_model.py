import re
import pickle
import os
import django
from datetime import datetime

DELIMITER = '*;*'
date_format_string = "%m/%d/%Y"
docket_date_format = "%m-%d-%Y"

os.sys.path.append('/Users/Alex/Sites/OSCN/ProtectiveOrders/')
# script must be inside OSCN project folder
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OSCN.settings")

django.setup()

from ProtectiveOrders.models import party, judge, attorney, event, issue, DocketEntry, ProtectiveOrder

year_list = ['2015']

for year in year_list:
    os.chdir(year)

    # commented for testing
    # po_list = os.listdir()

    # po_list.remove('.DS_Store')
    # for file in po_list:
    #     if( file.endswith('.txt')):
    #         po_list.remove(file)
    
    # generate po_list starting at PO-15-1357
    po_list = []
    for po_generated in range(2993,2994):
        po_list.append('2015_'+str(po_generated)+'.txt.p')

    for po_order in po_list:
        f = open(po_order,'rb')
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
        
        protective_order.save()

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
        print(protective_order.po_number) #for debugging purposes. Need to know at which PO attorneys fails
        if(po['attorneys']):
            attorney_data = po['attorneys'].split(DELIMITER) # accounting for last extraneous '*;*'. This was done in data_soup.py
            # attorney_str, client = po['attorneys'][:-1].split('*;*') # accounting for last '*;*'
            attorney_data_length = len(attorney_data)
            attorneys, clients = [], []
            if(attorney_data_length>2):
                # two or more lawyers present
                # attorneys are found at index 0,2, etc (first, third etc)
                for index, value in enumerate(attorney_data):
                    if(index%2==0):
                        attorneys.append(value)
                    else:
                        clients.append(value)
            elif(attorney_data_length>0):
                # one or two lawyers present. Most likely always 1 lawyer.
                for index, value in enumerate(attorney_data):
                    if(index%2==0):
                        attorneys.append(value)
                    else:
                        clients.append(value)
            else:
                # None found. if po['attorneys'] is always None for 0 attorneys (should be) then this code is never reached.
                pass
            client_match_str = r"\w{1,}\s{0,}\w{0,},\s{1,}\w{1,}\s{0,}\w{0,}"
            matched_clients = []
            # matched clients contained a list of all match clients. 1 or greater
            for client in clients:
                if(client==''):
                    matched_clients.append('')
                else:
                    matched_clients = re.findall(client_match_str,clients[0])
            #attorneys and clients must match in a 1:1 ratio
            print(attorneys)
            print(matched_clients)
            for index in range(len(attorneys)): # Attorney_iter, Client_iter in attorneys,clients wasn't working removed
            # the following statements can me a method for creating attorneys and clients 
                if(attorneys[index].find('(') == -1):
                    # attorney does not have bar number and likely no address, just name
                    lawyer = attorneys[index] #assign the full string to laywer
                    bar_number = ''
                    address = ''
                else:
                    first_paren = attorneys[index].find('(') # should be a string
                    last_paren = attorneys[index].find(')')
                    laywer = attorneys[index][:first_paren].strip()
                    bar_number = attorneys[index][first_paren+1:last_paren].split('#')[1].strip()
                    address = attorneys[index][last_paren+1:].strip()

                attorney_m = attorney(name=laywer,bar_number=bar_number,address=address)
                attorney_m.save()
                protective_order.save()
                # using a query set object
                # change .set to .add inorder to avoid override (if object already present it gets overwritten)
                protective_order.attorneys.set(attorney.objects.filter(id__exact=attorney_m.id))

                # will need to use regular expressions to match the various clients
                try:
                    last_name, first_name = matched_clients[index].split(',')
                    client_full_name = first_name.strip()+' '+last_name.strip()
                    client_att_connection = party.objects.filter(name__exact = client_full_name)
                    client_att_connection[0].attorney_str = attorney_m
                #client_att_connection.save()
                except:
                    print('No Clients can be attached to attorney')


        event_list = ''
        if(po['events']):
            # event_list = po['events'][:-len(DELIMITER)].split(DELIMITER)
            event_list = po['events'].split(DELIMITER)
            for e_index in range(0,len(event_list),4):
                e = event()
                e.event = event_list[e_index+0]
                e.party = event_list[e_index+1]
                e.docket = event_list[e_index+2]
                e.reporter = event_list[e_index+3]
                e.save()
                protective_order.save()
                # using add here prevents overriding of the other events added
                protective_order.events.add(e)

        issues = ''
        if(po['issues']):
            issues = po['issues'].split(DELIMITER)

        disposition = ''
        if(po['disposition']):
            disposition = po['disposition'][len(DELIMITER):].split(DELIMITER)


        clerks_office_match = r"Document Available at Court Clerk's Office"
        dockets = ''
        if(po['dockets']):
            dockets_list = po['dockets'].split('*;*')
            for d_index in range(0,len(dockets_list),6):
                d = DocketEntry()
                print(dockets_list[d_index]) # for debugging
                d.date = datetime.strptime(dockets_list[d_index],docket_date_format)
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