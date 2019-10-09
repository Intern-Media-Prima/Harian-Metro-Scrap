from urllib.parse import urlencode
from urllib.request import HTTPHandler, Request, urlopen, build_opener
from urllib.error import URLError
from bs4 import BeautifulSoup as bs
import json

from mysql.connector import connect as mysql_connect
from mysql.connector.errors import IntegrityError

from utils import map, filter, reduce, has_key, get_key, text_match, is_text_not_empty, find_matches

def open_url(url, headers={}, encoding='utf-8', max_retry=-1):
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
	while True:
		try: return urlopen(Request(url, headers=headers)).read().decode(encoding)
		except URLError: print('Connection error! Retrying "{}"...'.format(url))
		if max_retry != -1 and retry > max_retry: raise Exception('Max retry limit reached trying to connect "{}"! {}'.format(url, max_retry))

def open_soup(url, headers={}, encoding='utf-8'):
	return bs(open_url(url, headers=headers, encoding=encoding), 'html.parser')

def is_part_of_article(text):
	return is_text_not_empty()(text) and not text_match(r'^Berita berkaitan:$')(text)

def get_article(soup):
	attribs = { 'class': 'field-item even', 'property': 'content:encoded' }
	return '\n\n'.join(filter(map(soup.find('div', attribs).find_all('p'), lambda x : x.text), is_part_of_article))

def get_article_urls(query='', page=0):
	yielded = []
	url = 'https://www.hmetro.com.my/search?s={}{}'.format(query, '' if page == 0 or not isinstance(page, int) else '&page={}'.format(page))
	for url in filter(map(filter(open_soup(url).find_all('a'), has_key('href')), get_key('href')), text_match(r'^/.+?/\d{4}/\d{2}/\d{6}/.+$')):
		url = 'https://www.hmetro.com.my{}'.format(url)
		if url in yielded: continue
		yielded.append(url)
		yield page, url, get_article(open_soup(url))

def scrap(page=0):
	while True:
		yield from get_article_urls(page=page)
		page += 1

def try_cast(item, func):
	try: return func(item)
	except Exception: return item

CATEGORIES = ['utama','mutakhir','global','arena','rap','bisnes','metrotv','belanjawan2020']
CATEGORY_TO_ID = {}
ID_TO_CATEGORY = {}
for i in range(len(CATEGORIES)):
	CATEGORY_TO_ID[CATEGORIES[i]] = i+1
	ID_TO_CATEGORY[i+1] = CATEGORIES[i]

def get_category_by_id(id): 
	try: return ID_TO_CATEGORY[id]
	except KeyError: pass
def get_id_by_category(category): 
	try: return CATEGORY_TO_ID[category]
	except KeyError: pass

def insert_into(conn, sql, *values):
	cursor = conn.cursor()
	try:
		cursor.execute(
			sql, 
			(values)
		)
		conn.commit()
		print('Got url "{}" from page {}'.format(url, page))
	except IntegrityError as e: 
		code, message = str(e).split(': ')
		if code == '1062 (23000)': print('Skipping page {} url: {}'.format(page, url))
		else: print(e, 'Category: {}, CategoryID: {}'.format(c, cid))

def http_request(url, method='GET', headers={}, **post_fields):
	# post_data = urlencode(post_fields).encode("utf-8")
	post_data = '\n'.join([
		'------WebKitFormBoundaryjGaKlNg6H5LcF3V4',
		'Content-Disposition: form-data; name="file"; filename="test.txt"',
		'Content-Type: text/plain',
		'',
		'{text}',
		'------WebKitFormBoundaryjGaKlNg6H5LcF3V4--'
	]).format(**post_fields).encode('utf-8')
	print(post_data)
	return urlopen(Request(url, headers=headers, data=post_data)).read().decode('utf-8')

from sys import exit
def post_data(url, **post_vars):
	return http_request(url=url, method='POST', headers={'Content-Type': 'application/json'}, **post_vars)

if __name__ == '__main__':
	try:
		with open('latest_page.log', 'r') as file: latest_page = int(file.read())
	except: latest_page = 0 # 23

	with open('dbconfig.json', 'r') as file:
		config = json.loads(file.read())
	conn = mysql_connect(**config)

	for page, url, article in scrap(page=latest_page):
		# utama/2019/10/505232/datuk-red-enggan-cerai-adira
		match = find_matches(r'^https://www\.hmetro\.com\.my/(.+?)/(\d{4})/(\d{2})/(\d+?)/(.+)$', url)
		c, y, m, id, title = map(range(1, 6), lambda x : try_cast(match.group(x), int))
		cid = get_id_by_category(c)
		
		with open('article.txt', 'a', encoding='utf-8') as file:
			file.write('{}\n\n'.format(article))

		print('Got article from page {}: {}'.format(page, url))

		# ID, category_id, year, month, title, content
		# insert_into(
		# 	conn,
		# 	'INSERT INTO article (ID,category_id,year,month,title,content) VALUES (%s, %s, %s, %s, %s, %s)',
		# 	id, cid, y, m, title, article
		# )
		
		last_page = page



	if last_page and isinstance(last_page, int):
		with open('latest_page.log', 'w') as file: file.write(last_page)