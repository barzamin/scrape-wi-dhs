import requests
from lxml import html, etree
import sys
import json
from datetime import datetime

URL = 'https://www.dhs.wisconsin.gov/outbreaks/index.htm'

page = requests.get(URL)
with open(f"data/{datetime.now():%Y-%m-%d-%H:%M}.html", 'wb') as f:
	f.write(page.content)
doc = html.fromstring(page.content)

table_bulk = doc.xpath('//table[preceding-sibling::h5[contains(text(), "Wisconsin COVID-19 Test Results")]]')[0]
table_bycounty = doc.xpath('//table[preceding-sibling::h5[contains(text(), "Number of Positive Results by County")]]')[0]

def tab2arr(el):
	return [[etree.tostring(cell, method='text').decode().strip() for cell in row.xpath('(th|td)')] for row in el.xpath('tr')]

bulk_arr = tab2arr(table_bulk.find('tbody'))
bycounty_arr = tab2arr(table_bycounty.find('tbody'))

bulk_dat = {}
for label, count in bulk_arr:
	bulk_dat[label.lower()] = count

bycounty_dat = []
counties_total = 0
for county, count in bycounty_arr:
	count = int(count)
	if county == 'Total':
		counties_total = count

	community_spread = county.endswith('*')
	if community_spread:
		county = county[0:-1]

	bycounty_dat.append({
		'county': county,
		'community_spread': community_spread,
		'cases': count,
	})

with open(f"data/{datetime.now():%Y-%m-%d-%H:%M}.json", 'w') as f:
	json.dump({
		'bulk': bulk_dat,
		'counties': {
			'by_county': bycounty_dat,
			'total': counties_total,
		}	
	}, f, indent=2)
