# -*- coding: utf-8 -*-
import requests

r = requests.get('http://127.0.0.1:8000/api/references/finance_category')
data = r.json()
print('Finance Categories from API:')
for item in data['data']:
    print('  code=' + item['code'].ljust(10) + ' name=' + item['name'])

print('\nArchive Status from API:')
r2 = requests.get('http://127.0.0.1:8000/api/references/archive_status')
data2 = r2.json()
for item in data2['data']:
    print('  code=' + item['code'].ljust(10) + ' name=' + item['name'])

print('\nDatabase records:')
r3 = requests.get('http://127.0.0.1:8000/finance_archive/get_all')
data3 = r3.json()
for item in data3[:2]:
    print('  category=' + item['category'].ljust(10) + ' status=' + item['archive_status'])
