import requests
from bs4 import BeautifulSoup as bs
import json
from csv import writer
import re
import os

base_url = "https://www.bookbrahma.com/"

def clean_text(text):
    first_clean = text.replace(',','').replace(';', '')
    sec_clean = re.sub('\s+',' ', first_clean)
    if len(sec_clean)>1 and sec_clean[0] == " ":
        sec_clean = sec_clean[1:]
        
    if len(sec_clean)>1 and sec_clean[-1] == " ":
        sec_clean = sec_clean[:-1]
    
    return sec_clean

# author name and dob
def author_name_DOB(html):
    author_detail = html.find('div', class_="authorsNme")
    name = author_detail.find('h2')
    dob = author_detail.find('h3')
    
    if name:
        name = clean_text(name.text)
    else:
        dob = "" # name not exist return null
        
    if dob: 
        dob = clean_text(dob.text)
    else:
        dob = "" # dob not exist return null 
        
    return name, dob

# author description
def author_description(html):
    description = html.find('div', class_ = 'about_author')
    desc = ''
    p_tag = description.findAll('p')
    for p in p_tag:
        desc += p.text
        
    return clean_text(desc)


# download author book
def author_books(html):
    
    # author image url
    author_image = html.find('div', class_='author-book')
    author_image_url = base_url + author_image.find('img')['src'].replace('../', '')
    
    
    # books
    books_names = []
     
    eng_book_name = []
    # images
    images = []
    
    
    # no books written by the author if it raise exception
    try:
        owl_stage = html.find('div', id='book-by-author')
        books = owl_stage.findAll('div', class_='item')
        for book in books:
            book_name_in_english = book.find('a')['href']
        
            # book name in english
            book_eng = re.sub('.*/','', book_name_in_english)
            eng_book_name.append(book_eng)
        
            img = book.find('img')['src']
        
            # image src
            img_src = base_url + img.replace('../', '')
            images.append(img_src)
        
            book_name = book.find('p').text
            books_names.append(clean_text(book_name))
    except:
        # the books are not shown 
        pass
    
    return author_image_url, books_names, eng_book_name, images

# downlaod images
def download_images(name, img, books, book_img):
    # make path for each author
    try:
        os.mkdir(name)
        os.mkdir("%s/books"%name)
    except:
        print('already folder exists')
#     os.mkdir(name)
#     os.mkdir("%s/books"%name)
        
    # download author image
    with open("%s/%s.jpg"%(name, name), 'wb') as file:
        resp = requests.get(img)
        file.write(resp.content)
        
    # download books image
    for ind, url in enumerate(book_img):
        with open("%s/books/%s.png"%(name, books[ind]), 'wb') as file:
            resp = requests.get(url)
            file.write(resp.content)
            
    print("** images completed for %s **"%name)
    

# update in csv
def update_csv(auth, eng_auth, dob, desc, book_names, eng_book_names):
    csv_file = "info.csv"
    if not os.path.isfile(csv_file):
        li = ("author", "author(eng)", "DOB", "description", "book_names", "book_names(eng)")
        with open(csv_file, 'w') as f:
            obj = writer(f)
            obj.writerow(li)
 
    
    books = ";".join(book_names)
    eng_books = ";".join(eng_book_names)
    
    data = [auth, eng_auth, dob, desc, books, eng_books]
    

    with open(csv_file, 'a') as f:
        obj = writer(f)
        obj.writerow(data)
    
    
def scrape_site(link):
    
    resp = requests.get(link)
    html = bs(resp.content, 'html.parser')
    
    # author name and DOB stuff
    name, dob = author_name_DOB(html)
    
    
    # author description
    description = author_description(html)
    
    # books
    author_image, books_names, eng_book_name, images = author_books(html)
    
    # image download for author and book cover page
    
    ## another way to get english name author
    ## author_name_eng = re.sub('.*/|\(|\)|-{2,}?|[0-9]-[0-9]|[0-9]|[a-z]-$|-*[0-9]', '', link)
    author_name_eng = re.sub('.*/|.jpg', '', author_image)
    download_images(author_name_eng, author_image, eng_book_name, images)
    
    # print for debugging
    # print(author_name_eng, author_image, eng_book_name, images)
    
    # update in csv
    update_csv(name, author_name_eng, dob, description, books_names, eng_book_name)

def last_page(link):
    with open('last_visited.txt', 'w') as f:
        f.write(link)
        
    print("%%% last visited", link)
    

if __name__ == "__main__":

    # json load
    scraping_site = None
    with open('bookbrahma_authorlist.json') as file:
        scraping_site = json.load(file)
        
    # getting input to continue from failed one
    last_site = False
    check = str(input('Do you want to continue from last/failed one [y/n]: '))
    if check == 'y':
        last_site = str(input("enter last visited site: "))
        
    # scraping each site one by one
    all_links = scraping_site['author_links']
    
    for link in all_links:
        # checking for last book visited
        if last_site:
            if last_site == link:
                last_site = False
            else:
                continue
        
        # update last page
        last_page(link)
        
        # scraping the site
        scrape_site(link)
