import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      data = data[2:-1]
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
         else:
            playerInfo = json.loads(data)
            clients[addr]['position'] = playerInfo['position']
            clients[addr]['rotation'] = playerInfo['rotation']
         
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clients[addr]['position'] = {}
            clients[addr]['rotation'] = {}
            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

def cleanClients():
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         Player = {}
         clients[c]['color'] = {"r": random.random(), "g": random.random(), "b": random.random()} #dlksjldksa
         Player['id'] = str(c)
         Player['color'] = clients[c]['color']
         Player['position'] = clients[c]['position']
         Player['rotation'] = clients[c]['rotation']
         GameState['players'].append(Player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(0.03)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,())
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()