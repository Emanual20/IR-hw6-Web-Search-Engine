# Author: Emanual
# Date: 20201208

import sys
import pickle as pkl
import networkx as nx
import matplotlib.pyplot as plt

ROOT_URL = "https://www.nankai.edu.cn"
doc_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\doc_id.dict"
url_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_id.dict"
url_list_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_list.dict"
id_pagerank_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\id_pagerank.dict"
URL_NUM = 23136
PGRANK_ADJUST_PARAM = 1e4


def gen_pagerank():
    f = open(url_list_DICT_PATH, 'rb')
    p = pkl.load(f)

    G = nx.DiGraph()
    for i in range(0, len(p)):
        if i > URL_NUM:
            break
        if i in p.keys():
            for j in p[i]:
                G.add_edge(i, j)
    print("add finish..")

    pr = nx.pagerank(G, alpha=0.85)
    prdic = {}
    for node, pageRankValue in pr.items():
        if node <= URL_NUM:
            prdic[node] = pageRankValue * PGRANK_ADJUST_PARAM
    print("calc pagerank finish..")

    fdump = open(id_pagerank_DICT_PATH, "wb")
    pkl.dump(prdic, fdump, 0)
    print("write into id_pagerank.dict finish..")

    # lis.sort(key=lambda x:(x[1],x[0]),reverse=True)
    # for i in range(0, len(lis)):
    #     print(lis[i][0], lis[i][1])
