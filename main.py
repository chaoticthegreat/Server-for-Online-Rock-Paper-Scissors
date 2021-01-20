from flask import Flask,request
from threading import Thread
import time, random, requests
app = Flask(__name__)

clients = {}
servercount = 0
servers = {}
runningserver = {}
@app.route("/")
def hello_world():
  return "Hello World!"
@app.route("/<username>/<skip>")
def match(username, skip):
  global  servercount, clients, servers
  clients[username] = True
  while True:
    if skip =="false":
      for key in servers.keys():
        if len(servers[key]) == 1 :
          servers[key].append(username)
          runningserver[key] = {1:{username: None, servers[key][0]: None},2:{username: None, servers[key][0]: None},3:{username: None, servers[key][0]: None}}
          print(username," joined someone's server!")
          return {"server":str(key), "match": servers[key][0]}
    if skip == "true":
      myserver= request.json["server"]
    else:
      servercount+=1
      myserver = servercount
      servers[myserver] = [username]
    try:
      return {"server":str(myserver), "match": servers[myserver][1]}
    except IndexError:
      return {"server":myserver,"match":"nothing"}
@app.route("/server", methods = ["POST","GET"])
def server():
  global runningserver
  jsondata = request.json
  round = jsondata["round"]
  username = jsondata["username"]
  myserver = jsondata["server"]
  try:
    if servers[myserver][0] == username:opponent = servers[myserver][1]
    else:opponent = servers[myserver][0]
  except:
    x = requests.get("https://Server-for-Online-Rock-Paper-Scissors.proryan.repl.co/"+username+"/true", json = {"server":myserver})
    if x.json()["match"] == "nothing":
      return "kicked"
    return {"0":x.json(), "1":"true"}
  if request.method == "POST":
    choice = jsondata["choice"]
    runningserver[myserver][int(round)][username] = choice
    return "Done!"
  elif request.method == "GET":
    if len(list(runningserver[myserver][int(round)])) == 1:
      x = requests.get("https://Server-for-Online-Rock-Paper-Scissors.proryan.repl.co/"+username+"/true", json = {"server":myserver})
      if x.json()["match"] == "nothing":
        return "kicked"
      return {"0":x.json(), "1":"true"}
    elif runningserver[myserver][int(round)][opponent] == None:
      return "Nothing"
    else:
      return {0:runningserver[myserver][int(round)][opponent], 1:"false"}
  return "Hello"
@app.route("/check", methods = ["POST"])
def check():
  username = request.json["username"]
  global clients
  clients[username] = True
  print("I got you "+username)
  return "It doesn't matter!"
def run():
  app.run(host = '0.0.0.0', port = 3000, debug = False)
def heartbeat():
  global clients, servers, serverstate, runningserver
  while True:
    time.sleep(5)
    for client in list(clients):
      if clients[client] == False:
        del clients[client]
        for thing in list(servers):
          if client in servers[thing]:
            if len(servers[thing]) == 1:
              try:
                if thing in runningserver.keys():
                  del runningserver[thing]
                del servers[thing]
                del serverstate[thing]
                print("Oof! You got kicked! ",client)
              except:
                pass
            else:
              try:
                print("Kicked ",client)
                if thing in runningserver.keys():
                  for i in range(1,4):
                    runningserver[thing][i][client] = "kicked"
                servers[thing].remove(client)
                serverstate[thing] = True
              except:pass
      else:
        clients[client] = False
Thread(target = run).start()
Thread(target = heartbeat).start()