# OSCN
Django website for OSCN Protective Orders

## OSCN.py
Scrapes the OSCN website for protective orders given a year as a string. Uses the requests module to fetch the web pages.
Saves each page as a .txt file with of the form year_number_in_year.txt. For example, the first protective order of the year 2015 will be saved as 2015_1.txt

## data_soup.py
Reads previously saved webpages and using a combination of regex expressions and the BeautifulSoup module retrieves relevant information. Relevant information is saved into a python dictionary with keys such as 'case_details', 'attorneys', 'events', 'issues','disposition','dockets.' The dictionary is then saved as a serialized python object in a binary file of the form year_number_in_year.txt.p using the python pickle module.

## regex_to_model.py
Reads the previously serialized python dictionaries and saves their values to corresponding fields in the instances of ProtectiveOrder.models, such as: party, judge, attorney, event, issue, DocketEntry, ProtectiveOrder.

## ProtectiveOrders.models.py
Contains the Django models for data as found in the OSCN Protective Orders webpage.
