from bs4 import BeautifulSoup
import pickle
import os

directory_list = ['2015']


def string_stripper(text,replace_list):
    '''Removes unwanted characters in a string if they are present.
    
    Args:
        param1: text -- text string with possible unwanted characters
        param2: replace_list -- list of unwanted characters as strings
    Returns:
        returns a string with unwanted characters removed
    '''
    string_acc = text

    for repl in replace_list:
        while(repl in string_acc):
            string_acc = string_acc.replace(repl,' ')
    
    return string_acc

replace_list = ['\t,','\n','\xa0'] # use regular expression to replace multiple '\n' characters with 1. same with multiple spaces

for year in directory_list:
    os.chdir(year)

    po_list = os.listdir()

    for file in po_list:
        if( file.endswith('.p') or (file == '.DS_Store')):
            po_list.remove(file)

    for po in po_list:

        f = open(po)
        html_parser = 'html.parser'
        soup = BeautifulSoup(f,html_parser)
        f.close()

        string_acc = ''

        po_dictionary = dict()

        section_list = ['case_details','party','attorneys','events','issues','disposition','dockets']

        tables = soup.find_all('table')

        # case details
        po_dictionary['case_details'] = soup.find('table',attrs='caseStyle')

        # parties = soup.find('h2',attrs='section party')
        # parties can be obtained from case details 
        # po_dictionary['party'] = soup.find('h2',attrs='section party').next_sibling.next_sibling

        # attorneys
        po_dictionary['attorneys'] = soup.find('h2',attrs='section attorneys').next_sibling.next_sibling

        # events
        po_dictionary['events'] = soup.find('h2',attrs='section events').next_sibling.next_sibling

        # issues
        po_dictionary['issues'] = soup.find('h2',attrs='section issues').next_sibling.next_sibling.next_sibling.next_sibling

        # disposition
        po_dictionary['disposition'] = po_dictionary['issues'].next_sibling.next_sibling

        # dockets
        po_dictionary['dockets'] = soup.find('h2',attrs='section dockets').next_sibling.next_sibling

        # table1: no thead
        # table2: thead
        # table3: no thead
        # table4: thead
        # table5: thead

        def table_explorer(table,dictionary,section,theader=False):
            ''' '''
            # table_index = 1
            # for table in tables:
            if( table is None):
                pass
            else:
                table_headers = ''
                if(theader):
                    for th in table.find_all('th'):
                        for string in th.strings:
                            table_headers += string.strip()
                        table_headers += ';'
                    dictionary[section+'-header'] = table_headers[:-1]
                row_index = 1
                table_row_acc = '' # table row accumulator concatenates all table rows
                for table_row in table.find_all('tr'):
                    td_acc = ''
                    for td in table_row.find_all('td'):
                        for string in td.strings:
                            td_acc += string.strip()
                        td_acc += ';' # marks the end of table data tag
                    cleaned_string = string_stripper(td_acc,replace_list)
                    table_row_acc += cleaned_string # cleaned_string[:-1]
                    row_index += 1
                dictionary[section] = table_row_acc[:-1]
            # table_index += 1

        # case details
        table_explorer(po_dictionary['case_details'],po_dictionary,'case_details')
        # Attorneys
        table_explorer(po_dictionary['attorneys'],po_dictionary,'attorneys',theader=True)
        # Events
        table_explorer(po_dictionary['events'],po_dictionary,'events',theader=True)
        # Issues
        table_explorer(po_dictionary['issues'] ,po_dictionary,'issues')
        # Disposition
        table_explorer(po_dictionary['disposition'],po_dictionary,'disposition',theader=True)
        # Docket
        table_explorer(po_dictionary['dockets'],po_dictionary,'dockets',theader=True)

        p_file = open(po+'.p','wb')
        pickle.dump(po_dictionary,p_file)

    os.chdir('..')
''''
table header scrapper
table2_headers
for th in table2.find_all('th'):
    for string in th.strings:
        table2_headers += string.strip+';'

'''
# string_list = string_acc.split(';')

# while('' in string_list):
#     string_list.remove('')

# case_details = ' '.join(string_list)

# print(case_details)