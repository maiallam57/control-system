from ast import Pass
from copyreg import pickle
import socket
import threading
import json
from time import sleep
import config
import pickle
import ast
class Client(): #threading

    def __init__(self,HOST,PORT):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket object that supports IPv4, TCP Protocol
        # self.s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.s.connect((HOST, PORT)) # connect to server
        #self.receiver()
        # self.sender()
        #self.thread = threading.Thread(target=receiver)
        # self.thread = threading.Thread(target=self.receiver)
        # self.thread.start()
    
    def receiver(self):
        
        print('Connected!')
        # data = bytearray()
        self.s.send(str.encode('Server is working!'))
        while True:
            try:
                dataLength = int(self.s.recv(2).decode("utf-8"))
                data = self.s.recv(dataLength)
                if config.sensors == 'q':
                    socket.close()
                    break
                data_str=pickle.loads(data)
                # config.sensors=repr(ast.literal_eval(data_str))
                config.sensors=(data_str)
                print(data_str)
                
            except ConnectionError:
                print('Socket error')
                break
            sleep(0.1)
        return config.sensors

    def sender(self, data): 

        self.s.send((bytes(data, 'utf-8')))

