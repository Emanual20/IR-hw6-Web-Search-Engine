import pickle as pkl

url_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_id.dict"
url_list_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_list.dict"
id_pagerank_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\id_pagerank.dict"
MAX_RECOMMEND_NUM = 5


def RecommendManager(urlidlist):
    f = open(url_list_DICT_PATH, "rb")
    url_list_dic = pkl.load(f)

    f = open(id_pagerank_DICT_PATH, "rb")
    id_pagerank_dic = pkl.load(f)

    f = open(url_id_DICT_PATH, "rb")
    url_id_dic = pkl.load(f)

    pgurlidlist = []

    for urlid in urlidlist:
        for item in url_list_dic[urlid]:
            pgurlidlist.append(item)
    pgurlidlist = list(set(pgurlidlist))

    urlid_pgranklist = []

    for pgurlid in pgurlidlist:
        urlid_pgranklist.append([pgurlid, id_pagerank_dic[pgurlid]])

    urlid_pgranklist.sort(key=lambda x: (x[1], x[0]), reverse=True)

    print("maybe you also wanna acknowledge there sites..")
    for i in range(1, min(MAX_RECOMMEND_NUM, len(urlid_pgranklist)) + 1):
        print("Related", str(i), ": ", url_id_dic[urlid_pgranklist[i][0]])