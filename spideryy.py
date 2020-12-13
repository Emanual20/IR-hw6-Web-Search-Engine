#encoding='utf-8'

import json
import os
import pickle as pkl
import re
import requests
from bs4 import BeautifulSoup
from utils import IdMap

base_url = 'http://cc.nankai.edu.cn'
cur = 'http://cc.nankai.edu.cn'
doc_id_map = IdMap.IdMap()    # doc to id
max_loop = 100
nxt = []
tot = 0
url_anc_map = {}    # url to anctext
url_id_map = IdMap.IdMap()     # url to id
url_list_map = {}   # page link info

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

if __name__ == "__main__":
    url_anc = open(os.path.join('spider', 'url_anc.txt'), 'w', encoding='utf-8')
    doc_url = open(os.path.join('spider', 'doc_url.txt'), 'w', encoding='utf-8')
    while max_loop > 0 or len(nxt) > 0:
        # fetch
        html = get_html(cur)
        if html == None:
            print("xxx fetch ", cur, " failed, drop")
            while True:
                cur = nxt[0]
                nxt.remove(cur)
                if re.search("nankai", cur) == None:
                    continue
                if not re.search("\.cn|\.com", cur) == None:
                    break
            continue
        real_url = html.url
        if re.search('nankai', real_url) == None:
            print("xxx wrong url ", real_url, ", drop")
            while True:
                cur = nxt[0]
                nxt.remove(cur)
                if re.search("nankai", cur) == None:
                    continue
                if not re.search("\.cn|\.com", cur) == None:
                    break
            continue
        # write
        if not re.search('\.doc|\.docx|\.zip|\.rar|\.ppt|\.pptx|\.xlsx|\.xls|\.jpg|\.png|\.pdf|\.md', real_url) == None \
            or re.search('file|download', real_url) != None:
            anc = url_anc_map.get(cur)
            if anc != None:
                print("+++ document ", real_url)
                if doc_id_map.__have__(real_url) == None:
                    docid = doc_id_map.__getitem__(real_url)
                    doc_url.write(anc + " " + str(docid) + "\n")
        else:
            # add cur url
            if url_id_map.__have__(cur) == None:
                url_id_map.__getitem__(cur)
            write_result(html)
            tot = tot + 1
            print('@', tot, ' ', cur, ': ', len(nxt))
        while True:
            cur = nxt[0]
            nxt.remove(cur)
            if re.search("nankai", cur) == None:
                continue
            if not re.search("\.cn|\.com", cur) == None:
                break
        base_url = cur[:re.search("\.cn|\.com", cur).span()[1]]
        if max_loop > 0:
            max_loop = max_loop - 1
        if tot == 20000:
            break
    doc_url.close()
    url_anc.close()
    # save pages link
    # print(url_list_map)
    doc = open(os.path.join('data_out', 'url_list.dict'), 'wb')
    pkl.dump(url_list_map, doc)
    doc.close()
    doc = open(os.path.join('data_out', 'url_id.dict'), 'wb')
    pkl.dump(url_id_map, doc)
    doc.close()
    doc = open(os.path.join('data_out', 'doc_id.dict'), 'wb')
    pkl.dump(doc_id_map, doc)
    doc.close()
    # print(url_list_map)
    print("FINISH")