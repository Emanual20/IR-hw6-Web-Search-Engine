import os
import pickle as pkl

NICKNAME_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\name_pw.dict"
USER_LOG_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\name_userlog.dict"
NICKNAME_DICT = {}
USER_LOG_DICT = {}


# User Register & Login Modules
def InitUserModules():
    global NICKNAME_DICT
    f = open(NICKNAME_PATH, "rb")
    NICKNAME_DICT = pkl.load(f)

    # f = open(USER_LOG_PATH,"wb")
    # pkl.dump({},f)

    global USER_LOG_DICT
    f = open(USER_LOG_PATH, "rb")
    USER_LOG_DICT = pkl.load(f)

    print("User Modules Initialized..!")


def PrintDict():
    print(NICKNAME_DICT)


def RegisterManager(nickname, password):
    f = open(NICKNAME_PATH, "rb")
    NICKNAME_DICT = pkl.load(f)
    if nickname in NICKNAME_DICT.keys():
        return 0
    else:
        NICKNAME_DICT[nickname] = password
    f = open(NICKNAME_PATH, "wb")
    pkl.dump(NICKNAME_DICT, f)
    return 1


def LoginManager(nickname, password):
    f = open(NICKNAME_PATH, "rb")
    NICKNAME_DICT = pkl.load(f)
    if nickname in NICKNAME_DICT:
        if NICKNAME_DICT[nickname] == password:
            return 1
    return 0


def QueryLogManager(nickname, query):
    f = open(USER_LOG_PATH, "rb")
    LOG_DICT = pkl.load(f)

    if nickname not in LOG_DICT.keys() or LOG_DICT[nickname] is None:
        LOG_DICT[nickname] = []

    # update query log
    tmp = LOG_DICT[nickname]
    tmp.append(query)
    LOG_DICT[nickname] = tmp
    # print(LOG_DICT)

    # update user log to disk
    f = open(USER_LOG_PATH, "wb")
    pkl.dump(LOG_DICT, f)


def DisplayLogManager(nickname, num):
    f = open(USER_LOG_PATH, "rb")
    LOG_DIC = pkl.load(f)

    if nickname not in LOG_DIC.keys():
        print("you have no query history..")
        return

    NOW_LOG_LIST = LOG_DIC[nickname]
    print("your log list is as follows:")
    for i in range(1, min(eval(num), len(NOW_LOG_LIST), 20)+1):
        print("LATEST ", i, ": ", NOW_LOG_LIST[-i])
