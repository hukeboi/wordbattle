from flask import Flask, request, jsonify
from threading import Thread
import time
import secrets
import random
from flask_cors import CORS, cross_origin

app = Flask('')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def main():
    return "under construction"

allLetters = "ABDEFGHIJKLMNOPRSTUVYÄÖ"
weights = (
    19, #A
    5,  #B
    5,  #D
    18, #E
    6,  #F
    8,  #G
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
    14,  #Ä
    14,  #Ö

)
def returnNewGrid():
    new = {}
    for row in range(1, 14, 1):
        columnVal = {}
        for column in range(1, 11, 1):
            columnVal[str(column) + "col"] = random.choices(allLetters, weights=weights)
        new[str(row) + "row"] = columnVal
    return new


allData = {

}

#playersInServer = 0
#playerSecrets = []
#map = {}
#currentTurn = 1
#playerHasVoted = [False, False] #index 0 indicates if player voted, index 1 indicates the value of the vote
#currentWord = ""
#currentWordData = []

@app.route('/api/makenewgame', methods=['GET'])
@cross_origin()
def makenewgame():
    newGameId = str(secrets.token_hex(2))
    allData[newGameId] = {
        "playersInServer": 0,
        "playerSecrets": [],
        "map": {},
        "currentTurn": 1,
        "playerHasVoted": [False, False],
        "currentWord": "",
        "currentWordData": []
    }
    #print("NEW GAME: " + newGameId)
    return jsonify({"result" : "0", "gameid":newGameId})

@app.route('/api/getserverstatus', methods=['GET'])
@cross_origin()
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
@cross_origin()
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
@cross_origin()
def ping():
    return jsonify({"result": "0"})

@app.route('/api/postword', methods=['POST'])
@cross_origin()
def postword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    if (request.headers['player'] != str(data["currentTurn"])):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == data["playerSecrets"][0]:
        data["currentWord"] = request.json['word']
        data["currentWordData"] = request.json['worddata']
        while data["playerHasVoted"][0] == False:
            time.sleep(0.1)
        data["playerHasVoted"][0] = False
        if data["currentTurn"] == 1: data["currentTurn"] = 2 
        else: data["currentTurn"] = 1
        return jsonify({"result":"0", "answer": data["playerHasVoted"][1]})
    elif request.headers['player'] == "2" and request.headers['secret'] == data["playerSecrets"][1]:
        data["currentWord"] = request.json['word']
        data["currentWordData"] = request.json['worddata']
        while data["playerHasVoted"][0] == False:
            time.sleep(0.1)
        data["playerHasVoted"][0] = False
        if data["currentTurn"] == 1: data["currentTurn"] = 2 
        else: data["currentTurn"] = 1
        return jsonify({"result":"0", "answer": data["playerHasVoted"][1]})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

@app.route('/api/getnewword', methods=['GET'])
@cross_origin()
def getnewword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    if (request.headers['player'] == str(data["currentTurn"])):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == data["playerSecrets"][0]:
        while data["currentWord"] == "":
            time.sleep(0.1)
        word = data["currentWord"]
        data["currentWord"] = ""
        return jsonify({"result":"0", "word": word, "data":data["currentWordData"]})
    elif request.headers['player'] == "2" and request.headers['secret'] == data["playerSecrets"][1]:
        while data["currentWord"] == "":
            time.sleep(0.1)
        word = data["currentWord"]
        data["currentWord"] = ""
        return jsonify({"result":"0", "word": word, "data":data["currentWordData"]})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})

@app.route('/api/approveword', methods=['POST'])
@cross_origin()
def approveword():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    data = allData[request.headers['gameid']]
    if (request.headers['player'] == str(data["currentTurn"])):
        return jsonify({"result":"-1", "error":"An internal error occured"})
    if request.headers['player'] == "1" and request.headers['secret'] == data["playerSecrets"][0]:
        if request.json['result'] == "true":
            data["playerHasVoted"][1] = True
        else:
            data["playerHasVoted"][1] = False
        data["playerHasVoted"][0] = True
        return jsonify({"result":"0"})
    elif request.headers['player'] == "2" and request.headers['secret'] == data["playerSecrets"][1]:
        if request.json['result'] == "true":
            data["playerHasVoted"][1] = True
        else:
            data["playerHasVoted"][1] = False
        data["playerHasVoted"][0] = True
        return jsonify({"result":"0"})
    else:
        return jsonify({"result" : "-1", "error":"Invalid player secret."})
    
@app.route('/api/quit', methods=['GET'])
@cross_origin()
def quit():
    if request.headers['gameid'] not in allData: return jsonify({"result" : "-1", "error":"Invalid game id."})
    allData.pop(request.headers['gameid'])
    return jsonify({"result":"0"})


def run():
    app.run(host="0.0.0.0", port=8080, threaded=True)


def keep_alive():
    server = Thread(target=run)
    server.start()


keep_alive()

print("SERVER STARTED")