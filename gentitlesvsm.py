from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import re
import pickle as pkl
from string import punctuation

DATA_BASEPATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_dir\\doc_url.txt"
TITLES_TFIDF_VECTORIZOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\titles_vectorizor.dict"
# URLID2VECTOR_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\urlid_vector.dict"
MAX_LOOP_TIMES = 7364


def genvsm():
    mydoclist = []
    docidlist = []
    # url2id_dict = {}.
    f = open(DATA_BASEPATH, "rb")
    lines = f.readlines()

    for i in range(0, MAX_LOOP_TIMES):
        content = lines[i].decode('utf-8')
        content = (content.split(" "))[0]
        content = re.sub(r"[{}、，。！？·【】）》；;《“”（-]+".format(punctuation), " ", content)
        content = content.lower()
        words = ' '.join(jieba.lcut_for_search(content))
        mydoclist.append(words)
        docidlist.append(i)
        # print(words)
        print("DOC" + str(i) + "'s vector finish..")

    tfidf_vectorizer = TfidfVectorizer(min_df=1)
    tfidf_matrix = tfidf_vectorizer.fit_transform(mydoclist)
    fdense = tfidf_matrix.todense()

    # write tfidf_vectorizer & fileidlist into disk
    fovec = open(TITLES_TFIDF_VECTORIZOR_PATH, "wb")
    pkl.dump((tfidf_vectorizer, docidlist, fdense), fovec)
    print("write tfidf_vectorizer into disk finish")

    # # write urlid2vector dict into disk
    # fdense = tfidf_matrix.todense()
    # for i in range(0, len(fileidlist)):
    #     url2id_dict[fileidlist[i]] = fdense[i]
    # fodic = open(URLID2VECTOR_PATH, "wb")
    # pkl.dump(url2id_dict, fodic)
    # print("write urlid2vector dict into disk finish")
