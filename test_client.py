from socket import *
import json

sock = socket()
addr = ('127.0.0.1', 25014)
sock.connect(addr)
data = {'protocol': 'LOGIN', 'name': 'aaa', 'pwd': '13456'}
data = json.dumps(data)
sock.send(data.encode())
msg = sock.recv(1024)
print(msg.decode())
sock.close()
