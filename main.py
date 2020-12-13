# Author: Emanual
# Date: 20201208

import sys
import nkspider
import prtest
import gencontentsvsm
import genarchorsvsm
import gentitlesvsm
import UserMod
import QueryMod
import CachedMod
import RecommendMod
import pickle as pkl
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT_URL = "https://www.nankai.edu.cn"
doc_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\doc_id.dict"
url_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_id.dict"
url_list_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_list.dict"
id_pagerank_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\id_pagerank.dict"
CONTENTS_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\contents_vectorizor.dict"
ANCHORS_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\anchors_vectorizor.dict"
TITLES_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\titles_vectorizor.dict"
NOW_USER_NICKNAME = " "

if __name__ == "__main__":
    print("Welcome Using Sakura's Search Engine \"NOTHING CAN YOU FOUND\"..!")
    # gen_pagerank
    # prtest.gen_pagerank()
    # fload = open(id_pagerank_DICT_PATH,"rb")
    # s = pkl.load(fload)
    # print(s)

    # generate vsm
    # gencontentsvsm.genvsm()
    # genarchorsvsm.genvsm()
    # gentitlesvsm.genvsm()

    # a simple query test
    # f = open(CONTENTS_TFIDF_VECTORIZOR_PATH,"rb")
    # tfidf_vectorizer = pkl.load(f)
    # tfidf_matrix = tfidf_vectorizer.fit_transform(mydoclist)
    # new_docs = ["你好 我 是 一个 计算机 学生"]
    # new_term_freq_matrix = tfidf_vectorizer.transform(new_docs)
    # print(tfidf_vectorizer.vocabulary_)
    # print(new_term_freq_matrix.todense())
    # dense = new_term_freq_matrix.todense().tolist()
    # for i in range(0,len(dense[0])):
    #     if dense[0][i] > 0 :
    #         print(i," ",dense[0][i])

    UserMod.InitUserModules()
    while 1:
        option = input("please choose continue or quit: (C/Q)")
        if "q" in option or "Q" in option:
            break
        while 1:
            option = input("please log your account or register a new account: (L/R)")
            if "l" in option or "L" in option:
                nickname = input("[LOGIN] please input your username:")
                password = input("[LOGIN] please input your account's password:")
                x = UserMod.LoginManager(nickname, password)
                if x == 1:
                    print("login successful..")
                    NOW_USER_NICKNAME = nickname
                    break
                else:
                    print("invalid nickname or password..")

            if "r" in option or "R" in option:
                nickname = input("[REGISTER] please input your username:")
                password = input("[REGISTER] please input your account's password:")
                x = UserMod.RegisterManager(nickname, password)
                if x == 1:
                    print("register successful..")
                else:
                    print("invalid nickname or password..")

        while 1:
            print("please input ur query option:")
            option = input("(1 for doc query,2 for url query,3 for web query,4 for user log,5 for exit)")
            if '1' in option:
                query = input("please input ur query:")
                QueryMod.doc_query(query)
                UserMod.QueryLogManager(NOW_USER_NICKNAME, query)
                continue
            elif '2' in option:
                query = input("please input ur query:")
                url_id_list = QueryMod.url_query(query)
                RecommendMod.RecommendManager(url_id_list)
                UserMod.QueryLogManager(NOW_USER_NICKNAME, query)
                while 1:
                    cache_opt = input("please input the number of the cache you wanna say:(0-9)")
                    if 'q' in cache_opt or 'Q' in cache_opt:
                        break
                    cache_opt = eval(cache_opt)
                    if 0 <= cache_opt <= 9:
                        print("http://localhost:1425")
                        CachedMod.display(url_id_list[cache_opt])
                    elif 'q' in cache_opt or 'Q' in cache_opt:
                        break
                    else:
                        print("invalid range..")

                continue
            elif '3' in option:
                query = input("please input ur query:")
                url_id_list = QueryMod.site_query(query, NOW_USER_NICKNAME)
                RecommendMod.RecommendManager(url_id_list)
                UserMod.QueryLogManager(NOW_USER_NICKNAME, query)
                while 1:
                    cache_opt = input("please input the number of the cache you wanna say:(0-9/q)")
                    if 'q' in cache_opt or 'Q' in cache_opt:
                        break
                    cache_opt = eval(cache_opt)
                    if 0 <= cache_opt <= 9:
                        print("http://localhost:1425")
                        CachedMod.display(url_id_list[cache_opt])
                    else:
                        print("invalid range..")

                continue
            elif '4' in option:
                display_num = input("please input log's display window size (maximum 20):")
                UserMod.DisplayLogManager(NOW_USER_NICKNAME, display_num)
                continue
            elif "5" in option:
                print("SEE YOU LATER!", NOW_USER_NICKNAME)
                break
            else:
                print("invalid option.. try again..")

    print("Wish to see u in Sakura's Search Engine \"NOTHING CAN YOU FOUND\" again..!")
