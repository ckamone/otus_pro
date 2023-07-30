from config import *
import re
import os
from datetime import datetime
import urllib.parse


class Responser():
    def __init__(self, status, method, path, filename):
        self.status = status
        self.method = method
        self.path = path
        self.filename = filename if filename else 'index.html'
        self.header_main = self.get_main_header()
        self.header_server = 'Server: Microsoft-IIS/6.0\r\n'
        self.header_ctype = ''
        self.header_clen = ''
        self.header_date = ''
        self.header_connection = 'Connection: Close\r\n'
        self.clrf = '\r\n'
        self.headers = self.make_headers()
        
    def get_main_header(self):
        if self.status == 405:
            return 'HTTP/1.1 405 Method Not Allowed\r\n'
        elif self.status == 403:
            return 'HTTP/1.1 403 Forbidden\r\n'
        elif self.status == 404:
            return 'HTTP/1.1 404 Page Not Found\r\n'
        elif self.status == 200:
            return 'HTTP/1.1 200 OK\r\n'
        
    def make_header_ctype(self):
        filetype = None
        texttypes = ['html', 'css']
        apptypes = ['js']
        
        for tp in texttypes:
            if tp in self.filename:
                filetype = 'text/'+tp
                break
            else:
                if '.js' in self.filename:
                    filetype = "application/x-javascript"
                elif '.swf' in self.filename:
                    filetype = "application/x-shockwave-flash"
                else:
                    filetype = 'image/'+self.filename.split('.')[-1]
                    filetype = filetype.replace('jpg','jpeg')
        
        self.header_ctype = f'Content-Type: {filetype}\r\n'
    
    def make_header_clen(self):
        fullpath = self.path + self.filename
        with open(fullpath, 'rb+') as f:
            content = f.read()
        self.header_clen = f'Content-Length: {str(len(content))}\r\n'

    def make_header_date(self):
        date = datetime.now()
        string = date.strftime('%a, %D %b %Y %H:%M:%S %Z')
        self.header_date = f'Date: {string}\r\n'

    def make_headers(self):
        if self.status == 200:
            print('*'*80)
            self.make_header_ctype()
            self.make_header_clen()
        self.make_header_date()
        return self.header_main + self.header_server + self.header_ctype + self.header_clen + self.header_date + self.header_connection + self.clrf

    def make_resp(self):
        if self.status == 200:
            if self.method == 'HEAD':
                return self.headers
            else:
                fullpath = self.path + self.filename
                with open(fullpath, 'rb+') as f:
                    html = f.read()
                    if type(html) is bytes:
                        rsp = bytes(self.headers, 'UTF-8') + html + bytes(self.clrf, 'UTF-8')
                    else: 
                        rsp = self.headers + html.decode() + self.clrf
                    return rsp
        else:
            return self.headers


class RequestParse():
    def __init__(self, request):
        self.request = request.decode()
        # парсим метод
        self.method = self.get_method()
        # проверка что метод разрешен
        self.meth_is_allowed = self.is_allowed_meth()
        self.status = None
        self.path = None
        self.filename = None
        self.req_is_file = None
        self.file_is_exist = None
        self.query_string = None
        self.method_path = ''

        if self.meth_is_allowed:

            self.method_path = self.get_path()
            # # self.path = 
            self.path_is_allowed = self.is_allowed_path()
            if not self.path_is_allowed:
                self.status = 403
            
            # мы здесь, если метод и путь разрешены. далее проверки по файлу. если не файл то ищем индекс, если файл то ищем файл
            self.req_is_file = self.is_file_req()
            self.file_is_exist = self.is_exist_file()
            if not self.file_is_exist:
                self.status = 404
            else:
                self.status = 200
        else:
            self.status = 405
        
    def create_response(self):
        response = Responser(self.status, self.method, DOCUMENT_ROOT+self.method_path, self.filename)
        return response.make_resp()

    def get_method(self):
        return self.request.split(' ')[0]

    def is_allowed_meth(self):
        return True if self.method in ALLOWED_METHOD else False

    def get_path(self):
        path = re.findall(r'^(?:GET|HEAD)\s+.+\sHTTP', self.request)
        print('debg',path[0].split(' ')[1])
        return path[0].split(' ')[1]

    def is_allowed_path(self):
        return True if self.method_path in ALLOWED_PATH else False
    
    def check_query_string(self):
        if '?' in self.filename:
            self.query_string = self.filename.rsplit('?')[1]
            self.filename = self.filename.rsplit('?')[0]
            self.method_path = self.method_path.rsplit('?')[0]

    def check_spaces(self):
        if '%20' in self.filename:
            self.filename = self.filename.replace('%20', ' ')
            self.method_path = self.method_path.replace('%20', ' ')

    def decode_url(self):
        self.method_path = urllib.parse.unquote(self.method_path)

    def is_file_req(self):
        self.decode_url()
        if '.' in self.method_path:
            temp = self.method_path.split('.')[-1].rsplit('?')[0]
            if temp in ALLOWED_TYPES:
                self.filename = self.method_path.split('/')[-1]
                self.check_query_string()
                self.method_path = self.method_path.rstrip(self.filename)
                self.check_spaces()
                self.path_is_allowed = self.is_allowed_path()
                return True

    def is_exist_file(self):
        path = DOCUMENT_ROOT+self.method_path
        try:
            if not self.req_is_file:
                if 'index.html' in os.listdir(path):
                    return True

            # for (dirpath, dirnames, filenames) in os.walk(path):
            #     print('----', filenames)
            #     if 'index.html' in filenames:
            #         return True
            else:
            # for (dirpath, dirnames, filenames) in os.walk(path):
            #     if self.filename in filenames:
            #         return True
                if self.filename in os.listdir(path):
                    return True
        except NotADirectoryError:
            return False


def main():    
    request = b'GET //httptest/160313.jpg HTTP/1.1\r\nHost: localhost:8080\r\nUser-Agent: curl/7.81.0\r\nAccept: */*\r\n\r\n'
    req = RequestParse(request=request)
    print('DEBUG')
    # test method parse
    print('method:',req.method)
    # test method allowed check
    print('meth is allowed:', req.meth_is_allowed)
    

    # getting path
    print('req path:',req.method_path)

    # check is path allowed?
    print('req path allowed:', req.path_is_allowed)

    # is fileget_response() rreq?
    print('req with filename:', req.req_is_file)

    # 404 check
    print('file exists:', req.file_is_exist)

    # make resp
    print('\n',req.create_response(), sep='')


if __name__ == "__main__":
    main()

# def check_errors(request):
    
#     print(os.path.join(DOCUMENT_ROOT, filepath))
#     for (dirpath, dirnames, filenames) in os.walk(DOCUMENT_ROOT+filepath):
#         if filepath.split('/')[-1] in TYPES:
#             # file
#             pass
#         else:
#             # index page
#             if 'index.html' in filenames:
#                 print('here1')
#                 with open(DOCUMENT_ROOT+filepath+'index.html','rb+') as f:
#                     html = f.read()
#                     print(file)
#                     return html
#             print(dirpath, dirnames, filenames)
#     if check_403(filepath): 
#         return 'HTTP/1.1 403 Forbidden\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\n\r\n'
#     if check_404(filepath):
#         return 'HTTP/1.1 404 Page Not Found\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\n\r\n'
# def check_403(filepath):
#     '''проверка пути'''
#     pass


# def check_404(filepath):
#     '''проверка страницы'''
#     pass