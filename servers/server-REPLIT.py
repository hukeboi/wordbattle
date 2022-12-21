from flask import Flask, request, jsonify
import time
import secrets
import random
from waitress import serve
from uralicNLP import uralicApi
import os
import json


#CONFIG
#max games the server will host
MAX_GAMES = 5

#max waiting slots. How many people can wait for their friend to join
MAX_WAITING_SLOTS = 4

#max time to wait for opponent to join game (in seconds)
MAX_WAIT_TIME = 30.0

#max time from previous update to delete game (in minutes)
MAX_INACTIVE_GAME = 4

#password needed to retrieve all games from the server.
#make a get request to '/api/admin/getallgames' with the 'admin' header set as the password
ADMIN_PASSWORD = "1234"

#different letter weights
weights = (
    22,  #A
    2,   #B
    0,   #C
    2,   #D
    19,  #E
    1,   #F
    4,   #G
    17,  #H
    21,  #I
    19,  #J
    19,  #K
    18,  #L
    19,  #M
    19,  #N
    19,  #O
    17,  #P
    0,   #Q
    18,  #R
    19,  #S
    20,  #T
    19,  #U
    12,  #V
    0,   #W
    0,   #X
    3,   #Y
    0,   #Z
    0,   #Å
    9,  #Ä
    7,  #Ö
)

#DONT MODIFY ANYTHING BEYOND THIS!
app = Flask('')

@app.route('/')
def main():
    return "under construction"

allLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"
vocals = ["A", "E", "I", "O", "U", "Y", "Å", "Ä", "Ö"]
consonants = ["B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "X", "Z"]
width = 10
height = 13
peopleWaiting = 0
def GenerateMap():
    map = []
    for y in range(0, height, 1):
        thisRow = []
        for x in range(0, width, 1):
            thisRow.append(random.choices(allLetters, weights=weights))
        map.append(thisRow)
    return map
def SafeAddHeight(original, amount):
    newAmt = original + amount
    if newAmt <= 0:
        newAmt = 1
    elif newAmt >= height:
        newAmt = height - 1
    return newAmt
def SafeAddWidth(original, amount):
    newAmt = original + amount
    if newAmt <= 0:
        newAmt = 1
    elif newAmt >= width:
        newAmt = width - 1
    return newAmt
def ParseWeights():
    vocalWeights = []
    consonantWeights = []
    for i in range(0, len(weights), 1):
        if allLetters[i] in vocals:
            vocalWeights.append(weights[i])
        elif allLetters[i] in consonants:
            consonantWeights.append(weights[i])
        else:
            print("Warning: Invalid alphabet")
    return [vocalWeights, consonantWeights]
def ListToDict(map):
    new = {}
    for row in range(1, height + 1, 1):
        columnVal = {}
        for column in range(1, width + 1, 1):
            columnVal[str(column) + "col"] = map[row - 1][column - 1][0]
        new[str(row) + "row"] = columnVal
    return new
def breakConsonants(map):
    for x in range(0, width, 1):
        for y in range(0, height, 1):
            if map[y][x][0] not in vocals:
                if map[SafeAddHeight(y, -1)][x][0] not in vocals and map[SafeAddHeight(y, 1)][x][0] not in vocals and map[y][SafeAddWidth(y, -1)][0] not in vocals and map[y][SafeAddWidth(y, 1)][0] not in vocals:
                    map[y][x] = random.choices(vocals, weights=vocalWeights)

    return map
def breakVocals(map):
    for x in range(0, width, 1):
        for y in range(0, height, 1):
            if map[y][x][0] not in vocals:
                if (map[SafeAddHeight(y, -1)][x][0] not in consonants and map[SafeAddHeight(y, 1)][x][0] not in consonants) or (map[y][SafeAddWidth(y, -1)][0] not in consonants and map[y][SafeAddWidth(y, 1)][0] not in consonants):
                    map[y][x] = random.choices(consonants, weights=consonantWeights)

    return map
def IsValidWord(map, word, wordData):
    if len(word) != len(wordData): 
        return False
    for i in range(0, len(wordData), 1):
        pos = map[str(wordData[i][0]) + "row"][str(wordData[i][1]) + "col"]
        if pos[0] != word[i]:
            return False
            
    return True
def IsRealWord(word):
  test = uralicApi.lemmatize(word, "fin", word_boundaries=True)
  if test == []:
    return False
  for i in range(0, len(test), 1):
    with open('allwords.txt') as f:
      line = next((l for l in f if test[i] in l), None)
    if line != None:
      break
  if line == None:
    return False
  else:
    return True
ParsedWeights = ParseWeights()
vocalWeights = tuple(ParsedWeights[0])
consonantWeights = tuple(ParsedWeights[1])

if os.path.exists("config.json") == False:
    uralicApi.download("fin")
    with open("config.json", "w") as f:
        f.write(json.dumps({"install_words": False}))
else:
    with open("config.json", "r") as f:
        conf = json.load(f)
        if conf["install_words"] == True:
            uralicApi.download("fin")
            conf["install_words"] = False
            with open("config.json", "w") as f2:
                f2.write(json.dumps(conf))

#DONT MODIFY THESE
allData = {

}

@app.route('/api/makenewgame', methods=['GET'])
def makenewgame():
    toDel = []
    for game in allData:
        if time.time() - allData[game]["lastActivity"] > MAX_INACTIVE_GAME * 60:
            toDel.append(game)
    for i in range(0, len(toDel), 1):
        for obj in toDel:
            allData.pop(obj)
            print("A game was deleted because of inactivity.")
    if len(allData) > MAX_GAMES: return jsonify({"result" : "-1", "error":"The server is currently at full capacity"})
    newGameId = str(secrets.token_hex(2))
    allData[newGameId] = {
        "playersInServer": 0,
        "playerSecrets": [],
        "map": {},
        "currentTurn": 1,
        "currentWord": "",
        "currentWordData": [],
        "lastActivity": time.time()
    }
    #print("NEW GAME: " + newGameId)
    return jsonify({"result" : "0", "gameid":newGameId})

@app.route('/api/getserverstatus', methods=['GET'])
def getserverstatus():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    if data["playersInServer"] == 0:
        data["playersInServer"] = 1
        Psecret = str(secrets.token_hex(32))
        data["playerSecrets"].append(Psecret)
    elif data["playersInServer"] == 1:
        data["playersInServer"] = 2
        Psecret = str(secrets.token_hex(32))
        data["playerSecrets"].append(Psecret)
    else:
        returnData = {"result" : "-1", "error":"Already 2 players in server."}
        return jsonify(returnData)

    print("New player.\nSecret: " + Psecret + "\nGame id: " + request.headers['gameid'])
    returnData = {"result" : "0", "secret": Psecret, "player": str(data["playersInServer"])}
    return jsonify(returnData)
    
@app.route('/api/getgamedata', methods=['GET'])
def getGameData():
    global peopleWaiting
    if peopleWaiting >= MAX_WAITING_SLOTS: 
        allData.pop(request.headers['gameid'])
        return jsonify({"result" : "-1", "error":"Too many people waiting."})
    peopleWaiting += 1
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    data["lastActivity"] = time.time()
    if request.headers['secret'] == data["playerSecrets"][0]:
        player = 1
    elif request.headers['secret'] == data["playerSecrets"][1]:
        player = 2
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})
    if data["map"] == {}:
        newMap = GenerateMap()
        newMap = breakConsonants(newMap)
        newMap = breakVocals(newMap)
        newMap = ListToDict(newMap)
        data["map"] = newMap
    StartTime = time.time()
    while data["playersInServer"] != 2:
        time.sleep(0.1)
        if time.time() - StartTime > MAX_WAIT_TIME:
            peopleWaiting -= 1
            allData.pop(request.headers['gameid'])
            return jsonify({"result" : "-1", "error": "You timed out."})
    peopleWaiting -= 1
    return jsonify({"result" : "0", "data": data["map"]})

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"result": "0"})

