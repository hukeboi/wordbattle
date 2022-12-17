from flask import Flask, request, jsonify
import time
import secrets
import random
#from flask_cors import CORS, cross_origin
from waitress import serve

app = Flask('')

#cors = CORS(app, resources={r"/api/*": {"origins": "*.wordbattle.tk"}})
#app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def main():
    return "under construction"

allLetters = "ABDEFGHIJKLMNOPRSTUVYÄÖ"
weights = (
    19, #A
    2,  #B
    2,  #D
    18, #E
    2,  #F
    4,  #G
    17,  #H
    20,  #I
    19,  #J
    19,  #K
    18,  #L
    19,  #M
    19,  #N
    19,  #O
    17,  #P
    18,  #R
    19,  #S
    19,  #T
    19,  #U
    14,  #V
    3,  #Y
    12,  #Ä
    10,  #Ö

)
def returnNewGrid():
    new = {}
    for row in range(1, 14, 1):
        columnVal = {}
        for column in range(1, 11, 1):
            columnVal[str(column) + "col"] = random.choices(allLetters, weights=weights)
        new[str(row) + "row"] = columnVal
    return new
def IsValidWord(map, word, wordData):
    if len(word) != len(wordData): 
        return False
    for i in range(0, len(wordData), 1):
        pos = map[str(wordData[i][0]) + "row"][str(wordData[i][1]) + "col"]
        if pos[0] != word[i]:
            return False
            
    return True



allData = {

}

maxGames = 5
adminPassword = "1234"

#playersInServer = 0
#playerSecrets = []
#map = {}
#currentTurn = 1
#currentWord = ""
#currentWordData = []

@app.route('/api/makenewgame', methods=['GET'])
def makenewgame():
    if len(allData) > maxGames: return jsonify({"result" : "-1", "error":"The server is currently at full capacity"})
    newGameId = str(secrets.token_hex(2))
    allData[newGameId] = {
        "playersInServer": 0,
        "playerSecrets": [],
        "map": {},
        "currentTurn": 1,
        "currentWord": "",
        "currentWordData": []
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
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    if request.headers['secret'] == data["playerSecrets"][0]:
        player = 1
    elif request.headers['secret'] == data["playerSecrets"][1]:
        player = 2
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})
    if data["map"] == {}:
        data["map"] = returnNewGrid()
    while data["playersInServer"] != 2:
        time.sleep(0.1)
    return jsonify({"result" : "0", "data": data["map"]})

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"result": "0"})

@app.route('/api/postword', methods=['POST'])
def postword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    if (request.headers['player'] != str(data["currentTurn"])):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == data["playerSecrets"][0]:
        data["currentWord"] = request.json['word']
        data["currentWordData"] = request.json['worddata']
        if IsValidWord(data["map"], data["currentWord"], data["currentWordData"]) == False: return jsonify({"result":"-1", "error": "invalid word"}) 
        data["currentTurn"] = 2
        return jsonify({"result":"0"})
    elif request.headers['player'] == "2" and request.headers['secret'] == data["playerSecrets"][1]:
        data["currentWord"] = request.json['word']
        data["currentWordData"] = request.json['worddata']
        if IsValidWord(data["map"], data["currentWord"], data["currentWordData"]) == False: return jsonify({"result":"-1", "error": "invalid word"}) 
        data["currentTurn"] = 1
        return jsonify({"result":"0"})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

@app.route('/api/getnewword', methods=['GET'])
def getnewword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
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
    if request.headers['adminkey'] == adminPassword:
        return jsonify({"result":"0", "games":allData})
    else:
        return jsonify({"result":"0", "games":allData})

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://www.wordbattle.tk'
    response.headers["Access-Control-Allow-Headers"] = '*'
    return response

def run():
    print("SERVER STARTED")
    serve(app, host="0.0.0.0", port=8080, threads=maxGames)

run()