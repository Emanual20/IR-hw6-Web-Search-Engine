import socket
import time

HTML_PATH = "M:\\Code Area\\PY\\IR-hw6-Web-Search-Engine\\dataset\\data_dir\\"
HTML_SUFFIX = ".code"


def display(url_id):
    global HTML_PATH
    start_time = time.time()
    server_html = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_html.bind(("127.0.0.1", 1425))
    server_html.listen(10)
    while True:
        CACHE_PATH = HTML_PATH + str(url_id) + HTML_SUFFIX
        conn, addr = server_html.accept()
        msg = conn.recv(1024 * 12)
        file_html = open(CACHE_PATH, "rb")
        data = file_html.read()
        conn.sendall(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        try:
            conn.sendall(data)
        except ConnectionAbortedError:
            break
        conn.close()
        end_time = time.time()
        if time.localtime(end_time - start_time).tm_sec >= 5:
            break
        #
        # option = input("input q to quit Cache_Module:")
        # if 'q' in option or 'Q' in option:
        #     break
