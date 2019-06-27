import requests
# import pandas as pd
# from datetime import date

oscn_url = 'http://www.oscn.net/dockets/GetCaseInformation.aspx?db=oklahoma&number=PO-{0}-{1}'

years = [2015]

headers = {'user-agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}

po = 1
for year in years:
    good_request = True
    while(good_request):
        resp = requests.get(oscn_url.format(year, po), headers=headers)
        if('Something went wrong' not in resp.text and resp.ok):
            r_text = resp.text
            r_text = r_text.replace('\t', ' ')
            r_text = r_text.replace('<br>', ' ')
            r_text = r_text.replace('</ br>', ' ')
            r_text = r_text.replace('</br>', ' ')
            r_text = r_text.replace('<br/>', ' ')
            r_text = r_text.replace('<br />', ' ')
            r_text = r_text.replace('&nbsp;', ' ')
            f = open(f'{year}_{po}.txt', 'w')
            f.write(r_text)
            f.close()
            po += 1
        else:
            good_request = False
            po = 1
