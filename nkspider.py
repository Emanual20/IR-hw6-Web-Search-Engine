# Author: Emanual
# Date: 20201208
import requests
import bs4

fo = open("temp.txt","w")

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
            fo.write(str1+'\n')