import pickle as pkl
import jieba
import re
import numpy as np
from string import punctuation

doc_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\doc_id.dict"
url_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_id.dict"
url_list_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_list.dict"
CONTENTS_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\contents_vectorizor.dict"
ANCHORS_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\anchors_vectorizor.dict"
TITLES_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\titles_vectorizor.dict"
MAX_RECOMMEND_NUM = 10


def doc_query(query):
    f = open(TITLES_TFIDF_VECTORIZOR_PATH, "rb")
    tfidf_vectorizer, docidlist, docdense = pkl.load(f)

    query = re.sub(r"[{}、，。！？·【】）》；;《“”（-]+".format(punctuation), " ", query)
    query = query.lower()
    query_words = ' '.join(jieba.lcut_for_search(query))
    query = []
    query.append(query_words)

    new_term_freq_matrix = tfidf_vectorizer.transform(query)
    query_vec = np.array((new_term_freq_matrix.todense().tolist())[0])
    # np.linalg.norm(query_vec,ord=2)
    # for i in range(0, len(query_vec)):
    #     if query_vec[i] > 0:
    #         print(i, " ", query_vec[i])

    idscorepairlist = []
    docdenselist = docdense.tolist()
    round = len(docidlist)
    for i in range(0, round):
        doc_vec = np.array(docdenselist[i])
        score = np.dot(doc_vec, query_vec) / np.linalg.norm(query_vec, ord=2) / np.linalg.norm(doc_vec, ord=2)
        if score > 0:
            idscorepairlist.append([docidlist[i], score])

    idscorepairlist.sort(key=lambda x: (x[1], x[0]), reverse=True)

    print("if u wanna search following files:")
    f = open(doc_id_DICT_PATH, "rb")
    doc_id_list = pkl.load(f)

    for i in range(0, min(len(idscorepairlist), MAX_RECOMMEND_NUM)):
        print("Rank", i, ": ", doc_id_list[idscorepairlist[i][0]], idscorepairlist[i][1])


def url_query(query):
    pass


def site_query(query):
    pass
