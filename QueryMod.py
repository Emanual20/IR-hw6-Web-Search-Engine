import pickle as pkl
import jieba
import re
import numpy as np
from string import punctuation

DATA_BASEPATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_dir\\"
DATA_SUFFIX = ".info"
doc_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\doc_id.dict"
url_id_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_id.dict"
url_list_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\url_list.dict"
id_pagerank_DICT_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\id_pagerank.dict"
USER_LOG_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\name_userlog.dict"
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
        score = np.dot(doc_vec, query_vec) / (np.linalg.norm(query_vec, ord=2) + 1) / (
                    np.linalg.norm(doc_vec, ord=2) + 1)
        if score > 0:
            idscorepairlist.append([docidlist[i], score])

    idscorepairlist.sort(key=lambda x: (x[1], x[0]), reverse=True)

    print("maybe u wanna search following files:")
    f = open(doc_id_DICT_PATH, "rb")
    doc_id_list = pkl.load(f)

    for i in range(0, min(len(idscorepairlist), MAX_RECOMMEND_NUM)):
        print("Rank", i, ": ", doc_id_list[idscorepairlist[i][0]], idscorepairlist[i][1])


# return a urlidlist
def url_query(query):
    f = open(url_id_DICT_PATH, "rb")
    URL_ID_DIC = pkl.load(f)
    f = open(id_pagerank_DICT_PATH, "rb")
    ID_PAGERANK_DIC = pkl.load(f)

    BUFFER_LIST = []
    for id in ID_PAGERANK_DIC.keys():
        if query in URL_ID_DIC[id]:
            BUFFER_LIST.append([id, ID_PAGERANK_DIC[id]])

    BUFFER_LIST.sort(key=lambda x: (x[1], x[0]), reverse=True)

    ret_urlid_list = []
    print("maybe u wanna search following urls:")
    for i in range(0, min(len(BUFFER_LIST), MAX_RECOMMEND_NUM)):
        print("Rank", i, ": ", URL_ID_DIC[BUFFER_LIST[i][0]], BUFFER_LIST[i][1])
        ret_urlid_list.append(BUFFER_LIST[i][0])
    return ret_urlid_list


# return a siteidlist
def site_query(query, nickname):
    MAX_CONTENTS_TIMES = 5000
    MAX_HISTORY_CONSIDERING_NUM = 10

    f = open(CONTENTS_TFIDF_VECTORIZOR_PATH, "rb")
    tfidf_vectorizer, urlidlist, wordslist = pkl.load(f)

    # calc real query_vec
    query = re.sub(r"[{}、，。！？·【】）》；;《“”（-]+".format(punctuation), " ", query)
    query = query.lower()
    query_words = ' '.join(jieba.lcut_for_search(query))
    query = []
    query.append(query_words)

    new_term_freq_matrix = tfidf_vectorizer.transform(query)
    query_vec = np.array((new_term_freq_matrix.todense().tolist())[0])

    # put user's history queries into vector to some extent
    f = open(USER_LOG_PATH, "rb")
    LOG_DIC = pkl.load(f)
    if nickname in LOG_DIC.keys():
        LATEST_QUERY_LIST = LOG_DIC[nickname]
        round = min(MAX_HISTORY_CONSIDERING_NUM, len(LATEST_QUERY_LIST))
        for i in range(1, round + 1):
            vec = [LATEST_QUERY_LIST[-i]]
            tmp_mat = tfidf_vectorizer.transform(vec)
            tmp_vec = np.array((tmp_mat.todense().tolist())[0])
            query_vec = query_vec + tmp_vec * 0.3 / (round + 1)

    idscorepairlist = []
    round = len(urlidlist)

    # calc all the sites score, must be one site one time, or will run out of memory
    for i in range(0, round):
        if i > MAX_CONTENTS_TIMES:
            break

        try:
            f = open(DATA_BASEPATH + str(urlidlist[i]) + DATA_SUFFIX, "rb")
        except FileNotFoundError:
            continue

        mysitelist = []
        words = wordslist[i]
        mysitelist.append(words)
        now_doc_freq_matrix = tfidf_vectorizer.transform(mysitelist)
        contents_vec = np.array((now_doc_freq_matrix.todense().tolist())[0])

        score = np.dot(contents_vec, query_vec) / (np.linalg.norm(query_vec, ord=2) + 1) / (
                    np.linalg.norm(contents_vec, ord=2) + 1)
        if score > 0:
            idscorepairlist.append([urlidlist[i], score])
        # if not (i % 500):
        #     print("site:", i, "finish")

    idscorepairlist.sort(key=lambda x: (x[1], x[0]), reverse=True)

    print("maybe u wanna search following sites:")
    f = open(url_id_DICT_PATH, "rb")
    url_id_dict = pkl.load(f)

    ret_urlid_list = []
    for i in range(0, min(len(idscorepairlist), MAX_RECOMMEND_NUM)):
        print("Rank", i, ": ", url_id_dict[idscorepairlist[i][0]], idscorepairlist[i][1])
        ret_urlid_list.append(idscorepairlist[i][0])

    return ret_urlid_list
