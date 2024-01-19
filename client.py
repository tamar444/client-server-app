from socket import *
from threading import *
import time

srv_adress='localhost'
srv_port=2222
client_sock=socket(AF_INET,SOCK_STREAM)
client_sock.connect((srv_adress,srv_port))

class ReadThread(Thread):
    def __init__(self, client_sock):
        self.sock=client_sock
        super().__init__()
        self.start()
    def run(self):
      try:
       while True:
        message = client_sock.recv(1024).decode()
        if message=='Dovidjenja!':
            print(message)
            break
        elif message.startswith('Potvrda:'):
            ms=str(round(time.time()*1000))
            potvrda_o_uplati='potvrda_o_uplati'+ms+'.txt'
            with open(potvrda_o_uplati,'w') as fajl:
                  fajl.write(message)
            continue
        print(message)
      except:
         print('Server je prekinuo komunikaciju.')

if __name__=='__main__':
    read_thread=ReadThread(client_sock)
    while True:
        user_input = input()
        client_sock.send(user_input.encode())
        if user_input.lower() == '6':
            break