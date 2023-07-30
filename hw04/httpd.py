import socket
import sys
import threading
import re
from request_handler import RequestParse
from config import *
import argparse

def run_server(port=8080, workers=1):
    '''запуск сервера'''
    if DEBUG:
        print('run_server')
    # биндим порт
    serv_sock = create_serv_sock(port)
    cid = 0
    while True:
        # принимаем клиента
        client_sock = accept_client_conn(serv_sock, cid)
        # обслуживаем клиента
        while True:
            if len(POOL) < workers:
                # основной поток - занимается приемом входящих подключений
                # когда создается клиентский сокет, запускается дополнительный поток
                t = threading.Thread(name = str(cid), target=serve_client, args=(client_sock,cid))
                POOL[cid] = t
                t.start()
                break
            else:
                print('waiting free worker for CLIENT:', cid, ', workers busy:', len(POOL),'/', workers)   
        cid += 1


def create_serv_sock(serv_port):
    '''биндим порт'''
    if DEBUG:
        print('create_serv_sock')
    # с помощью socket создаем объект для работы с сокетом
    serv_sock = socket.socket(socket.AF_INET,
                              socket.SOCK_STREAM,
                              proto=0)
    # биндимся и слушаем сокет
    serv_sock.bind(('0.0.0.0', serv_port))
    serv_sock.listen()
    print('Listening on {}:{}'.format('127.0.0.1', serv_port))
    return serv_sock


def accept_client_conn(serv_sock, cid):
    '''принимаем клиента'''
    if DEBUG:
        print('accept_client_conn')
    client_sock, client_addr = serv_sock.accept()
    print(f'Client #{cid} connected '
          f'{client_addr[0]}:{client_addr[1]}')
    return client_sock
    

def serve_client(client_sock, cid):
    '''обслуживаем клиента'''
    if DEBUG:
        print('serve_client')
    # читаем запрос
    request = read_request(client_sock)
    print('Received {}'.format(request))
    if request is None:
        print(f'Client #{cid} unexpectedly disconnected')
    else:
        # задерживаем запрос
        response = handle_request(request)
        # выдача ответа 
        write_response(client_sock, response, cid)


def read_request(client_sock, delimiter=b'\r\n\r\n'):
    '''читаем запрос'''
    if DEBUG:
        print('read_request')
    request = bytearray()
    try:
        while True:
            chunk = client_sock.recv(4)
            if not chunk:
                # Клиент преждевременно отключился.
                return None

            request += chunk
            if delimiter in request:
                return request

    except ConnectionResetError:
        # Соединение было неожиданно разорвано.
        return None
    except:
        raise





def get_requested_path(request):
    req = request.decode()
    path = re.findall(r'^(?:GET|HEAD)\s+.+\sHTTP', req)
    if DEBUG:
        print('\nDEBUG', path[0].split(' ')[1])
        
    return path[0].split(' ')[1]


def is_file_request(path):
    filename = path.split('/')[-1]
    if '.' in filename:
        return filename




def handle_request(request):
    '''удерживаем запрос'''
    if DEBUG:
        print('handle_request')
    
    req = RequestParse(request)
    return req.create_response()


def handle_request_old(request):
    '''удерживаем запрос'''
    if DEBUG:
        print('handle_request')

    responce = 'HTTP/1.1 200 OK\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\n\r\n'
    if 'HEAD' in request.decode():
        # if error:
        #     return error
        return responce
    elif 'GET' in request.decode():
        # if error:
        #     return error
        return responce + '<html><pre>{0}</pre></html>'
    else:
        return 'HTTP/1.1 405 Method Not Allowed\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\n\r\n'


def write_response(client_sock, response, cid):
    '''выдаем ответ'''
    if DEBUG:
        print('write_response')
        print(repr(response))
    if type(response) is bytes:
        client_sock.sendall(response)
    else:
        client_sock.sendall(response.encode())
    client_sock.close()
    POOL.pop(cid)
    print(f'Client #{cid} has been served')


if __name__ == '__main__':
    parser_var = argparse.ArgumentParser()

    parser_var.add_argument('-r',
                        default=DOCUMENT_ROOT,
                        help="set document root")
    parser_var.add_argument('-p',
                        default=8080,
                        help="set port")
    parser_var.add_argument('-w',
                        default=20,
                        help="set workers")
    args = parser_var.parse_args()
    DOCUMENT_ROOT = args.r
    run_server(port=int(args.p),workers=int(args.w))