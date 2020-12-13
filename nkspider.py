# Author: Emanual
# Date: 20201208
import requests
import bs4
import re
import os
from bs4 import BeautifulSoup
from utils import IdMap

fo = open("temp.txt", "w")
base_url = 'http://cc.nankai.edu.cn'
cur = 'http://cc.nankai.edu.cn'
doc_id_map = IdMap.IdMap()  # doc to id
max_loop = 100
nxt = []
tot = 0
url_anc_map = {}  # url to anctext
url_id_map = IdMap.IdMap()  # url to id
url_list_map = {}  # page link info


def get_html(url):
    # print("try to get: ", url)
    try:
        temp = requests.get(url, timeout=2)
        temp.encoding = 'utf-8'
    except:
        return None
    return temp


def write_result(html):
    soup = BeautifulSoup(html.text, 'lxml')
    addr = url_id_map.__getitem__(cur)
    # add code
    doc = open(os.path.join('data_dir', str(addr) + '.code'), 'w', encoding='utf-8')
    doc.write(html.text)
    doc.close()
    # url and anctext
    data = soup.select('a')
    pages = set()
    # url_anc.write("+++ now is : " + cur + "\n")
    for item in data:
        text = re.sub("[\r \n\t]", '', item.get_text())
        if text == None or text == '':
            continue
        url = item.get('href')
        if url == None or url == '' or re.search('java|void', url) != None:
            continue
        # add header
        if re.search('\.cn|\.com', url) == None:
            if re.match('http|https|www\.', url) == None:
                if re.match('\/', url) == None:
                    url = '/' + url
                url = base_url + url
        if not re.search('\.doc|\.docx|\.zip|\.rar|\.ppt|\.pptx|\.xlsx|\.xls|\.jpg|\.png|\.pdf|\.md', url) == None \
                or re.search('file|download', url) != None:
            if doc_id_map.__have__(url) == None:
                docid = doc_id_map.__getitem__(url)
                url_anc_map.setdefault(url, text)
                doc_url.write(text + " " + str(docid) + "\n")
            continue
        if url_id_map.__have__(url) == None:
            urlid = url_id_map.__getitem__(url)
            nxt.append(url)
            url_anc.write(text + " " + str(urlid) + "\n")
            url_anc_map.setdefault(url, text)
        urlid = url_id_map.__getitem__(url)
        pages.add(urlid)
    url_list_map.setdefault(url_id_map.__getitem__(cur), pages)
    # context
    doc = open(os.path.join('data_dir', str(addr) + '.info'), 'w', encoding='utf-8')
    data = soup.select('head')
    for item in data:
        text = re.sub('[\r \n\t]', '', item.get_text())
        if text == None or text == '':
            continue
        doc.write(text)
    data = soup.select('body')
    for item in data:
        text = re.sub('[\r \n\t]', '', item.get_text())
        if text == None or text == '':
            continue
        doc.write(text)
    doc.close()


def spider(s_url):
    print("spider in nkspider is called..")
    web_url = s_url
    r = requests.get(web_url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    f_list = []
    list_title = soup.find('title')
    print(list_title.text.encode('raw_unicode_escape').decode('utf-8'))
    list1 = soup.find_all('a')
    for item in list1:
        archor = item.text.encode('raw_unicode_escape').decode('utf-8')
        str1 = str(item.get('href').encode('utf-8'))
        if "nankai" in str1:
            f_list.append(str1)
            fo.write(archor)
            fo.write(str1 + '\n')