@app.route('/api/postword', methods=['POST'])
def postword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    data["lastActivity"] = time.time()
    if (request.headers['player'] != str(data["currentTurn"])):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == data["playerSecrets"][0]:
        if IsValidWord(data["map"], request.json['word'], request.json['worddata']) == False: return jsonify({"result":"-1", "error": "invalid word"}) 
        if IsRealWord(request.json['word'].lower()) == False:
            return jsonify({"result":"1", "message": "Not a real word!"})
        data["currentWord"] = request.json['word']
        data["currentWordData"] = request.json['worddata']
        data["currentTurn"] = 2
        return jsonify({"result":"0"})
    elif request.headers['player'] == "2" and request.headers['secret'] == data["playerSecrets"][1]:
        if IsValidWord(data["map"], request.json['word'], request.json['worddata']) == False: return jsonify({"result":"-1", "error": "invalid word"}) 
        if IsRealWord(request.json['word'].lower()) == False:
            return jsonify({"result":"1", "message": "Not a real word!"})
        data["currentWord"] = request.json['word']
        data["currentWordData"] = request.json['worddata']
        data["currentTurn"] = 1
        return jsonify({"result":"0"})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

@app.route('/api/getnewword', methods=['GET'])
def getnewword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    data["lastActivity"] = time.time()
    if (request.headers['player'] == str(data["currentTurn"])):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == data["playerSecrets"][0]:
        while data["currentWord"] == "":
            if request.headers['gameid'] not in allData:
                return jsonify({"result":"-1", "error": "Game closed"})
            time.sleep(0.1)
        word = data["currentWord"]
        data["currentWord"] = ""
        return jsonify({"result":"0", "word": word, "data":data["currentWordData"]})
    elif request.headers['player'] == "2" and request.headers['secret'] == data["playerSecrets"][1]:
        while data["currentWord"] == "":
            if request.headers['gameid'] not in allData:
                return jsonify({"result":"-1", "error": "Game closed"})
            time.sleep(0.1)
        word = data["currentWord"]
        data["currentWord"] = ""
        return jsonify({"result":"0", "word": word, "data":data["currentWordData"]})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

    
@app.route('/api/quit', methods=['GET'])
def quit():
    game = request.args.get('id')
    if game not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    allData.pop(game)
    print("Game deleted: " + game + "\nGames currently: " + str(len(allData)))
    return jsonify({"result":"0"})

@app.route('/api/admin/getallgames', methods=['GET'])
def getallgames():
    if request.headers['admin'] == ADMIN_PASSWORD:
        return jsonify({"result":"0", "games":allData})
    else:
        return jsonify({"result":"-1", "error":"unauthorized"})

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://www.wordbattle.tk'
    response.headers["Access-Control-Allow-Headers"] = '*'
    return response

def run():
    print("SERVER STARTED")
    serve(app, host="0.0.0.0", port=8080, threads=MAX_GAMES + MAX_WAITING_SLOTS + 1)

run()