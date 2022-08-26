#!/usr/bin/env python3
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import requests
from generate_rsa import generate_key_pair


class HTTPRequest(QObject):
    completed = pyqtSignal(requests.Response)
    error = pyqtSignal(Exception)

    def __init__(self, url: str,
                 method: str = "GET", parent: QObject = None):
        super().__init__(parent)
        self.method = method
        self.url = url

    @classmethod
    def from_url(cls, url: str, method: str = "GET", parent: QObject = None):
        return cls(url, method, parent)

    @classmethod
    def from_strings(cls, protocol: str, host: str, port: int, path: str,
                     method: str = "GET", parent: QObject = None):
        url = f"{protocol}://{host}:{port}/{path}"
        return cls(url, method, parent)

    @pyqtSlot()
    @pyqtSlot(str, str, dict)
    def make_request(self, url: str = None, method: str = None,
                     kwargs: dict = {}):
        if url is None or url == "":
            url = self.url
        if method is None or url == "":
            method = self.method

        print(url, method, kwargs)

        try:
            response = requests.request(method, url, **kwargs)
            self.completed.emit(response)
        except requests.ConnectionError as err:
            self.error.emit(err)
        except requests.exceptions.InvalidURL as err:
            self.error.emit(err)
        except Exception as err:
            self.error.emit(err)


class GenerateRSA(QObject):
    completed = pyqtSignal(dict)
    error = pyqtSignal(Exception)

    def __init__(self, password: str = None,
                 key_options: dict = {
                    "public_exponent": 65537,
                    "key_size": 4096
                 },
                 private_file: str = None,
                 public_file: str = None, parent: QObject = None):
        super().__init__(parent)
        self.password = password
        self.key_options = key_options
        self.private_file = private_file
        self.public_file = public_file

    @pyqtSlot()
    @pyqtSlot(str, dict, str, str)
    def gen_key(self, password: str = None, key_options: dict = None,
                private_file: str = None, public_file: str = None):
        if password is None:
            password = self.password
        if key_options is None:
            key_options = self.key_options
        if private_file is None:
            private_file = self.private_file
        if public_file is None:
            public_file = self.public_file

        try:
            key = generate_key_pair(password, key_options,
                                    private_file, public_file)
            self.completed.emit(key)
        except Exception as err:
            self.error.emit(err)


if __name__ == '__main__':
    request = HTTPRequest("http", "localhost", 5000)
    request.completed[requests.Response].connect(lambda res: print(res))
    request.error[Exception].connect(lambda err: print(err))
    request.make_request()

    rsa = GenerateRSA()
    rsa.completed[dict].connect(lambda keys: print(keys))
    rsa.error[Exception].connect(lambda err: print(err))
    rsa.gen_key()
