import requests
from bs4 import BeautifulSoup as bs
import json
import os

url = "https://www.bookbrahma.com/authors/"

base_url = "https://www.bookbrahma.com/"

json_file = "bookbrahma_authorlist.json"

author_list_area = "container"


page = 1

authors_path = []

def authors_exist(path, authors):
    try:
        resp = requests.get(path)
        html = bs(resp.content, 'html.parser')
        author_list = html.find('div', id=author_list_area)
        authors_cnt = author_list.findAll('a', class_="card-link")
        for author in authors_cnt:
            link = base_url + author['href'].replace('../', '')
            authors.append(link)
        return authors_cnt
    except:
        return False


while True:
    current_url = url+str(page)
    if not authors_exist(current_url, authors_path):
        print('**************** last page', page)
        break
        
    print("========== page %d completed ==========="%page)
    print("<<<< number of authors %d>>>>"%(len(authors_path)))
    page += 1
    
with open(json_file, 'w') as file:
    json.dump({'author_links': authors_path}, file, indent = 6)
