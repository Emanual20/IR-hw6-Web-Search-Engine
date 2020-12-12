import os
import pickle as pkl

NICKNAME_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_out\\name_pw.dict"
NICKNAME_DICT = {}


# User Register & Login Modules
def InitUserModules():
    global NICKNAME_DICT
    f = open(NICKNAME_PATH, "rb")
    NICKNAME_DICT = pkl.load(f)
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
